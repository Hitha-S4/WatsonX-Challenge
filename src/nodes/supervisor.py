from datetime import datetime
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langgraph.types import Command

from src.utils.chat_watsonx_llm import ChatLLMInstance
from src.models.graph_state import GraphState


class Supervisor:
    def __init__(self, chat_llm: ChatLLMInstance, logger):
        self.chat_llm = chat_llm
        self.logger = logger

    def agent_manager(
        self, state: GraphState
    ) -> Command[Literal["order_stories", "story_assignee", "plan_next_sprint"]]:
        return Command(goto=state["next_node"])
