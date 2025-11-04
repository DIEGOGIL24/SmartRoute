import requests
import os
from crewai.tools import tool

@tool("read_categories_file")
def read_categories_file() -> str:
    """
    Lee un archivo .txt que contiene una lista de categorías turísticas.

    Returns:
        Contenido del archivo como string
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'categories2.txt')
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return f"Error: No se encontró el archivo"
    except Exception as e:
        return f"Error al leer el archivo: {str(e)}"

if __name__ == '__main__':
    print(read_categories_file.run())