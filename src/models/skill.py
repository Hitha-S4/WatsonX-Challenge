from typing import List
from pydantic import BaseModel
from enum import Enum

class ProficiencyLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    EXPERT = "Expert"

class Skill(BaseModel):
    skill_name: str
    proficiency: ProficiencyLevel 


