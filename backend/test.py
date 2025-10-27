import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pika
import psycopg2
from contextlib import contextmanager

app = FastAPI(
    title="SmartRoute Travel API",
    description="API para recomendaciones de viajes con RabbitMQ y PostgreSQL",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://user:pass@rabbitmq:5672/')
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/smartroute')

# Modelos Pydantic
class TravelRequest(BaseModel):
    prompt: str

class TravelRecommendation(BaseModel):
    destination: str
    weather: str | None
    activities: list[str]
    hotels: list[str]

class HealthResponse(BaseModel):
    status: str
    postgres: str
    rabbitmq: str

# Context managers para conexiones
@contextmanager
def get_rabbitmq_connection():
    """Context manager para conexiones RabbitMQ"""
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    try:
        yield connection
    finally:
        connection.close()

@contextmanager
def get_postgres_connection():
    """Context manager para conexiones PostgreSQL"""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

# Funciones de prueba
def test_rabbitmq() -> str:
    """Prueba la conexión con RabbitMQ"""
    try:
        with get_rabbitmq_connection() as connection:
            channel = connection.channel()
            channel.queue_declare(queue='test_queue', durable=True)
            channel.basic_publish(
                exchange='',
                routing_key='test_queue',
                body='Health check'
            )
        return "✅ RabbitMQ OK"
    except Exception as e:
        return f"❌ RabbitMQ Error: {str(e)}"

def test_postgres() -> str:
    """Prueba la conexión con PostgreSQL"""
    try:
        with get_postgres_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            cursor.close()
        return "✅ PostgreSQL OK"
    except Exception as e:
        return f"❌ PostgreSQL Error: {str(e)}"

def send_message_to_rabbit(message: str) -> str:
    """Envía un mensaje a la cola de RabbitMQ"""
    try:
        with get_rabbitmq_connection() as connection:
            channel = connection.channel()
            channel.queue_declare(queue='travel_messages', durable=True)
            channel.basic_publish(
                exchange='',
                routing_key='travel_messages',
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Mensaje persistente
                )
            )
        return f"✅ Mensaje enviado a RabbitMQ: {message}"
    except Exception as e:
        return f"❌ Error al enviar: {str(e)}"

def read_messages_from_rabbit(limit: int = 10) -> str:
    """Lee mensajes de la cola de RabbitMQ"""
    try:
        with get_rabbitmq_connection() as connection:
            channel = connection.channel()
            channel.queue_declare(queue='travel_messages', durable=True)
            
            messages = []
            for _ in range(limit):
                method, properties, body = channel.basic_get(
                    queue='travel_messages',
                    auto_ack=True
                )
                if body:
                    messages.append(body.decode())
                else:
                    break
            
            if messages:
                return f"✅ Mensajes leídos ({len(messages)}): " + ", ".join(messages)
            else:
                return "📭 No hay mensajes en la cola"
    except Exception as e:
        return f"❌ Error al leer: {str(e)}"

def save_to_postgres(destination: str, prompt: str) -> str:
    """Guarda una búsqueda en PostgreSQL"""
    try:
        with get_postgres_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO travel_searches (destination, prompt, created_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT DO NOTHING
            """, (destination, prompt))
            conn.commit()
            cursor.close()
        return "✅ Guardado en PostgreSQL"
    except Exception as e:
        # Si la tabla no existe, solo retornar info sin error
        return f"ℹ️ PostgreSQL: {str(e)[:50]}"

# Endpoints
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "SmartRoute Travel API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Verifica el estado de las conexiones"""
    postgres_status = test_postgres()
    rabbit_status = test_rabbitmq()
    
    status = "healthy" if "✅" in postgres_status and "✅" in rabbit_status else "degraded"
    
    return {
        "status": status,
        "postgres": postgres_status,
        "rabbitmq": rabbit_status
    }

@app.post("/api/travel-recommendations", response_model=TravelRecommendation)
async def get_recommendations(request: TravelRequest):
    """
    Obtiene recomendaciones de viaje basadas en el prompt del usuario.
    
    Comandos especiales:
    - 'test' o 'conexion': Prueba las conexiones
    - 'enviar': Envía un mensaje a RabbitMQ
    - 'leer': Lee mensajes de RabbitMQ
    """
    prompt = request.prompt.lower().strip()
    
    if not prompt:
        raise HTTPException(status_code=400, detail="El prompt no puede estar vacío")
    
    # Comandos de prueba
    if "test" in prompt or "conexion" in prompt or "conexión" in prompt:
        activities = [
            test_postgres(),
            test_rabbitmq()
        ]
        
        if "enviar" in prompt or "send" in prompt:
            send_result = send_message_to_rabbit(f"Test desde API: {prompt}")
            activities.append(send_result)
        
        if "leer" in prompt or "read" in prompt:
            read_result = read_messages_from_rabbit()
            activities.append(read_result)
        
        return TravelRecommendation(
            destination="🔧 Panel de Diagnóstico",
            weather=None,
            activities=activities,
            hotels=[]
        )
    
    # Recomendaciones de playa
    if any(word in prompt for word in ["playa", "mar", "caribe", "costa"]):
        destination = "Cartagena de Indias, Colombia"
        
        # Guardar en DB y enviar a RabbitMQ
        db_result = save_to_postgres(destination, prompt)
        rabbit_result = send_message_to_rabbit(f"Búsqueda: {prompt} -> {destination}")
        
        return TravelRecommendation(
            destination=destination,
            weather="☀️ Soleado y cálido, 28-32°C. Perfecto para el mar Caribe.",
            activities=[
                "🏰 Explorar la Ciudad Amurallada y calles coloniales",
                "🤿 Snorkel en las Islas del Rosario",
                "🍽️ Gastronomía caribeña en Getsemaní",
                "⛵ Paseo en velero al atardecer",
                f"📊 {db_result}",
                f"📨 {rabbit_result}"
            ],
            hotels=[
                "Hotel Boutique Casa del Arzobispado - Centro histórico colonial",
                "Hilton Cartagena - Resort frente al mar con spa",
                "Hotel Quadrifolio - Opción económica en Getsemaní"
            ]
        )
    
    # Recomendaciones de montaña
    if any(word in prompt for word in ["montaña", "frio", "frío", "nieve"]):
        destination = "Bariloche, Argentina"
        
        db_result = save_to_postgres(destination, prompt)
        rabbit_result = send_message_to_rabbit(f"Búsqueda: {prompt} -> {destination}")
        
        return TravelRecommendation(
            destination=destination,
            weather="❄️ Fresco, 5-15°C. Ideal para montaña y lagos.",
            activities=[
                "🏔️ Circuito Chico y vistas del lago Nahuel Huapi",
                "🎿 Esquí en Cerro Catedral",
                "🍫 Tour de chocolaterías artesanales",
                "🚡 Teleférico al Cerro Otto",
                f"📊 {db_result}",
                f"📨 {rabbit_result}"
            ],
            hotels=[
                "Llao Llao Hotel & Resort - Lujo con vistas al lago",
                "Design Suites Bariloche - Moderno y confortable",
                "Selina Bariloche - Para viajeros jóvenes"
            ]
        )
    
    # Respuesta por defecto - Lisboa
    destination = "Lisboa, Portugal"
    db_result = save_to_postgres(destination, prompt)
    rabbit_result = send_message_to_rabbit(f"Búsqueda: {prompt} -> {destination}")
    
    return TravelRecommendation(
        destination=destination,
        weather="🌤️ Clima suave, 22-26°C. Perfecto para caminar.",
        activities=[
            "🚋 Recorrer Alfama en tranvía amarillo",
            "🥐 Pasteles de Belém originales",
            "🏰 Castillo de São Jorge con vistas panorámicas",
            "🎵 Fado en vivo en Bairro Alto",
            f"📊 {db_result}",
            f"📨 {rabbit_result}"
        ],
        hotels=[
            "Memmo Alfama Hotel - Boutique con terraza panorámica",
            "Pestana Palace Lisboa - Palacio del siglo XIX",
            "The Independente Hostel - Diseño moderno y céntrico"
        ]
    )

@app.get("/api/messages")
async def get_messages():
    """Lee los últimos mensajes de RabbitMQ"""
    result = read_messages_from_rabbit(limit=20)
    return {"result": result}

@app.post("/api/messages")
async def send_message(message: dict):
    """Envía un mensaje a RabbitMQ"""
    if "text" not in message:
        raise HTTPException(status_code=400, detail="Se requiere el campo 'text'")
    
    result = send_message_to_rabbit(message["text"])
    return {"result": result}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting SmartRoute API...")
    print("📍 Internal: http://0.0.0.0:8080")
    print("📍 Via Traefik: http://api.localhost")
    print("📍 Docs: http://api.localhost/docs")
    print("📍 Health: http://api.localhost/health")
    uvicorn.run(app, host="0.0.0.0", port=8080)