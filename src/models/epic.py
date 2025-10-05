from typing import List
from pydantic import BaseModel, Field
from src.models.story import Story


class Epic(BaseModel):
    epic_id: str = Field(description="DONOT UPDATE. Epic Id")
    title: str = Field(description="Title of the Jira EPIC")
    description: str = Field(description="Description of the Jira EPIC")
    stories: List[Story]
