import time
import requests
import base64
from typing import List, Dict

from src.models.story import Story
from src.models.epic import Epic
from src.models.employee import Employee
from src.models.sprint import Sprint

MAX_RETRIES = 3
RETRY_DELAY = 2


class JiraUtils:
    JIRA_BASE_URL = "https://ashwathyashwathy761.atlassian.net/rest/api/3/issue"
    PROJECT_KEY = "AI1"

    def __init__(self, email: str, api_token: str, logger):
        """Initialize JiraUtils with authentication"""
        self.encoded_auth_string = self.get_token(api_token, email)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {self.encoded_auth_string}",
        }
        self.epic_mapping = {}  # To store {epic_title: epic_key}
        self.logger = logger

    def get_token(self, api_token: str, email: str):
        auth_string = f"{email}:{api_token}"
        encoded_auth_string = base64.b64encode(auth_string.encode("utf-8")).decode(
            "utf-8"
        )
        return encoded_auth_string

    def create_epic(self, epic: Epic) -> str:
        """Create an epic in Jira and return its issue key"""
        payload = {
            "fields": {
                "project": {"key": self.PROJECT_KEY},
                "summary": epic.title,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": epic.description}],
                        }
                    ],
                },
                "issuetype": {"name": "Epic"},
            }
        }

        response = requests.post(self.JIRA_BASE_URL, headers=self.headers, json=payload)
        if response.status_code == 201:
            issue_key = response.json()["key"]
            self.logger.info(f"Epic Created: {epic.title} -> {issue_key}")
            return issue_key
        else:
            self.logger.info(f"Failed to create epic: {epic.title} -> {response.text}")
            return None

    def create_task(self, subtask_title: str, epic_key: str, description: str) -> str:
        """Create a task in Jira and link it to an epic"""
        payload = {
            "fields": {
                "project": {"key": self.PROJECT_KEY},
                "summary": subtask_title,  # Task name is the subtask title
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": description}],
                        }
                    ],
                },
                "issuetype": {"name": "Story"},
                "parent": {"key": epic_key},  # Link task to epic
                # "customfield_10037": [epic_key],  # Epic link field
            }
        }

        response = requests.post(self.JIRA_BASE_URL, headers=self.headers, json=payload)
        if response.status_code == 201:
            issue_key = response.json()["key"]
            self.logger.info(
                f"Task Created: {subtask_title} -> {issue_key} (Linked to {epic_key})"
            )
            return issue_key
        else:
            self.logger.info(
                f"Failed to create task: {subtask_title} -> {response.text}"
            )
            return None

    def process_epics_and_tasks(self, epics: List[Epic], stories: List[Story]):
        """Create epics and then link subtasks to the correct epics, then update the state and epic model"""

        # Step 1: Create epics and update the state with the Jira epic ID
        for epic in epics:
            try:
                epic_key = self.create_epic(epic)
                if epic_key:
                    self.epic_mapping[epic.title.lower()] = epic_key  # Store epic ID
                    epic.epic_id = epic_key
            except Exception as e:
                self.logger.info(f"Got an Exception {e}")

        # Step 2: Create subtasks as individual tasks, linking them to the correct epic and updating the Story model
        stories_dict = {}
        for story in stories:
            try:
                if story.epic.lower() in self.epic_mapping.keys():
                    epic_key = self.epic_mapping[story.epic.lower()]

                    # Retry loop for create_task
                    task_key = None
                    for attempt in range(1, MAX_RETRIES + 1):
                        task_key = self.create_task(
                            story.title, epic_key, story.description
                        )
                        if task_key:
                            break  # Exit retry loop if successful
                        self.logger.warning(
                            f"Retry {attempt}/{MAX_RETRIES}: Failed to create task for {story.title}. Retrying in {RETRY_DELAY}s..."
                        )
                        time.sleep(RETRY_DELAY)  # Wait before retrying

                    if task_key:
                        story.issue_id = task_key
                        stories_dict[story.issue_id] = story
                    else:
                        self.logger.error(
                            f"Failed to create task for {story.title} after {MAX_RETRIES} retries."
                        )
                        raise Exception(
                            f"Failed to create task for {story.title} after {MAX_RETRIES} retries."
                        )
                else:
                    self.logger.info(
                        f"Skipping Story: {story.title} (No matching epic found)"
                    )
                    raise RuntimeError(
                        f"Skipping Story: {story.title} (No matching epic found)"
                    )

            except Exception as e:
                self.logger.error(f"Got an Exception: {e}")
                raise Exception(f"Got an Exception: {e}")

        self.logger.info("Processed epics and tasks, updated stories and epics.")
        return stories_dict

    def assign_story(self, story: Story) -> bool:
        """Assign a story to a person using their email"""
        # Get the account ID from email
        user_info_url = f"https://ashwathyashwathy761.atlassian.net/rest/api/3/user/search?query={story.assignee}"
        user_response = requests.get(user_info_url, headers=self.headers)
        if user_response.status_code == 200 and user_response.json():
            account_id = user_response.json()[0]["accountId"]
        else:
            self.logger.info(
                f"Failed to retrieve account ID for {story.assignee}: {user_response.text}"
            )
            return False
        
        # Assign the issue
        assign_url = f"{self.JIRA_BASE_URL}/{story.issue_id}/assignee"
        payload = {"accountId": account_id}
        assign_response = requests.put(assign_url, headers=self.headers, json=payload)
        if assign_response.status_code == 204:
            self.logger.info(f"Successfully assigned {story.title} to {story.assignee}")
            return True
        else:
            self.logger.info(
                f"Failed to assign {story.issue_id}: {assign_response.text}"
            )
            return False

    def create_sprint(self, sprint: Sprint) -> bool:
        """Create sprint on Jira Board"""
        user_info_url = "https://ashwathyashwathy761.atlassian.net/rest/agile/1.0/sprint"
        payload = {
            "name": sprint.name,
            "startDate": sprint.startDate.isoformat(),
            "endDate": sprint.endDate.isoformat(),
            "originBoardId": "2"
        }

        response = requests.post(user_info_url, headers=self.headers, json=payload)

        if response.status_code == 201:
            response_data = response.json()
            if response_data and "id" in response_data:
                sprint.id = response_data["id"]
                return True
            else:
                self.logger.error(f"Unexpected response: {response_data}")
        else:
            self.logger.error(
                f"Failed to create sprint {sprint.name}, Response: {response.text}"
            )
        return False
    
    def assign_stories_to_sprint(self, sprint: Sprint) -> bool:
        """Assign all stories in a sprint to that sprint in Jira"""
        if not sprint.id:
            self.logger.error("Sprint ID is missing. Cannot assign stories.")
            return False

        success_count = 0
        total_stories = len(sprint.stories)

        for story in sprint.stories.values():
            issue_url = f"https://ashwathyashwathy761.atlassian.net/rest/api/2/issue/{story.issue_id}"
            payload = {
                "fields": {
                    "customfield_10020": sprint.id  # Sprint ID field in Jira
                }
            }

            response = requests.put(issue_url, headers=self.headers, json=payload)

            if response.status_code == 204:
                self.logger.info(f"Story {story.issue_id} assigned to Sprint {sprint.id}")
                success_count += 1
            else:
                self.logger.error(
                    f"Failed to assign Story {story.issue_id} to Sprint {sprint.id}, Response: {response.text}"
                )

        return success_count == total_stories