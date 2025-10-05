from typing import List
from pydantic import BaseModel
from src.models.sprint import Sprint


class ProjectPlan(BaseModel):
    name: str
    description: str
    sprints: List[Sprint]
