from langgraph.prebuilt import create_react_agent
from src.utils.jira import JiraUtils
from src.settings.app_settings import AppSettings
from src.models.graph_state import GraphState
from src.models.story_employee import EmployeeStory
from src.utils.chat_watsonx_llm import ChatLLMInstance
from src.tools.determine_who import DetermineWho


class AssignStory:
    def __init__(self, chat_llm: ChatLLMInstance, settings: AppSettings, logger):
        self.settings = settings
        self.logger = logger
        self.chat_llm = chat_llm
        self.jira_utils = JiraUtils(
            self.settings.JIRA_EMAIL, self.settings.JIRA_API_TOKEN, self.logger
        )

    def story_assignee(self, state: GraphState):
        """Assigns stories to employees in batches of 3 and updates state accordingly."""

        all_stories = list(state["stories"].values())
        batch_size = 3

        for i in range(0, len(all_stories), batch_size):
            stories = all_stories[i : i + batch_size]  # Pick the next 3 stories
            project_details = {
                "project_name": state["input"].project_name,
                "project_description": state["input"].project_desc,
            }
            # Get story assignment response
            story_agent = self.get_react_agent(
                self.get_tools(
                    chat_llm=self.chat_llm,
                    stories=stories,
                    project_details=project_details,
                    employee_bandwidth=state["employee_bandwidth"],
                )
            )
            agent_prompt = """ 
                Your task is to assign each story to the most suitable employee based on the following criteria:

                1. **Skill Match** - The employee must have the required skills for the story.  
                2. **Bandwidth Availability** - Verify that the employee has the capacity to take on the story. If they don't, identify another employee who can.  
                3. **Unique Assignment** - Each story should be assigned to only one employee.  

                To accomplish this, you have access to the following tool:  
                - **Determine Who**  
                Ensure that every story is assigned efficiently, considering both skill relevance and workload distribution.  
            """

            response = story_agent.invoke({"messages": [("user", agent_prompt)]})
            response = response["structured_response"]
            response = response.model_dump()
            # Update state with assigned employee emails and update bandwidth
            for story_id, emp_id in response["story_employee_mapping"].items():
                story = state["stories"][story_id]
                employee = state["employee_data"].get(emp_id)
                if employee:
                    # story.assignee = employee.email
                    story.assignee = employee.emp_id
                    if emp_id in state["employee_bandwidth"]:
                        state["employee_bandwidth"][emp_id][
                            "bandwidth"
                        ] -= story.estimate
                        state["employee_bandwidth"][emp_id]["story"] = story.title

        return {
            "employee_bandwidth": state["employee_bandwidth"],
            "stories": state["stories"],
            "next_node": "assign_story_jira",
        }

    def get_react_agent(self, tools):
        story_agent = create_react_agent(
            model=self.chat_llm,
            tools=tools,
            debug=True,
            response_format=EmployeeStory,
        )
        return story_agent

    def get_tools(self, stories, project_details, chat_llm, employee_bandwidth):
        return [
            DetermineWho(
                chat_llm=chat_llm,
                employee_bandwidth=employee_bandwidth,
                stories=stories,
                project_details=project_details,
            )
        ]
