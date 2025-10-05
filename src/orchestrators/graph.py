from langgraph.graph import StateGraph, START, END
from src.models.graph_state import GraphState
from src.utils.chat_watsonx_llm import ChatLLMInstance
from src.nodes.epic_stories import EpicStories
from src.nodes.supervisor import Supervisor
from src.nodes.read_csv import CSVProcessor
from src.nodes.estimated_sprint_count import EstimatedSprintCount
from src.nodes.jira import JiraNode
from src.nodes.story_assignee import AssignStory

from src.nodes.order_stories import OrderStories
from src.nodes.plan_next_sprint import PlanNextSprint
from src.nodes.supervisor import Supervisor


class ProjectPlannerGraph:
    def __init__(self, model, settings, logger):
        self.model = model
        self.logger = logger
        # self.app = self.create_graph()
        self.settings = settings
        self.chat_llm_manager = ChatLLMInstance(
            settings=self.settings, model_id="meta-llama/llama-3-3-70b-instruct"
        )
        self.chat_llm = self.chat_llm_manager.get_llm()

        self.supervisor = Supervisor(chat_llm=self.chat_llm, logger=self.logger)
        self.epic_and_stories = EpicStories(
            chat_llm=self.chat_llm, logger=self.logger, settings=self.settings
        )
        self.csv_manager = CSVProcessor(settings=self.settings, logger=self.logger)
        self.estimates_sprint_count = EstimatedSprintCount(
            country_code="US", logger=self.logger
        )
        self.jira_node = JiraNode(settings=self.settings, logger=self.logger)
        self.assign_story = AssignStory(
            chat_llm=self.chat_llm, settings=self.settings, logger=self.logger
        )

        self.order_stories = OrderStories(chat_llm=self.chat_llm, logger=self.logger)

        self.plan_next_sprint = PlanNextSprint(
            settings=self.settings, logger=self.logger
        )

        self.supervisor = Supervisor(chat_llm=self.chat_llm, logger=self.logger)
        ## Create Node Objects
        self.workflow = ""

    def create_graph(self):
        self.workflow = StateGraph(self.model)

        ## Add nodes and edges
        self.workflow.add_node(
            "estimate_sprint_count", self.estimates_sprint_count.calculate_sprint_days
        )
        self.workflow.add_node(
            "epic_and_stories", self.epic_and_stories.identify_epics_stories
        )
        self.workflow.add_node("data_manager", self.csv_manager.data_manager)
        self.workflow.add_node("load_input_data", self.csv_manager.process_csv)
        self.workflow.add_node(
            "load_employee_data", self.csv_manager.read_employee_data
        )
        self.workflow.add_node("create_jira_issues", self.jira_node.create_jira_issues)
        self.workflow.add_node("story_assignee", self.assign_story.story_assignee)
        self.workflow.add_node("assign_story_jira", self.jira_node.assign_story_jira)
        self.workflow.add_node("order_stories", self.order_stories.order_stories)
        self.workflow.add_node(
            "employee_bandwidth_for_sprint",
            self.estimates_sprint_count.employee_bandwidth_for_next_sprint,
        )

        self.workflow.add_node(
            "plan_next_sprint", self.plan_next_sprint.plan_next_sprint
        )

        self.workflow.add_node(
            "utils_manager", self.estimates_sprint_count.utils_manager
        )
        self.workflow.add_node("jira_manager", self.jira_node.jira_manager)

        self.workflow.add_node("agent_manager", self.supervisor.agent_manager)

        self.workflow.add_node("create_and_update_sprint", self.jira_node.create_sprint)

        self.workflow.add_edge("load_input_data", "data_manager")
        self.workflow.add_edge("load_employee_data", "data_manager")
        self.workflow.add_edge("epic_and_stories", "utils_manager")
        self.workflow.add_edge("estimate_sprint_count", "jira_manager")
        self.workflow.add_edge("create_jira_issues", "agent_manager")

        self.workflow.add_edge("order_stories", "agent_manager")
        self.workflow.add_edge("employee_bandwidth_for_sprint", "agent_manager")
        self.workflow.add_edge("story_assignee", "jira_manager")
        self.workflow.add_edge("assign_story_jira", "utils_manager")
        self.workflow.add_edge("plan_next_sprint", "jira_manager")
        self.workflow.add_edge(START, "data_manager")
        self.workflow.add_edge("create_and_update_sprint", END)


        app = self.workflow.compile()
        return app

    # def should_end(self, state: GraphState):
    #     if "next_node" in state and (state["next_node"] == "__end__" or state["next_node"] is END):
    #         return END
    #     elif "next_node" in state and state["next_node"]:
    #         return state["next_node"]
