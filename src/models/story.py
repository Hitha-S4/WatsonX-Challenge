from typing import List
from pydantic import BaseModel, Field


class Story(BaseModel):
    issue_id: str = Field(description="DONOT UPDATE. Issue Id")
    title: str = Field(description="Title of the Jira Story/Issue")
    description: str = Field(description="Description of the Jira Story/Issue")
    assignee: str = Field(description="DONOT UPDATE. Assignee")
    epic: str = Field(description="Epic name from Area given")
    estimate: int = Field(description="Estimate/Story Points. Make sure youre accountable for the story points you give. Max value is 5. Keep the value realistic")
    sprint: str = Field(description="DONOT UPDATE. Sprint Name")
