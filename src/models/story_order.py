from typing import List
from pydantic import BaseModel, Field



class StoryOrder(BaseModel):
    stories: List[str] = Field(
        description="List of issue_ids in their order of required completion"
    )
