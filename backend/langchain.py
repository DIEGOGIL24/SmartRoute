from langchain_ollama import ChatOllama


def generar_itinerario(json_data: str):
    """
    Genera un itinerario turístico basado en el JSON proporcionado.
    El JSON debe contener la información de ciudad, fechas y lugares.
    """
    llm = ChatOllama(
        model="llama3.1",
        base_url="http://ollama:11434",
        temperature=0,
    )

    messages = [
        (
            "system",
            """
            Genera un itinerario turístico SOLO en español para la ciudad y fechas del siguiente JSON.

            Responde en español usando este formato exacto:

            🌍 Itinerario para [CIUDAD del JSON]
            📅 Período: [Primera fecha - Última fecha]

            ✨ Basado en el clima y lugares disponibles:

            Día 1 (fecha):
            - Mañana: [Actividad + lugar turístico + clima esperado]
            - Tarde: [Actividad + lugar turístico + clima esperado]  
            - Noche: [Actividad + lugar turístico + clima esperado]

            (Repite para cada fecha única en los pronósticos)

            🌡️ Clima esperado: [Resumen general]

            💡 Recomendaciones:
            - 3 consejos prácticos

            IMPORTANTE: Responde SOLO con el itinerario, sin repetir este prompt
            """,
        ),
        ("human", json_data),
    ]

    ai_msg = llm.invoke(messages)
    return ai_msg


def extract_text(response):
    return response.content


if __name__ == "__main__":
    ejemplo_json = """
    {
        "city": "Manizales",
        "dates": ["2025-11-10", "2025-11-11", "2025-11-12"],
        "places": ["Termales El Otoño", "Catedral Basílica", "Cable Aéreo"]
    }
    """
    resultado = generar_itinerario(ejemplo_json)
    out = extract_text(resultado)
    print(out)
