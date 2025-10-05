from datetime import datetime
import pandas as pd
from collections import defaultdict
from pydantic import BaseModel
from typing import List, Literal
from langgraph.types import Command
from src.models.epic import Epic
from src.models.task import Task
from src.models.graph_state import GraphState
from src.settings.app_settings import AppSettings
from src.models.employee import Employee
from src.models.leave import Leave
from src.models.skill import Skill, ProficiencyLevel
from src.config.dummy_data import DUMMY_EPIC_DATA, DUMMY_STORY_DATA


class CSVProcessor:
    def __init__(self, settings: AppSettings, logger):
        self.logger = logger
        self.settings = settings

    def data_manager(
        self, state: GraphState
    ) -> Command[Literal["load_input_data", "load_employee_data", "epic_and_stories"]]:
        if "project_data" not in state:
            return Command(goto="load_input_data")
        elif "next_node" in state and state["next_node"]:
            return Command(goto=state["next_node"])
        # elif "project_data" in state and state["project_data"]:
        #     return Command(goto="load_employee_data")
        # elif "employee_data" in state and state["employee_data"]:
        #     return Command(goto="epic_and_stories")

    def process_csv(self, state: GraphState):
        self.logger.info("Loading Input Data")
        csv_path = self.settings.CSV_PATH
        df = pd.read_csv(csv_path, header=1)

        task_dict = defaultdict(list)
        for _, row in df.iterrows():
            task_dict[row["Task"]].append(row["Sub-task"])

        epic_list = [
            Epic(epic_id="", title=task, description="", stories=[])
            for task in task_dict.keys()
        ]

        task_dict = {
            task: Task(area=task, subtask=subtasks)
            for task, subtasks in task_dict.items()
        }

        return {"project_data": task_dict, "epics": epic_list, "next_node": "load_employee_data"}

    def read_employee_data(self, state: GraphState):
        """Reads employee data from a CSV file and returns a dictionary of Employee objects."""
        self.logger.info("Loading Employee Data")
        csv_path = self.settings.EMPLOYEE_DATA
        df = pd.read_csv(csv_path, header=1)
        employees = {}

        for _, row in df.iterrows():
            emp = Employee(
                emp_id=row["Employee id"],
                name=row["name"],
                email=row["Email id"],
                skills=self.parse_skills(row["Skills"]),
                leave_plans=self.parse_leaves(row["Leave plan"]),
            )
            employees[emp.emp_id] = emp

        if self.settings.MODE.lower() == "dev":
            return {
                "epics": DUMMY_EPIC_DATA,
                "stories": DUMMY_STORY_DATA,
                "employee_data": employees,
                "next_node": "epic_and_stories",
            }

        return {"employee_data": employees, "next_node": "epic_and_stories"}

    def parse_skills(self, skill_str: str) -> List[Skill]:
        """Parses the skills string into a list of Skill objects."""
        skills = []
        skill_str = skill_str.strip('"')
        skill_pairs = skill_str.split("], ")

        for pair in skill_pairs:
            pair = pair.strip("[] ")
            if "," in pair:
                skill_name, level = pair.rsplit(",", 1)
                skills.append(
                    Skill(
                        skill_name=skill_name.strip(),
                        proficiency=ProficiencyLevel(level.strip()),
                    )
                )

        return skills

    def parse_leaves(self, leave_str: str) -> List[Leave]:
        """Parses the leave plan string into a list of Leave objects."""
        leaves = []
        leave_str = leave_str.strip('"')
        leave_str = leave_str.replace("],[", "], [")
        leave_pairs = leave_str.split("], ")

        for pair in leave_pairs:
            pair = pair.strip("[] ")
            if "," in pair:
                occasion, leave_date = pair.rsplit(",", 1)
                try:
                    leaves.append(
                        Leave(
                            ocassion=occasion.strip(),
                            date=datetime.strptime(
                                leave_date.strip(), "%Y-%m-%d"
                            ).date(),
                        )
                    )
                except ValueError as e:
                    self.logger.error(f"Error parsing leave date: {leave_date} - {e}")
                    continue

        return leaves
