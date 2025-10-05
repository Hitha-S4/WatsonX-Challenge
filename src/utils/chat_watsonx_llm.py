"""Class for WatsonX LLM"""

import os
from langchain_ibm import ChatWatsonx
from src.settings.app_settings import AppSettings


class ChatLLMInstance:
    """WatsonX LLM"""

    def __init__(self, settings: AppSettings, model_id):
        self.settings = settings
        self.model_id = model_id
        self.params = {
            "decoding_method": "greedy",
            "temperature": 0,
            "min_new_tokens": 5,
            "max_new_tokens": 250,
            "stop_sequences": ["\nObservation", "\n\n"],
        }

    def get_llm(self):
        """Get LLM"""
        llm = ChatWatsonx(
            apikey=self.settings.WATSONX_API_KEY,
            params=self.params,
            model_id=self.model_id,
            url=self.settings.WATSONX_API_ENDPOINT,
            project_id=self.settings.WATSONX_PROJECT_ID,
        )

        return llm
