import json
import os
import re

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from api_services import test_postgres, test_rabbitmq, send_message_to_rabbit, read_messages_from_rabbit
from connections import get_postgres_connection
from models import MessageRequest, MessageRequestForWeather, MessageRequestForTourism, HealthResponse, MessageItinerary
from routes import router as frontend_router
from tourism_agent import tourism_agent
from weather_agent import weather_agent
from langchain import extract_text, generar_itinerario

app = FastAPI(
    title="SmartRoute",
    description="Generador de itinerarios basado en el clima y preferencias turísticas",
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


def validate_time_string(time_str: str) -> int:
    try:
        days = int(time_str)
        return days
    except ValueError:
        match = re.search(r'\d+', time_str)
        if match:
            return int(match.group())
        else:
            return 5


def extract_coordinates(agent_result):
    try:
        lat = float(agent_result["current"]["coordinates"]["lat"])
        lon = float(agent_result["current"]["coordinates"]["lon"])
        print(f"Coordenadas extraídas: lat={lat}, lon={lon}")
        return [lat, lon]
    except (KeyError, TypeError, ValueError) as e:
        print(f"Error extrayendo coordenadas: {e}")
        return [None, None]

@app.get("/getItineraryInfo", response_class=PlainTextResponse)
async def get_itinerary_info():
    final_result = []

    weather_messages = read_messages_from_rabbit(1, os.getenv('WEATHER_QUEUE'))

    agent_result = None
    weather_result = None
    from datetime import datetime
    tourism_result = None
    city = None
    time = None

    for message in weather_messages:
        print(f"Mensaje? {message} \n")
        city = message["city"]
        time = message["time"]
        days = validate_time_string(time)
        print("Agente del clima ha empezado a las " + datetime.now().strftime("%H:%M:%S"))
        weather_result = weather_agent.run_weather_forecast(city, days)
        print("Agente del clima ha terminado a las " + datetime.now().strftime("%H:%M:%S"))
    lat, lon = extract_coordinates(weather_result)

    print("Resultado del agente del clima:\n\n")
    print(weather_result)
    final_result.append(weather_result)

    print("Voy a guardar")
    # save_to_postgres(city, time, agent_result)
    print("Ya guarde")

    tourism_messages = read_messages_from_rabbit(1, os.getenv('TOURISM_QUEUE'))

    for message in tourism_messages:
        interests = message["interests"]

        if not isinstance(interests, list):
            if isinstance(interests, str):
                interests = [interests]
            else:
                interests = []

        print("Agente de turismo ha empezado a las " + datetime.now().strftime("%H:%M:%S"))
        tourism_result = tourism_agent.run_tourism_category_selector(
            user_interests=interests,
            latitude=lat,
            longitude=lon,
            weather=final_result
        )

        print("Agente de turismo ha terminado a las " + datetime.now().strftime("%H:%M:%S"))
        print("Voy a guardar")
        print("Ya guardé")
        final_result.append(tourism_result)

        print("Resultado final de los agentes:\n\n")
        print(final_result)

    print("\n\n\n" + str(final_result) + "\n\n\n")

    print("No se que poner "+ "\n\n\n\n\n\n\n")

    json_string = json.dumps(final_result, ensure_ascii=False)
    out = extract_text(generar_itinerario(json_string))

    print("Aca va la salida")
    print(out)

    print(type(out))

    return out


@app.post("/sendItineraryInfo")
async def send_itinerary_info(message: MessageItinerary):
    print(f"Prueba {message.city}")
    print(f"{message.time}")
    print(f"{message.interests}")
    weather_message = {
        "city": message.city,
        "time": message.time
    }
    weather_result = send_message_to_rabbit(
        json.dumps(weather_message),
        os.getenv('WEATHER_QUEUE')
    )

    tourism_message = {
        "interests": message.interests
    }
    tourism_result = send_message_to_rabbit(
        json.dumps(tourism_message),
        os.getenv('TOURISM_QUEUE')
    )

    return {
        "weather_queue_result": weather_result,
        "tourism_queue_result": tourism_result,
        "status": "Messages sent successfully"
    }


##Endpooints de prueba

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
                user_interests=interests,
                latitude=5.5353,
                longitude=-73.3678
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
