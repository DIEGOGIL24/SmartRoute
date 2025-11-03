import os
from crewai import Agent, Task, Crew, LLM
from .weather_api import get_weather, get_forecast_weather
from .json_structure import WeatherReport
from dotenv import load_dotenv

# load_dotenv()
#
# os.environ["OPEN_WEATHER_APP"] = os.getenv("OPEN_WEATHER_APP")

llm = LLM(
    model="ollama/qwen3",
    base_url="http://ollama:11434"
)

info_agent = Agent(
    role="Weather Forecast Expert",
    goal="""Analyze and provide detailed and accurate weather forecasts for {destination} for the specified {time_range},
         delivering comprehensive meteorological information in a structured and easy-to-interpret JSON format.""",
    backstory="""You are a meteorologist who ALWAYS uses weather APIs to get accurate, real-time data. 
       You NEVER make up or invent weather data. You MUST use the get_weather and get_forecast_weather tools 
       to retrieve actual weather information from OpenWeatherMap API.""",
    llm=llm,
    tools=[get_weather, get_forecast_weather],
    verbose=True,
)

task1 = Task(
    description="""Retrieve real weather data using the provided tools and add your expert analysis.

    REQUIRED ACTIONS:
    1. Call get_weather(city="{destination}") to get current conditions
    2. Call get_forecast_weather(place="{destination}", days={time_range}) to get forecast
    3. ANALYZE the API data and ADD a "summary" field to EACH forecast item with your recommendation

    CRITICAL INSTRUCTIONS FOR SUMMARIES:
    - For EACH item in the forecasts array, ADD a new field called "summary"
    - The summary must be ONE sentence with a practical recommendation
    - Base your summary on the specific weather data of that forecast (temperature, rain, wind, etc.)
    - Examples: 
      * "Ideal day for outdoor activities with pleasant temperatures and clear skies."
      * "Bring an umbrella as rain is expected throughout the day."
      * "Strong winds expected, not recommended for outdoor events."

    IMPORTANT: 
    - You MUST use both tools to get real API data
    - Do NOT invent weather numbers (temp, humidity, etc.)
    - DO add your expert summary/recommendation to each forecast
    - The dates in the forecast come from OpenWeatherMap API""",

    expected_output="""JSON with two sections:
    {
        "current": <result from get_weather tool>,
        "forecast": {
            "city": "city name",
            "forecasts": [
                {
                    "date": "from API",
                    "description": "from API",
                    "temperature": {"min_temp": X, "max_temp": Y},
                    "wind_speed": "from API",
                    "humidity": "from API",
                    "clouds": "from API",
                    "summary": "YOUR ONE-SENTENCE RECOMMENDATION HERE"
                },
                ... more forecasts with summary in each one
            ]
        }
    }

    Remember: Add "summary" field to EVERY forecast item.""",
    agent=info_agent,
    output_pydantic=WeatherReport
)

crew = Crew(
    agents=[info_agent],
    tasks=[task1],
    verbose=True
)


def run_weather_forecast(destination, time_range):
    weather_result = crew.kickoff(inputs={
        'destination': destination,
        'time_range': time_range
    })

    if weather_result.pydantic:
        return weather_result.pydantic.model_dump()

    return weather_result.raw
