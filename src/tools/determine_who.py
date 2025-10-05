import requests
import logging
from typing import List, Dict, ClassVar,Any
from src.models.story import Story
from src.models.employee import Employee
from src.utils.chat_watsonx_llm import ChatLLMInstance
from langchain.tools import BaseTool
from src.settings.app_settings import AppSettings
from langchain_core.prompts import PromptTemplate
from src.models.story_employee import EmployeeStory

PROMPT_TEMPLATE = PromptTemplate.from_template(
    "You are given a list of stories: {stories}, along with project details: {project_details}. Additionally, you have employee bandwidth data: {employee_bandwidth}, which includes each employee’s skills and availability "
    "Your task is to assign each story to the most suitable employee based on their skills. "
    "Each story should be assigned only once.Employees may have multiple skills, but prioritize matching the required skill for each story "
    "Distribute stories as evenly as possible while ensuring skill alignment."
    "If stories are related or dependent on each other, assign them to the same employee whenever feasible"
)

class DetermineWho(BaseTool):
    """Tool to map story to an employee"""

    name: str = "Determine who"
    description: str = (
        "Identifies the most suitable employee for a story based on skills and returns employee-story mapping"
    )
    chat_llm: Any
    employee_bandwidth:Dict[str, Dict]
    stories: List[Story]
    project_details: Dict[str, Any]

    settings: ClassVar = AppSettings()
    logger: ClassVar = logging.getLogger(__name__)

    def _run(self) -> List[Dict[str, str]]:
        """Synchronously assigns employees to stories based on skills."""
        assignee_chain = PROMPT_TEMPLATE | self.chat_llm.with_structured_output(EmployeeStory)
        story_employee_mapping = assignee_chain.invoke(
            input={
                "stories": self.stories, 
                "employee_bandwidth": self.employee_bandwidth,
                "project_details": self.project_details
            }
        )
        return story_employee_mapping