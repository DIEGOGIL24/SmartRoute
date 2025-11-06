from typing import List, Optional

from pydantic import BaseModel, Field


class ReportInterests(BaseModel):
    selected_categories: List[str] = Field(description="lista de intereses con el NOMBRE EXACTO del archivo")


class DisplayName(BaseModel):
    text: str = Field(description="Nombre del lugar (texto visible)")
    languageCode: str = Field(description="Código de idioma del nombre, por ejemplo 'es' o 'en'")


class Place(BaseModel):
    types: List[str] = Field(description="Lista de categorías o tipos del lugar según Google Places")
    formattedAddress: str = Field(description="Dirección formateada del lugar")
    rating: Optional[float] = Field(default=None, description="Calificación promedio del lugar (0.0 a 5.0)")
    displayName: DisplayName = Field(description="Objeto con el nombre y código de idioma del lugar")


class PlacesReport(BaseModel):
    places: List[Place] = Field(description="Lista de lugares encontrados en la búsqueda")


##Itinerario JSON model

class TourismAgentResponse(BaseModel):
    places: List[Place]
    weather_note: str = Field(
        ...,
        description="Explicación de por qué estos lugares fueron seleccionados basándose en el clima y pronóstico"
    )