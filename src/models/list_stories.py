from typing import List
from pydantic import BaseModel, Field
from src.models.story import Story


class StoryList(BaseModel):
    stories: List[Story] = Field(description="List of Objects of Model Epic")
