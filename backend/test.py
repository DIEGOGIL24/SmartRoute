import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pika
import psycopg2
from contextlib import contextmanager
from routes import router as frontend_router

app = FastAPI(
    title="SmartRoute Test & Diagnostics API",
    description="API para testing de conexiones con RabbitMQ y PostgreSQL",
    version="1.0.0-test"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas del frontend (opcional, para cuando se necesite)
app.include_router(frontend_router)

RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://user:pass@rabbitmq:15672/')
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/smartroute')

# Modelos Pydantic
class MessageRequest(BaseModel):
    text: str

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
                body='Health check test'
            )
        return "✅ RabbitMQ OK - Conectado correctamente"
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
        return f"✅ PostgreSQL OK - Versión conectada"
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
                properties=pika.BasicProperties(delivery_mode=2)
            )
        return f"✅ Mensaje enviado a RabbitMQ: '{message}'"
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

def get_queue_info() -> dict:
    """Obtiene información de las colas en RabbitMQ"""
    try:
        with get_rabbitmq_connection() as connection:
            channel = connection.channel()
            
            # Declarar colas para obtener info
            queue_test = channel.queue_declare(queue='test_queue', durable=True, passive=True)
            queue_travel = channel.queue_declare(queue='travel_messages', durable=True, passive=True)
            
            return {
                "test_queue": queue_test.method.message_count,
                "travel_messages": queue_travel.method.message_count
            }
    except Exception as e:
        return {"error": str(e)}

def test_postgres_tables() -> list[str]:
    """Lista las tablas en PostgreSQL"""
    try:
        with get_postgres_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return tables if tables else ["(No hay tablas creadas)"]
    except Exception as e:
        return [f"Error: {str(e)}"]

# Endpoints de Testing
@app.get("/")
async def root():
    """Endpoint raíz con información de testing"""
    return {
        "message": "SmartRoute Test & Diagnostics API",
        "version": "1.0.0-test",
        "mode": "testing",
        "docs": "/docs",
        "endpoints": {
            "testing": {
                "health": "/health",
                "detailed_health": "/health/detailed",
                "send_message": "/api/messages (POST)",
                "read_messages": "/api/messages (GET)",
                "clear_messages": "/api/messages/clear (DELETE)",
                "queue_info": "/rabbitmq/queues",
                "tables": "/postgres/tables",
                "init_schema": "/postgres/init-schema (POST)"
            },
            "frontend": {
                "travel_recommendations": "/api/travel-recommendations (POST)"
            }
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check básico"""
    postgres_status = test_postgres()
    rabbit_status = test_rabbitmq()
    
    status = "healthy" if "✅" in postgres_status and "✅" in rabbit_status else "degraded"
    
    return {
        "status": status,
        "postgres": postgres_status,
        "rabbitmq": rabbit_status
    }

@app.get("/health/detailed")
async def detailed_health():
    """Health check detallado con información de colas y tablas"""
    postgres_status = test_postgres()
    rabbit_status = test_rabbitmq()
    queue_info = get_queue_info()
    tables = test_postgres_tables()
    
    return {
        "status": "healthy" if "✅" in postgres_status and "✅" in rabbit_status else "degraded",
        "services": {
            "postgres": postgres_status,
            "rabbitmq": rabbit_status
        },
        "rabbitmq_queues": queue_info,
        "postgres_tables": tables
    }

@app.get("/api/messages")
async def get_messages():
    """Lee los últimos mensajes de RabbitMQ"""
    result = read_messages_from_rabbit(limit=20)
    queue_info = get_queue_info()
    
    return {
        "result": result,
        "queue_info": queue_info
    }

@app.post("/api/messages")
async def send_message(message: MessageRequest):
    """Envía un mensaje a RabbitMQ"""
    result = send_message_to_rabbit(message.text)
    queue_info = get_queue_info()
    
    return {
        "result": result,
        "queue_info": queue_info
    }

@app.delete("/api/messages/clear")
async def clear_messages():
    """Limpia todos los mensajes de la cola"""
    try:
        count = 0
        with get_rabbitmq_connection() as connection:
            channel = connection.channel()
            while True:
                method, properties, body = channel.basic_get(
                    queue='travel_messages',
                    auto_ack=True
                )
                if not body:
                    break
                count += 1
        
        return {"result": f"✅ Se eliminaron {count} mensajes de la cola"}
    except Exception as e:
        return {"result": f"❌ Error: {str(e)}"}

@app.get("/rabbitmq/queues")
async def get_queue_stats():
    """Obtiene estadísticas de las colas de RabbitMQ"""
    return {
        "queues": get_queue_info(),
        "rabbitmq_status": test_rabbitmq()
    }

@app.get("/postgres/tables")
async def get_tables():
    """Lista las tablas de PostgreSQL"""
    tables = test_postgres_tables()
    return {
        "tables": tables,
        "count": len(tables),
        "postgres_status": test_postgres()
    }

@app.post("/postgres/init-schema")
async def init_schema():
    """Inicializa el schema de la base de datos"""
    try:
        with get_postgres_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS travel_searches (
                    id SERIAL PRIMARY KEY,
                    destination VARCHAR(255) NOT NULL,
                    prompt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            conn.commit()
            cursor.close()
        
        tables = test_postgres_tables()
        return {
            "result": "✅ Tabla 'travel_searches' creada exitosamente",
            "tables": tables
        }
    except Exception as e:
        return {"result": f"❌ Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    print("🔧 Starting Test & Diagnostics API...")
    print("📍 Mode: TESTING")
    print("📍 Docs: http://localhost:8080/docs")
    print("📍 Health: http://localhost:8080/health")
    print("📍 Frontend routes available at: /api/travel-recommendations")
    uvicorn.run(app, host="0.0.0.0", port=8080)