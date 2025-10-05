from typing import List
from pydantic import BaseModel


class Task(BaseModel):
    area: str
    subtask: List[str]

