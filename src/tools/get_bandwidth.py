import requests
import logging
from typing import List, Dict, ClassVar,Any
from src.models.story import Story
from langchain.tools import BaseTool
from src.settings.app_settings import AppSettings
from src.models.story_employee import EmployeeStory



class GetBandwidth(BaseTool):
    """Tool to map story to an employee"""

    name: str = "Get Bandwidth"
    description: str = (
    "Verifies whether each employee has enough bandwidth to take on the story, based on the story's estimate and the employee's available bandwidth. "
    "Returns a dictionary indicating whether each employee has sufficient bandwidth."
    )
    employee_bandwidth_mapping:dict
    stories: List[Story]
    settings: ClassVar = AppSettings()
    logger: ClassVar = logging.getLogger(__name__)

    def _run(self,story_employee_mapping:dict):
        """Verifies if each employee has enough bandwidth for their assigned story"""
        result = {}
        for issue_id, emp_id in story_employee_mapping.items():
            story = next((s for s in self.stories if s.issue_id == issue_id), None) 
            if story:
                story_estimate = story.estimate  
                employee_bandwidth = self.employee_bandwidth_mapping.get(emp_id, 0)
                if employee_bandwidth >= story_estimate:
                    result[emp_id] = True  
                else:
                    result[emp_id] = False
            else:
                result[emp_id] = False  
        return result