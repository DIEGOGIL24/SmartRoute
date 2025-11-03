from typing import List

from pydantic import BaseModel


class MessageRequest(BaseModel):
    text: str


class MessageRequestForWeather(BaseModel):
    city: str
    time: str


class MessageRequestForTourism(BaseModel):
    interests: List[str]


class HealthResponse(BaseModel):
    status: str
    postgres: str
    rabbitmq: str
