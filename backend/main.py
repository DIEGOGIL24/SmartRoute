import re
import os

from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_services import test_postgres, test_rabbitmq, send_message_to_rabbit, read_messages_from_rabbit
from connections import get_postgres_connection
from models import MessageRequest, MessageRequestForWeather, MessageRequestForTourism, HealthResponse
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


@app.get("/health", response_model=HealthResponse)
async def health_check():
    postgres_status = test_postgres()
    rabbit_status = test_rabbitmq()

    status = "healthy" if "Todo bien" in postgres_status and "Todo bien" in rabbit_status else "degraded"

    return {
        "status": status,
        "postgres": postgres_status,
        "rabbitmq": rabbit_status
    }


@app.get("/viewMessages")
async def get_messages():
    result = read_messages_from_rabbit(20, "travel_messages")

    return {
        "result": result
    }


@app.get("/viewWeatherMessages")
async def get_messages_weather():
    result = read_messages_from_rabbit(1, os.getenv('WEATHER_QUEUE'))

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
        "result": outs
    }


@app.get("/viewTourismMessages")
async def get_messages_tourism():
    result = read_messages_from_rabbit(1, os.getenv('TOURISM_QUEUE'))

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

    return {
        "result": result
    }


@app.post("/sendWeatherInfo")
async def send_message(message: MessageRequestForWeather):
    full_message_json = message.model_dump_json()
    result = send_message_to_rabbit(full_message_json, os.getenv('WEATHER_QUEUE'))

    return {
        "result": result
    }


@app.post("/sendTourismInfo")
async def send_message(message: MessageRequestForTourism):
    full_message_json = message.model_dump_json()
    result = send_message_to_rabbit(full_message_json, os.getenv('TOURISM_QUEUE'))

    return {
        "result": result
    }


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080)
