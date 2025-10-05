from src.settings.app_settings import AppSettings
from src.models.graph_state import GraphState
from src.models.sprint import Sprint


class PlanNextSprint:
    def __init__(self, settings: AppSettings, logger):
        self.settings = settings
        self.logger = logger

    def plan_next_sprint(self, state: GraphState):
        """
        Assign stories to employees ensuring the total estimate does not exceed their bandwidth.
        Stories are assigned sequentially based on their order in the state['stories'].
        """
        assigned_stories = {}

        for story in state["stories"].values():
            emp_id = story.assignee
            estimate = story.estimate

            if emp_id in state["employee_bandwidth"]:
                remaining_bandwidth = state["employee_bandwidth"][emp_id]["bandwidth"]

                # Ensure story fits within the remaining bandwidth
                if estimate <= remaining_bandwidth:
                    assigned_stories[story.issue_id] = story
                    state["employee_bandwidth"][emp_id]["bandwidth"] -= estimate
                else:
                    # If the story can't fit, stop assigning further (as order matters)
                    break

        state['next_sprint'].stories = assigned_stories

        return {"next_sprint": state['next_sprint'], "next_node": "create_and_update_sprint"}
