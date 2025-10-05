from datetime import datetime
from typing import Literal, List
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langgraph.types import Command
from src.utils.chat_watsonx_llm import ChatLLMInstance
from src.models.graph_state import GraphState
from src.models.epic import Epic
from src.models.list_epics import EpicList
from src.models.list_stories import StoryList
from src.settings.app_settings import AppSettings

PROMPT_TEMPLATE = PromptTemplate.from_template(
    "This is the name of the Project: {project_name}, this is its description: {project_description}.\
    Your job is to identify all the Jira Stories that can be created from the list of subtasks that come under the given domain\
    Epic: {area}, Subtasks: {subtasks}. You can break subtasks into many stories if seemed necessary. Make sure stories are in the sequential order of their completion. \
    Only fill Story Title, Description, Estimate Story Points, Epic Name \
    Only fill the mentioned parameters.\
    DONOT FILL OTHER PARAMETERS "
)


PROMPT_TEMPLATE_EPIC = PromptTemplate.from_template(
    "This is the name of the Project: {project_name}, this is its description: {project_description}.\
    Your job is to create Jira Epic and its details from the following domains of work for the project. \
    Dont create additonal EPICs other than the ones in the below list \
    Domain: {area}. Make sure they are in the sequential order of their completion. \
    Fill in only Epic Title and description. \
    DONOT FILL OTHER PARAMETERS "
)


class EpicStories:
    def __init__(self, chat_llm: ChatLLMInstance, logger, settings: AppSettings):
        self.chat_llm = chat_llm
        self.logger = logger
        self.settings = settings

    def identify_epics_stories(self, state: GraphState):
        # self.logger(f"Inside Identify for {state['kwargs']}")
        if self.settings.MODE == "Prod":
            self.logger.info(f"Identifying Epics")
            epic_chain = self.get_chain(PROMPT_TEMPLATE_EPIC, EpicList)
            areas = list(state["project_data"].keys())

            epics_list = epic_chain.invoke(
                input={
                    "project_name": state["input"].project_name,
                    "project_description": state["input"].project_desc,
                    "area": areas,
                }
            )

            story_chain = self.get_chain(PROMPT_TEMPLATE, StoryList)
            final_stories_list = []

            for area, tasks in state["project_data"].items():
                self.logger.info(f"Identifying Stories for {area}")
                story_list = story_chain.invoke(
                    input={
                        "project_name": state["input"].project_name,
                        "project_description": state["input"].project_desc,
                        "area": tasks.area,
                        "subtasks": tasks.subtask,
                    }
                )
                for epic in epics_list.epics:
                    if epic.title.lower() == area.lower():
                        epic.stories = story_list.stories

                final_stories_list.extend(story_list.stories)

            return {"epics": epics_list.epics, "stories": final_stories_list, 'next_node': 'estimate_sprint_count'}
        return {"next_node": "estimate_sprint_count"}

    def get_chain(self, prompt_template, model):
        chain = prompt_template | self.chat_llm.with_structured_output(model)
        return chain
