from pydantic import BaseModel, Field
from typing import List, Dict, Any


class Temperature(BaseModel):
    min_temp: float
    max_temp: float

class DailyForecast(BaseModel):
    date: str = Field(description="from API")
    description: str = Field(description="from API")
    temperature: Temperature
    wind_speed: float = Field(description="from API")
    humidity: int = Field(description="from API")
    clouds: int = Field(description="from API")
    summary: str = Field(description="YOUR ONE-SENTENCE RECOMMENDATION HERE")

class ForecastReport(BaseModel):
    city: str = Field(description="city name")
    forecasts: List[DailyForecast]

class WeatherReport(BaseModel):
    current: Dict[str, Any] = Field(description="<result from get_weather tool>")
    forecast: ForecastReport
