import json
import os
import re
from contextlib import contextmanager
from typing import Any, Dict, List

import pika
import psycopg2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from routes import router as frontend_router
from tourism_agent import tourism_agent
from weather_agent import weather_agent

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
app.include_router(frontend_router)

RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://user:pass@rabbitmq:5672/')
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/smartroute')


class MessageRequest(BaseModel):
    text: str


class MessageRequestForWeather(BaseModel):
    city: str
    time: str


class MessageRequestForTourism(BaseModel):
    interests: List[str]


class HealthResponse(BaseModel):
    status: str
    postgres: str
    rabbitmq: str


# Context managers para conexiones
@contextmanager
def get_rabbitmq_connection():
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    try:
        yield connection
    finally:
        connection.close()


@contextmanager
def get_postgres_connection():
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
        return "RabbitMQ OK - Conectado correctamente"
    except Exception as e:
        return f"RabbitMQ Error: {str(e)}"


def test_postgres() -> str:
    """Prueba la conexión con PostgreSQL"""
    try:
        with get_postgres_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            cursor.close()
        return f"PostgreSQL OK - Versión conectada"
    except Exception as e:
        return f"PostgreSQL Error: {str(e)}"


def send_message_to_rabbit(message: str, queue: str) -> str:
    """Envía un mensaje a la cola de RabbitMQ"""
    try:
        with get_rabbitmq_connection() as connection:
            channel = connection.channel()
            channel.queue_declare(queue=queue, durable=True)
            channel.basic_publish(
                exchange='',
                routing_key=queue,
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)
            )
        return f"Mensaje enviado a RabbitMQ: '{message}'"
    except Exception as e:
        return f"Error al enviar: {str(e)}"


def read_messages_from_rabbit(limit: int, queue: str) -> List[Dict[str, Any]]:
    """Lee mensajes de la cola de RabbitMQ"""
    try:
        with get_rabbitmq_connection() as connection:
            channel = connection.channel()
            channel.queue_declare(queue=queue, durable=True)

            print(queue)
            messages = []
            for _ in range(limit):
                method, properties, body = channel.basic_get(
                    queue=queue,
                    auto_ack=True
                )
                print(body)
                if body:
                    message_string = body.decode()
                    print(message_string)
                    print("1")
                    message_dict = json.loads(message_string)
                    print("2")
                    print(message_dict)
                    messages.append(message_dict)
                else:
                    break

            print("Todo bien")
            return messages
    except Exception as e:
        print(f"Error al leer: {str(e)}")
        return []


def get_queue_info() -> dict:
    """Obtiene información de las colas en RabbitMQ"""
    try:
        with get_rabbitmq_connection() as connection:
            channel = connection.channel()

            queue_travel = channel.queue_declare(queue='travel_messages', durable=True, passive=True)
            queue_weather = channel.queue_declare(queue='weather', durable=True, passive=True)

            return {
                "travel_messages": queue_travel.method.message_count,
                "weather_messages": queue_weather.method.message_count
            }
    except Exception as e:
        return {"error": str(e)}


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


@app.get("/viewMessages")
async def get_messages():
    """Lee los últimos mensajes de RabbitMQ"""
    result = read_messages_from_rabbit(20, "travel_messages")
    queue_info = get_queue_info()

    return {
        "result": result,
        "queue_info": queue_info
    }


@app.get("/viewWeatherMessages")
async def get_messages_weather():
    result = read_messages_from_rabbit(1, "weather")
    queue_info = get_queue_info()

    outs = []
    for message in result:
        city = message["city"]
        time = message["time"]
        try:
            days = int(time)
        except ValueError:
            match = re.search(r'\d+', time)
            if match:
                days = int(match.group())
            else:
                days = 5
        agent_result = weather_agent.run_weather_forecast(city, days)
        print("Voy a guardar")
        save_to_postgres(city, time, agent_result)
        print("Ya guarde")
        outs.append(agent_result)

    return {
        "result": outs,
        "queue_info": queue_info
    }


@app.get("/viewTourismMessages")
async def get_messages_tourism():
    result = read_messages_from_rabbit(1, "tourism")
    queue_info = get_queue_info()

    outs = []
    for message in result:
        interests = message["interests"]  # Ahora es un arreglo

        # Validar que interests sea una lista
        if not isinstance(interests, list):
            # Si viene como string, convertirlo a lista
            if isinstance(interests, str):
                interests = [interests]
            else:
                interests = []

        try:
            agent_result = tourism_agent.run_tourism_category_selector(
                user_interests=interests
            )
            print("Voy a guardar")
            print("Ya guardé")
            outs.append(agent_result)
        except Exception as e:
            print(f"Error procesando mensaje: {str(e)}")
            outs.append({
                "error": str(e),
                "interests": interests
            })

    return {
        "queue_info": queue_info,
        "results": outs,
        "total_processed": len(outs)
    }


def save_to_postgres(destination: str, time: str, out: str) -> None:
    try:
        with get_postgres_connection() as conn:
            cursor = conn.cursor()

            print("Guardando")
            cursor.execute("""
                           INSERT INTO prompts (user_id, city, time_str, response_text)
                           VALUES ('00000000-0000-0000-0000-000000000001',
                                   %s,
                                   %s,
                                   %s);
                           """, (destination, time, out))

            print("Guardado aaaaa")
            conn.commit()
            cursor.close()
    except Exception as e:
        print(f"Error guardando en PostgreSQL: {e}")


@app.post("/sendMessage")
async def send_message(message: MessageRequest):
    full_message_json = message.model_dump_json()
    result = send_message_to_rabbit(full_message_json, "travel_messages")
    queue_info = get_queue_info()

    return {
        "result": result,
        "queue_info": queue_info
    }


@app.post("/sendWeatherInfo")
async def send_message(message: MessageRequestForWeather):
    full_message_json = message.model_dump_json()
    result = send_message_to_rabbit(full_message_json, "weather")
    queue_info = get_queue_info()

    return {
        "result": result,
        "queue_info": queue_info
    }


@app.post("/sendTourismInfo")
async def send_message(message: MessageRequestForTourism):
    full_message_json = message.model_dump_json()
    result = send_message_to_rabbit(full_message_json, "tourism")
    queue_info = get_queue_info()

    return {
        "result": result,
        "queue_info": queue_info
    }


@app.get("/rabbitmq/queues")
async def get_queue_stats():
    """Obtiene estadísticas de las colas de RabbitMQ"""
    return {
        "queues": get_queue_info(),
        "rabbitmq_status": test_rabbitmq()
    }


if __name__ == "__main__":
    import uvicorn

    print("🔧 Starting Test & Diagnostics API...")
    print("📍 Mode: TESTING")
    print("📍 Docs: http://localhost:8080/docs")
    print("📍 Health: http://localhost:8080/health")
    print("📍 Frontend routes available at: /api/travel-recommendations")
    # result = agent.crew.kickoff(inputs={
    #     'destination': 'Tunja, Colombia',
    #     'time_range': 'los próximos 3 días'
    # })
    # print("Aca llegue")
    # print(result)
    uvicorn.run(app, host="0.0.0.0", port=8080)
