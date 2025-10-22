import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pika
import psycopg2

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://user:pass@rabbitmq:5672/')
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/smartroute')

class TravelRequest(BaseModel):
    prompt: str

class TravelRecommendation(BaseModel):
    destination: str
    weather: str | None
    activities: list[str]
    hotels: list[str]

def test_rabbitmq():
    """Prueba básica de RabbitMQ"""
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='test')
        channel.basic_publish(exchange='', routing_key='test', body='Hello')
        connection.close()
        return "✅ RabbitMQ OK"
    except Exception as e:
        return f"❌ RabbitMQ Error: {str(e)}"

def test_postgres():
    """Prueba básica de PostgreSQL"""
    try:
        db_url = DATABASE_URL.replace('postgresql+psycopg2://', 'postgresql://')
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return "✅ PostgreSQL OK"
    except Exception as e:
        return f"❌ PostgreSQL Error: {str(e)}"

def send_message_to_rabbit(message):
    """Envía un mensaje a RabbitMQ"""
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='messages')
        channel.basic_publish(exchange='', routing_key='messages', body=message)
        connection.close()
        return f"✅ Mensaje enviado: {message}"
    except Exception as e:
        return f"❌ Error al enviar: {str(e)}"

def read_messages_from_rabbit():
    """Lee mensajes de RabbitMQ"""
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='messages')
        
        messages = []
        for i in range(10):
            method, properties, body = channel.basic_get(queue='messages', auto_ack=True)
            if body:
                messages.append(body.decode())
            else:
                break
        
        connection.close()
        
        if messages:
            return "✅ Mensajes: " + ", ".join(messages)
        else:
            return "📭 No hay mensajes en la cola"
    except Exception as e:
        return f"❌ Error al leer: {str(e)}"

@app.post("/api/travel-recommendations")
async def get_recommendations(request: TravelRequest) -> TravelRecommendation:
    prompt = request.prompt.lower()
    
    # Si el prompt contiene "test" o "conexion", ejecutar pruebas
    if "test" in prompt or "conexion" in prompt or "conexión" in prompt:
        postgres_status = test_postgres()
        rabbit_status = test_rabbitmq()
        
        activities = [postgres_status, rabbit_status]
        
        # Agregar pruebas adicionales según el prompt
        if "enviar" in prompt or "send" in prompt:
            send_result = send_message_to_rabbit("Prueba desde frontend")
            activities.append(send_result)
        
        if "leer" in prompt or "read" in prompt:
            read_result = read_messages_from_rabbit()
            activities.append(read_result)
        
        return TravelRecommendation(
            destination="Tests de Conexión",
            weather=None,
            activities=activities,
            hotels=[]
        )
    
    # Recomendaciones normales de viajes
    if "playa" in prompt or "mar" in prompt:
        return TravelRecommendation(
            destination="Cartagena de Indias, Colombia",
            weather="Soleado y cálido, 28-32°C. Perfecto para disfrutar del mar Caribe.",
            activities=[
                "Explorar la Ciudad Amurallada y sus calles coloniales",
                "Snorkel en las Islas del Rosario",
                "Disfrutar de la gastronomía caribeña en Getsemaní",
                "Paseo en velero al atardecer"
            ],
            hotels=[
                "Hotel Boutique Casa del Arzobispado - Centro histórico con encanto colonial",
                "Hilton Cartagena - Resort frente al mar con spa",
                "Hotel Quadrifolio - Opción económica en el corazón de Getsemaní"
            ]
        )
    
    # Respuesta por defecto
    return TravelRecommendation(
        destination="Lisboa, Portugal",
        weather="Clima suave y soleado, 22-26°C. Perfecto para explorar la ciudad a pie.",
        activities=[
            "Recorrer el barrio de Alfama en tranvía amarillo",
            "Degustar pasteles de Belém originales",
            "Mirador de São Jorge con vistas panorámicas",
            "Vida nocturna en Bairro Alto con música fado en vivo"
        ],
        hotels=[
            "Memmo Alfama Hotel - Boutique con terraza panorámica",
            "Pestana Palace Lisboa - Palacio del siglo XIX convertido en hotel",
            "The Independente Hostel & Suites - Diseño moderno con excelente ubicación"
        ]
    )

@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    postgres = test_postgres()
    rabbit = test_rabbitmq()
    
    return {
        "status": "running",
        "postgres": postgres,
        "rabbitmq": rabbit
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FastAPI server on port 8000...")
    print("📍 Visit: http://localhost:8000/health")
    print("📍 API docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8080)