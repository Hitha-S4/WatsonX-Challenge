import operator
from typing import Annotated, List, Tuple, Dict, Any, Union
from typing_extensions import TypedDict
from src.models.project_planner_request import ProjectPlannerRequest
from src.models.task import Task
from src.models.employee import Employee
from src.models.sprint import Sprint
from src.models.project_plan import ProjectPlan
from src.models.story import Story
from src.models.epic import Epic


class GraphState(TypedDict):
    input: ProjectPlannerRequest
    kwargs: Any
    project_data: Dict[str, Task]
    employee_data: Dict[str, Employee]
    next_sprint: Sprint
    project_plan: ProjectPlan
    stories: Union[List[Story], Dict[str, Story]]
    epics: List[Epic]
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    should_end: bool
    next_node: str
    employee_bandwidth: Dict[str, Dict]
    available_sprint_days_count: Any
