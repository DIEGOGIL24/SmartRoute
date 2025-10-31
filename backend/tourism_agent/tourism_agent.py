from crewai import Agent, Task, Crew, LLM
from .tourism_tools import read_categories_file

# load_dotenv()

llm = LLM(
    model="ollama/qwen3",
    base_url="http://ollama:11434"
)

tourism_agent = Agent(
    role="Experto en Turismo y Selección de Experiencias",
    goal="""Analizar los intereses del usuario ({user_interests}) y seleccionar las categorías turísticas más pertinentes del catálogo disponible, 
    proporcionando recomendaciones personalizadas y justificadas.""",
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

task1 = Task(
    description="""PASO 1 - OBLIGATORIO: Usa INMEDIATAMENTE la herramienta read_categories_file() para obtener el catálogo de categorías disponibles. NO continúes sin hacer esto primero.

PASO 2: Una vez que tengas el contenido del archivo, copia EXACTAMENTE los nombres de las categorías que aparecen en él.

PASO 3: Analiza los intereses del usuario: {user_interests}

PASO 4: Selecciona ÚNICAMENTE categorías que aparecen en el archivo leído. Nombres EXACTOS, sin modificaciones.

PASO 5: Clasifica las categorías seleccionadas en:
   - ALTAMENTE RECOMENDADAS: 3-5 categorías con alineación perfecta
   - RECOMENDADAS: 2-4 categorías con buena alineación
   - OPCIONALES: 1-3 categorías de interés indirecto

REGLAS CRÍTICAS:
❌ NO inventes categorías
❌ NO modifiques nombres de categorías
❌ NO agregues categorías que no están en el archivo
✅ USA SOLO categorías del archivo leído
✅ COPIA los nombres exactamente como aparecen""",

    expected_output="""JSON estructurado con este formato EXACTO:

    {
        "archivo_leido": "primeras 3 líneas del archivo para verificar que lo leíste",
        "analisis_de_intereses": {
            "intereses_recibidos": ["lista", "de", "intereses"],
            "perfil_de_viajero": "descripción breve del tipo de viajero",
            "intereses_detectados": ["intereses explícitos e implícitos"]
        },
        "categorias_seleccionadas": {
            "altamente_recomendadas": [
                {
                    "categoria": "NOMBRE EXACTO del archivo",
                    "relevancia": "explicación de relevancia",
                    "experiencias_clave": ["experiencias"]
                }
            ],
            "recomendadas": [
                {
                    "categoria": "NOMBRE EXACTO del archivo",
                    "relevancia": "explicación",
                    "experiencias_clave": ["experiencias"]
                }
            ],
            "opcionales": [
                {
                    "categoria": "NOMBRE EXACTO del archivo",
                    "relevancia": "explicación",
                    "experiencias_clave": ["experiencias"]
                }
            ]
        },
        "resumen": "Conclusión sobre el match",
        "total_categorias_seleccionadas": "número"
    }""",
    agent=tourism_agent,
)

crew = Crew(
    agents=[tourism_agent],
    tasks=[task1],
    verbose=True
)


def run_tourism_category_selector(user_interests: list):
    """
    Ejecuta el agente de turismo para seleccionar categorías basadas en intereses.

    Args:
        user_interests: Lista de intereses del usuario (ej: ["naturaleza", "aventura", "fotografía"])

    Returns:
        Resultado del análisis con categorías seleccionadas
    """

    interests_str = ", ".join(user_interests)

    result = crew.kickoff(inputs={
        'user_interests': interests_str
    })
    return result
