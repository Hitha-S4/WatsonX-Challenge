from typing import List
from pydantic import BaseModel
from src.models.skill import Skill
from src.models.leave import Leave


class Employee(BaseModel):
    emp_id: str
    name: str
    email: str
    skills: List[Skill]
    leave_plans: List[Leave]
