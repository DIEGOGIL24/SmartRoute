import os
from crewai import Agent, Task, Crew, LLM
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
    goal="Analyze and provide detailed and accurate weather forecasts for {destination} for the specified {time_range}, delivering comprehensive meteorological information in a structured and easy-to-interpret JSON format.",
    backstory="You are a professional meteorologist with over 15 years of experience in climate analysis and weather forecasting. You have worked in national meteorological services and climate research stations, specializing in the interpretation of atmospheric data, predictive models, and weather trend analysis. You have a deep understanding of global climate patterns, extreme weather events, and the ability to translate complex technical data into useful and understandable information. Your experience includes the use of advanced technologies for climate monitoring and the creation of structured reports for various sectors such as agriculture, tourism, transportation, and urban planning.",
    llm=llm,
    verbose=True,
)

task1 = Task(
    description="""Obtain and analyze real-time weather forecasts for {destination} during the {time_range} period. 
                Use the weather forecast tool to collect up-to-date meteorological data and 
                generate a comprehensive analysis that includes current conditions, trends, and 
                recommendations based on the forecast.""",
    expected_output="""A complete report in JSON format containing:
                    - Current weather data (temperature, humidity, pressure, wind, precipitation)
                    - Extended forecast according to the specified {time_range} with the day, month and year
                    - Visibility and atmospheric conditions information""",
    agent=info_agent,
)

crew = Crew(
    agents=[info_agent],
    tasks=[task1],
    verbose=True
)

# result = crew.kickoff(inputs={
#     'destination': 'Tunja, Colombia',
#     'time_range': 'los próximos 3 días'
# })
#
# print(result)
