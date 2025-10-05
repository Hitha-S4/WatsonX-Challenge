from typing import List
from pydantic import BaseModel, Field
from src.models.epic import Epic


class EpicList(BaseModel):
    epics: List[Epic] = Field(description="List of Objects of Model Epic")
