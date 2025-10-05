from langchain_core.prompts import PromptTemplate
from src.utils.chat_watsonx_llm import ChatLLMInstance
from src.models.graph_state import GraphState
from src.models.story_order import StoryOrder


PROMPT_TEMPLATE = PromptTemplate.from_template(
    "This is the name of the Project: {project_name}, this is its description: {project_description}.\
    Your job is to order the Stories in the sequence of their completion. Make sure you not what stories needs to be finished before what.\
    These are all the stories: {stories}. Return just the list of issue_id in the order of their required completion. \
        Take care of all the dependencies between the stories too "
)


class OrderStories:
    def __init__(self, chat_llm: ChatLLMInstance, logger):
        self.chat_llm = chat_llm
        self.logger = logger

    def order_stories(self, state: GraphState):
        story_list = [
            {
                "issue_id": key,
                "epic": story.epic,
                "title": story.title,
                "description": story.description,
            }
            for key, story in state["stories"].items()
        ]
        chain = self.get_chain()

        result = chain.invoke(
            input={
                "project_name": state["input"].project_name,
                "project_description": state["input"].project_desc,
                "stories": story_list,
            }
        )

        reordered_dict = {
            key: state["stories"][key] for key in result.stories if key in state["stories"]
        }

        return {"stories": reordered_dict, "next_node": "story_assignee"}

    def get_chain(self):
        entity_agent = PROMPT_TEMPLATE | self.chat_llm.with_structured_output(
            StoryOrder
        )
        return entity_agent
