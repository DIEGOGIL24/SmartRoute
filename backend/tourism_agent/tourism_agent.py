import os
from pathlib import Path

from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv
from typing import Any

from .places_api import search_places
from .tourism_json import ReportInterests, PlacesReport, TourismAgentResponse
from .tourism_tools import read_categories_file

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

llm = LLM(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_key=os.getenv("AZURE_API_KEY"),
    base_url=os.getenv("AZURE_ENDPOINT"),
    api_version="2024-12-01-preview"
)

tourism_agent = Agent(
    role="Experto en Turismo",
    goal="Analizar intereses del usuario y encontrar lugares turísticos relevantes cercanos",
    backstory="""Eres un agente especializado en turismo que:
    1. Lee catálogos de categorías turísticas
    2. Analiza intereses de usuarios y encuentra las mejores coincidencias
    3. Busca lugares específicos que se alineen con esas preferencias

    Trabajas de forma metódica y precisa, usando las herramientas disponibles.""",
    llm=llm,
    tools=[read_categories_file, search_places],
    verbose=True
)

task_read_categories = Task(
    description="""Lee el archivo de categorías usando la herramienta 'read_categories_file'.

    Devuelve todo el contenido del archivo tal como aparece.""",
    expected_output="Contenido completo del archivo de categorías",
    agent=tourism_agent,
    tools=[read_categories_file]
)

task_select_categories = Task(
    description="""Analiza los intereses del usuario: {user_interests}

    Revisa las categorías disponibles del contexto anterior.
    Identifica las categorías más relevantes para los intereses mencionados.

    Utiliza los nombres exactos de las categorías que aparecen en el archivo.""",
    expected_output="JSON con campo 'selected_categories' conteniendo lista de categorías relevantes",
    agent=tourism_agent,
    output_pydantic=ReportInterests,
    context=[task_read_categories]
)

task_search_places = Task(
    description="""Utiliza las categorías seleccionadas en el paso anterior.

    Llama a la herramienta 'search_places' con:
    - categories: las categorías de la tarea anterior
    - latitude: {latitude}
    - longitude: {longitude}

    Realiza una única búsqueda con estos parámetros.""",
    expected_output="Lista JSON de lugares encontrados",
    agent=tourism_agent,
    context=[task_select_categories],
    output_pydantic=PlacesReport,
    tools=[search_places]
)

select_final_places = Task(
    description="""Utiliza los lugares seleccionados en el paso anterior.
    Analiza los lugares encontrados y selecciona SOLO los más acordes segun el clima
    y pronosticos futuros usando {weather}. (maximo 5 lugares).""",
    expected_output="""Lista JSON de lugares finales recomendados con una nota al final pero dentro del JSON del todo del porque 
                    fueron seleccionados esos lugares con base al clima.""",
    agent=tourism_agent,
    context=[task_search_places],
    output_pydantic=TourismAgentResponse,
    tools=[]
)

crew = Crew(
    agents=[tourism_agent],
    tasks=[task_read_categories, task_select_categories, task_search_places, select_final_places],
    verbose=True
)


def run_tourism_category_selector(user_interests: list, latitude: float, longitude: float, weather: list[Any]):
    """
    Ejecuta el flujo completo de selección de turismo.

    Args:
        user_interests: Lista de intereses del usuario
        latitude: Latitud de la ubicación
        longitude: Longitud de la ubicación
        weather: Datos del clima y pronóstico

    Returns:
        Diccionario con los resultados o string con output raw
    """
    interests_str = ", ".join(user_interests)

    tourism_result = crew.kickoff(inputs={
        'user_interests': interests_str,
        'latitude': latitude,
        'longitude': longitude,
        'weather': weather
    })

    last_task_output = select_final_places.output

    if last_task_output.pydantic:
        return last_task_output.pydantic.model_dump()
    elif last_task_output.json_dict:
        return last_task_output.json_dict
    else:
        return last_task_output.raw
