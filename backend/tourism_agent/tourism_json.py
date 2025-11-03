from pydantic import BaseModel, Field
from typing import List, Dict


class InterestAnalysis(BaseModel):
    interest_received: List[str] = Field(description="lista de intereses")
    traveler_profile: str = Field(description="descripción breve del tipo de viajero")


class SelectedCategory(BaseModel):
    category: str = Field(description="NOMBRE EXACTO del archivo")
    relevance: str = Field(description="explicación de relevancia")
    key_experiences: List[str] = Field(description="experiencias")


class ReportInterests(BaseModel):
    file_read: str = Field(description="primeras 3 líneas del archivo para verificar que lo leíste")
    interest_analysis: InterestAnalysis
    selected_categories: List[SelectedCategory]
    total_categories_selected: int = Field(description="número")