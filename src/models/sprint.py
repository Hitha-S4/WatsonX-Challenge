from typing import Dict
from pydantic import BaseModel
from src.models.story import Story
from datetime import datetime

class Sprint(BaseModel):
    id: int
    name: str
    startDate : datetime
    endDate : datetime
    goal: str
    stories: Dict[str, Story]