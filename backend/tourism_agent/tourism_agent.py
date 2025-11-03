from crewai import Agent, Task, Crew, LLM
from .tourism_tools import read_categories_file
from .tourism_json import ReportInterests

# load_dotenv()

llm = LLM(
    model="ollama/qwen3",
    base_url="http://ollama:11434"
)

tourism_agent = Agent(
    role="Experto en Turismo y Selección de Experiencias",
    goal="""PRIMERO leer el archivo de categorías usando read_categories_file(), 
    LUEGO analizar los intereses ({user_interests}) y seleccionar SOLO categorías 
    que existen en el archivo leído.""",

    backstory="""Eres un agente de turismo especializado.

        REGLAS CRÍTICAS:
        1. SIEMPRE usar read_categories_file() ANTES de hacer recomendaciones
        2. NUNCA inventar categorías
        3. SOLO seleccionar categorías que existen en el archivo
        4. Si una categoría no existe, buscar la más similar del archivo""",

    llm=llm,
    tools=[read_categories_file],
    verbose=True,
    allow_delegation=False 
)

task1 = Task(
    description="""Reads the categories file using read_categories_file().
                Compares the categories in the file with these interests: {user_interests} 
                Return ONLY categories that exist in the file.""",

    expected_output="""JSON with:
        - categories_from_file: list of all categories read
        - selected_categories: categories relevant to the user
        - justification: why you selected each category""",
    agent=tourism_agent,
    output_pydantic=ReportInterests
)

crew = Crew(
    agents=[tourism_agent],
    tasks=[task1],
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
