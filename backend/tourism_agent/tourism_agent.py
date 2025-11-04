from crewai import Agent, Task, Crew, LLM
from .tourism_tools import read_categories_file
from .tourism_json import ReportInterests
from .places_api import search_places

# load_dotenv()

llm = LLM(
    model="ollama/qwen3",
    base_url="http://ollama:11434"
)

tourism_agent = Agent(
    role="Experto en Turismo y Selección de Experiencias",
    goal="""Leer un catálogo de categorías OBLIGATORIAMENTE usando la herramienta 'read_categories_file'.
        Luego, analizar los intereses del usuario ({user_interests}) y seleccionar las categorías más pertinentes
        de ESE catálogo leído.""",
    backstory="""Eres un agente de turismo especializado con amplia experiencia en matching de 
    perfiles de viajeros con experiencias turísticas. Tu expertise está en comprender las 
    preferencias, motivaciones y estilos de viaje de los usuarios para recomendar las categorías 
    de actividades y experiencias que mejor se alineen con sus intereses.

    Tienes la habilidad de:
    - Interpretar intereses diversos y encontrar conexiones con categorías turísticas
    - Identificar categorías primarias y secundarias según relevancia
    - Justificar cada selección con argumentos sólidos
    - Detectar intereses implícitos que el usuario podría disfrutar

    IMPORTANTE: Siempre debes leer el archivo de categorías usando la herramienta 
    read_categories_file antes de hacer cualquier recomendación.""",
    llm=llm,
    tools=[read_categories_file],
    verbose=True,
)

task_read_file = Task(
    description="""Usa la herramienta 'read_categories_file' para leer el contenido
    completo del archivo de categorías de turismo. Devuelve el contenido exacto
    del archivo como un string.""",
    expected_output="Un string que contiene todas las categorías del archivo, separadas por saltos de línea.",
    agent=tourism_agent
)

task_select_categories = Task(
    description="""Toma la lista de categorías extraida de la tarea anterior.
    Compara esa lista con los intereses del usuario: {user_interests}.
    Selecciona ÚNICAMENTE las categorías del contexto que coincidan o sean
    altamente relevantes para los intereses del usuario.""",
    expected_output="""Un JSON con:
    - selected_categories: categorías relevantes para el usuarioa""",
    agent=tourism_agent,
    context=[task_read_file],
    output_pydantic=ReportInterests
)

task_search_places = Task(
    description="""La tarea anterior seleccionó categorías relevantes.

    Usa la herramienta 'search_places' para buscar lugares cercanos que pertenezcan 
    a esas categorías.

    PARÁMETROS:
    - categories: Toma la lista 'selected_categories' del resultado anterior
    - latitude: 6.2518
    - longitude: -75.5636

    IMPORTANTE: 
    - Llama a la herramienta UNA VEZ pasando TODAS las categorías seleccionadas
    - La herramienta devolverá lugares para todas las categorías""",
    expected_output="Lista de lugares encontrados en formato JSON con nombre, dirección, categoría y rating",
    agent=tourism_agent,
    context=[task_select_categories],
    tools=[search_places]
)

crew = Crew(
    agents=[tourism_agent],
    tasks=[task_read_file, task_select_categories, task_search_places],
    verbose=True
)


def run_tourism_category_selector(user_interests: list):
    interests_str = ", ".join(user_interests)

    tourism_result = crew.kickoff(inputs={
        'user_interests': interests_str
    })

    if tourism_result.pydantic:
        return tourism_result.pydantic.model_dump()

    return tourism_result.raw
