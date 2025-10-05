import datetime
from datetime import date, timedelta
import requests
from typing import Dict, List, Literal
from langgraph.types import Command
from src.utils.calender import PublicHolidayUtils
from src.models.graph_state import GraphState, Employee
from src.models.skill import Skill
from src.models.leave import Leave
from src.models.employee import Employee
from src.models.sprint import Sprint

class EstimatedSprintCount:
    def __init__(self, country_code: str, logger):
        self.calendar_api = PublicHolidayUtils(country_code)
        self.logger = logger

    def utils_manager(self, state: GraphState)-> Command[Literal["estimate_sprint_count", "employee_bandwidth_for_sprint"]]:
        return Command(goto=state['next_node'])

    def calculate_sprint_days(self, state: GraphState) -> Dict:
        """
        Calculates the total estimated days needed for the project,
        considering employee capacity, public holidays, and sprint constraints.
        """
        # Step 1: Get total sprint points needed
        self.logger.info(f"stories: {state['stories']}")
        total_points = sum(story.estimate for story in state["stories"])
        self.logger.info(f"total_points: {total_points}")

        # Step 2: Get number of employees
        num_employees = len(state["employee_data"])
        self.logger.info(f"number of employees: {num_employees}")
        if num_employees == 0:
            raise ValueError("No employees found for the project.")

        # Step 3: Calculate estimated days needed
        estimated_days = total_points // num_employees
        self.logger.info(f"estimated: {estimated_days}")

        # Step 4: Fetch public holidays from tomorrow for estimated_days duration
        start_date = datetime.date.today() + timedelta(days=1)
        end_date = start_date + timedelta(days=int(2 * estimated_days))
        public_holidays = set(
            self.calendar_api.get_public_holidays(start_date, end_date)
        )
        # num_holidays = len(public_holidays)

        # Step 5: Adjust estimated days to include public holidays
        # final_days_needed = estimated_days + num_holidays

        end_date, available_days = self.calculate_end_date(
            start_date=start_date,
            estimated_days=estimated_days,
            public_holidays=public_holidays,
        )

        # Step 6: Compute available days in a sprint (next 14 days)
        sprint_start = start_date
        sprint_end = sprint_start + timedelta(days=14)

        # Remove weekends (Saturdays & Sundays)
        available_sprint_days = [
            sprint_start + timedelta(days=i)
            for i in range(14)
            if (sprint_start + timedelta(days=i)).weekday() < 5  # 0-4 are weekdays
        ]

        # Employee bandwidth calculation
        employee_bandwidth = {}
        for emp_id, employee in state["employee_data"].items():
            # Count the number of leaves for each employee within the project duration (from tomorrow to final_days_needed)
            leave_count = self.count_leaves_in_range(employee, start_date, end_date)

            # Calculate the bandwidth: final_days_needed - leave_count
            bandwidth = available_days - leave_count
            employee_bandwidth[emp_id] = {
                "employee_name": employee.name,
                "bandwidth": bandwidth,
                "skills": employee.skills,
            }

        self.logger.info(f"len of available days for project: available_days")

        # Remove public holidays from available days
        available_sprint_days = [
            day for day in available_sprint_days if day not in public_holidays
        ]
        self.logger.info(f"available days for next sprint: {available_sprint_days}")
        self.logger.info(f"bandwidth: {employee_bandwidth}")

        return {
            "available_sprint_days_count": len(available_sprint_days),
            "employee_bandwidth": employee_bandwidth,
            "next_node": "create_jira_issues"
        }

    def employee_bandwidth_for_next_sprint(self, state: GraphState):
        """Calculate Employee bandwidth for next sprint"""

        sprint_duration = 14

        start_date = datetime.date.today() + timedelta(days=1)
        end_date = start_date + timedelta(days=sprint_duration)

        employee_bandwidth = {}
        for emp_id, employee in state["employee_data"].items():
            leave_count = self.count_leaves_in_range(employee, start_date, end_date)

            bandwidth = sprint_duration - leave_count - 4
            employee_bandwidth[emp_id] = {
                "employee_name": employee.name,
                "bandwidth": bandwidth,
            }
        
        sprint = Sprint(id = 1, name="Sprint 1", startDate=start_date, endDate=end_date, goal="", stories={})

        return {"employee_bandwidth": employee_bandwidth, "next_node": "plan_next_sprint", "next_sprint": sprint}

    def count_leaves_in_range(
        self, employee: Employee, start_date: date, end_date: date
    ) -> int:
        """
        Counts the number of leave days for the employee in the given date range.
        """
        leave_count = 0
        self.logger.info(f"employee leave plan:{employee.leave_plans}")
        for leave in employee.leave_plans:
            self.logger.info(f"start_date:{start_date}")
            self.logger.info(f"leave_date:{leave.date}")
            self.logger.info(f"end_date:{end_date}")
            if start_date <= leave.date <= end_date:
                leave_count += 1
            self.logger.info(f"leave count of {employee.email} is {leave_count}")
        return leave_count

    def calculate_end_date(self, start_date: date, estimated_days, public_holidays):
        """
        Calculates the end date by considering only working days (excluding weekends and public holidays).

        :param start_date: The starting date (datetime.date)
        :param estimated_days: Number of working days needed
        :param public_holidays: Set of public holidays (datetime.date)
        :return: Adjusted end_date
        """
        current_date = start_date
        workdays_count = 0

        while workdays_count < estimated_days:
            # Check if the day is a weekday and not a public holiday
            if current_date.weekday() < 5 and current_date not in public_holidays:
                workdays_count += 1
            # Move to the next day
            current_date += timedelta(days=1)

        return current_date, workdays_count
