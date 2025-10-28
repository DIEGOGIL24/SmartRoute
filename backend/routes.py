import os
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from pydantic import BaseModel
import pika
import json
import psycopg2
from contextlib import contextmanager

# Crear el router
router = APIRouter()

RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://user:pass@rabbitmq:15672/')
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/smartroute')

# Modelos Pydantic
class TravelRequest(BaseModel):
    prompt: str

class TravelRecommendation(BaseModel):
    destination: str
    weather: str | None
    activities: list[str]
    hotels: list[str]

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

# Funciones auxiliares
def send_message_to_rabbit(message: str) -> None:
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
    except Exception as e:
        print(f"Error enviando a RabbitMQ: {e}")

def save_to_postgres(destination: str, weather: str, activities: list, hotels: list, user_id: str) -> None:
    """Guarda un itinerario en la tabla itineraries de PostgreSQL"""
    try:
        with get_postgres_connection() as conn:
            cursor = conn.cursor()

            # Fechas por defecto (7 días desde hoy)
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=7)

            # Convertimos las actividades y hoteles en un JSON para itinerary_details
            itinerary_details = json.dumps({
                "activities": activities,
                "hotels": hotels
            }, ensure_ascii=False)

            cursor.execute("""
                INSERT INTO itineraries (user_id, destination, start_date, end_date, weather_summary, itinerary_details, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (user_id, destination, start_date, end_date, weather, itinerary_details))

            conn.commit()
            cursor.close()
    except Exception as e:
        print(f"Error guardando en PostgreSQL: {e}")


# Endpoints del Frontend
@router.post("/api/travel-recommendations", response_model=TravelRecommendation)
async def get_recommendations(request: TravelRequest):
    """
    Obtiene recomendaciones de viaje basadas en el prompt del usuario.
    
    Este endpoint es para el frontend de la aplicación.
    """
    prompt = request.prompt.lower().strip()
    
    if not prompt:
        raise HTTPException(status_code=400, detail="El prompt no puede estar vacío")
    
    user_id = "43813dff-6c37-4277-94f0-90cb98f50609"
    
    # Recomendaciones de montaña
    if any(word in prompt for word in ["montaña", "montana", "frio", "frío", "nieve", "mountain", "ski", "esqui"]):
        destination_data = {
            "destination": "Bariloche, Argentina",
            "weather": "❄️ Fresco, 5-15°C. Ideal para montaña y lagos.",
            "activities": [
                "🏔️ Circuito Chico y vistas del lago Nahuel Huapi",
                "🎿 Esquí en Cerro Catedral",
                "🍫 Tour de chocolaterías artesanales",
                "🚡 Teleférico al Cerro Otto"
            ],
            "hotels": [
                "Llao Llao Hotel & Resort - Lujo con vistas al lago",
                "Design Suites Bariloche - Moderno y confortable",
                "Selina Bariloche - Para viajeros jóvenes"
            ]
        }
    # Recomendaciones de playa
    elif any(word in prompt for word in ["playa", "beach", "mar", "costa", "caribe", "sol"]):
        destination_data = {
            "destination": "Cartagena, Colombia",
            "weather": "☀️ Cálido y soleado, 28-32°C",
            "activities": [
                "🏖️ Relajación en Playa Blanca",
                "🏰 Tour por el centro histórico amurallado",
                "🍽️ Gastronomía caribeña en Getsemaní",
                "🚤 Excursión a Islas del Rosario"
            ],
            "hotels": [
                "Hotel Sofitel Legend Santa Clara - Histórico y lujoso",
                "Casa San Agustín - Boutique colonial",
                "Selina Cartagena - Moderno y social"
            ]
        }
    # Destino por defecto (ciudad/cultura)
    else:
        destination_data = {
            "destination": "Buenos Aires, Argentina",
            "weather": "🌤️ Templado, 18-25°C. Clima agradable todo el año.",
            "activities": [
                "💃 Show de tango en el barrio de San Telmo",
                "🏛️ Visita a La Boca y Caminito",
                "🥩 Cena en una parrilla tradicional",
                "🎭 Teatro Colón y Avenida 9 de Julio"
            ],
            "hotels": [
                "Alvear Palace Hotel - Elegancia clásica",
                "Hotel Madero - Diseño moderno en Puerto Madero",
                "Esplendor by Wyndham - Boutique en Palermo"
            ]
        }

    # Enviar mensaje a RabbitMQ
    send_message_to_rabbit(f"Búsqueda: {prompt} -> {destination_data['destination']}")

    # Guardar en PostgreSQL
    save_to_postgres(
        destination=destination_data["destination"],
        weather=destination_data["weather"],
        activities=destination_data["activities"],
        hotels=destination_data["hotels"],
        user_id=user_id
    )

    # ← ESTO ES LO CRÍTICO: SIEMPRE RETORNAR UN VALOR
    return TravelRecommendation(**destination_data)