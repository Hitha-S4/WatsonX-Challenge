from copy import deepcopy
from typing import Dict, List, Literal
from langgraph.types import Command
from src.nodes.read_csv import CSVProcessor
from src.settings.app_settings import AppSettings
from src.models.graph_state import GraphState
from src.utils.jira import JiraUtils


class JiraNode:
    def __init__(self, settings: AppSettings, logger):
        self.settings = settings
        self.logger = logger
        self.jira_utils = JiraUtils(
            self.settings.JIRA_EMAIL, self.settings.JIRA_API_TOKEN, self.logger
        )

    def jira_manager(
        self, state: GraphState
    ) -> Command[Literal["create_jira_issues", "assign_story_jira","create_and_update_sprint"]]:
        return Command(goto=state["next_node"])

    def create_jira_issues(self, state: GraphState):
        """
        Reads epics and tasks from CSV and creates Jira issues.
        """
        stories_dict = self.jira_utils.process_epics_and_tasks(
            state["epics"], state["stories"]
        )
        return {"stories": stories_dict, "next_node": "order_stories"}

    def assign_story_jira(self, state: GraphState):
        """
        Assign each story in the state to an employee in Jira.
        """
        for story in state["stories"].values():
            temp_story = deepcopy(story)
            temp_story.assignee = state["employee_data"].get(story.assignee, "").email
            self.jira_utils.assign_story(temp_story)
        return {"next_node": "employee_bandwidth_for_sprint"}

    def create_sprint(self, state: GraphState):
        """
        create the sprint on the jira board
        """
        self.jira_utils.create_sprint(state["next_sprint"])
        self.jira_utils.assign_stories_to_sprint(state["next_sprint"])

        return {"next_node": "__end__"}

    
    def assign_stories_to_sprint(self, state: GraphState):
        """
        create the sprint on the jira board
        """
        response = self.jira_utils.assign_stories_to_sprint(state["next_sprint"])
        return response