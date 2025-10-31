import re

import requests
from crewai.tools import tool


@tool
def get_forecast_weather(place: str, days: int):
    """
    MANDATORY TOOL: Get REAL weather forecast from OpenWeatherMap API.

    This tool makes an actual API call to get future weather predictions.
    DO NOT invent forecast data. ALWAYS use this tool.

    Args:
        place: City name (e.g., "Tunja, CO", "Bogotá")
        days: Number of days to forecast (1-5, API provides data every 3 hours)

    Returns:
        dict: Real forecast data from API with list of predictions including:
            - date (dt_txt): actual date and time from API
            - description: weather description
            - temperature: min and max temperatures
            - wind_speed: wind speed

    Example usage:
        get_forecast_weather(place="Tunja, CO", days=3)
    """

    parameters = {
        "q": place,
        "appid": "b37abef24c08690c10c25d126959eb4f",
        "units": "metric",
        "lang": "es"
    }

    try:
        response = requests.get("https://api.openweathermap.org/data/2.5/forecast", params=parameters)
        response.raise_for_status()

        data = response.json()

        out_data = {
            "forecasts": []
        }

        for item in data['list'][:days * 8]:
            forecast = {
                "date": item["dt_txt"],
                "description": item["weather"][0]["description"],
                "temperature": {
                    "min_temp": item["main"]["temp_min"],
                    "max_temp": item["main"]["temp_max"],
                },
                "wind_speed": item["wind"]["speed"]
            }

            out_data["forecasts"].append(forecast)

        return out_data

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener datos: {e}")
        return None


@tool
def get_weather(city: str):
    """
    MANDATORY TOOL: Get REAL current weather data from OpenWeatherMap API.

    This tool makes an actual API call to get live weather data.
    DO NOT invent or make up weather data. ALWAYS use this tool.

    Args:
        city: Name of the city (e.g., "Tunja, CO", "Bogotá")

    Returns:
        dict: Real weather data from API including:
            - name: city name
            - weather: temperature, status, description, humidity, wind_speed, rain, clouds

    Example usage:
        get_weather(city="Tunja, CO")
    """

    parameters = {
        "q": city,
        "appid": "b37abef24c08690c10c25d126959eb4f",
        "units": "metric",
        "lang": "es"
    }

    try:
        response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=parameters)
        response.raise_for_status()

        data = response.json()

        out_data = {
            "name": data["name"],
            "weather": {
                "temperature" : data["main"]["temp"],
                "status": data["weather"][0]["main"],
                "description" : data["weather"][0]["description"],
                "humidity" : data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "rain" : data.get("rain", {}).get("1h", 0),
                "clouds" : data["clouds"]["all"],
            }
        }

        return out_data

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener datos: {e}")
        return None


if __name__ == '__main__':
    city = "Yopal, CO"
    print("Clima actual")
    print(get_weather.run(city=city))
    print("Pronostico")
    print(get_forecast_weather.run(place=city, days=3))
