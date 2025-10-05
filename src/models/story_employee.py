from typing import List
from pydantic import BaseModel, Field
from src.models.story import Story



class EmployeeStory(BaseModel):
     story_employee_mapping : dict = Field(description="mapping of issue_id of a story to emp_id of an employee")
