from typing import List

from pydantic import BaseModel, Field

class ReportInterests(BaseModel):
    selected_categories: List[str] = Field(description="lista de intereses con el NOMBRE EXACTO del archivo")