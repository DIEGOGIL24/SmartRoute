import os
from pathlib import Path
from typing import List

import requests
from crewai.tools import tool
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv('API_KEY_PLACES')
radius = 11000


@tool
def search_places(categories: List[str], latitude: float, longitude: float):
    """
    Busca lugares turísticos cercanos basados en categorías específicas.

    Args:
        categories: Lista de categorías a buscar (ej: ["cafe", "park", "museum"])
        latitude: Latitud de la ubicación central
        longitude: Longitud de la ubicación central

    Returns:
        JSON string con lugares encontrados
    """
    url = 'https://places.googleapis.com/v1/places:searchNearby'

    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': API_KEY,
        'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.types,places.rating'
    }

    body = {
        'includedTypes': categories,
        'maxResultCount': 10,
        'locationRestriction': {
            'circle': {
                'center': {
                    'latitude': latitude,
                    'longitude': longitude
                },
                'radius': radius
            }
        }
    }

    print("🔍 Buscando lugares...")
    print(f"Tipos: {', '.join(categories)}")
    print(f"Ubicación: {latitude}, {longitude}")
    print(f"Radio: {radius}m\n")

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        data = response.json()

        if 'places' in data:
            places_found = []
            print(f"✅ Encontrados {len(data['places'])} lugares:\n")

            for i, place in enumerate(data['places'], 1):
                nombre = place['displayName']['text']
                direccion = place.get('formattedAddress', 'N/A')
                rating = place.get('rating', 'N/A')
                tipos = ', '.join(place.get('types', [])[:2])

                print(f"{i}. {nombre}")
                print(f"   📍 {direccion}")
                print(f"   ⭐ {rating}")
                print(f"   🏷️  {tipos}\n")

                places_found.append({
                    'name': nombre,
                    'address': direccion,
                    'rating': rating,
                    'types': place.get('types', [])
                })

            return places_found

        else:
            print("❌ No se encontraron lugares")
            return []
    else:
        print(f"❌ Error {response.status_code}")
        print(response.text)
        return []


if __name__ == "__main__":
    categories1 = ['restaurant', 'cafe']
    latitude1 = 6.2518
    longitude1 = -75.5636
    search_places.run(categories1, latitude1, longitude1)
