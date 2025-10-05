import base64

from src.models.project_planner_request import ProjectPlannerRequest
from src.utils.watsonx_llm import LLMInstance
from src.utils.chat_watsonx_llm import ChatLLMInstance


class ProjectPlannerService:
    def __init__(self, graph_app, settings):
        self.graph_app = graph_app
        self.settings = settings
        self.llm_manager = LLMInstance(
            settings=self.settings, model_id="meta-llama/llama-3-405b-instruct"
        )
        self.chat_llm_manager = ChatLLMInstance(
            settings=self.settings, model_id="meta-llama/llama-3-3-70b-instruct"
        )

    async def invoke(self, request: ProjectPlannerRequest):
        result = self.graph_app.invoke(input = {"input": request})
        return result

    def get_graph(self):
        image_stream = self.graph_app.get_graph(xray=True).draw_mermaid_png()

        image_base64 = base64.b64encode(image_stream).decode("utf-8")

        # Return the image in an HTML page
        html_content = f"""
        <html>
            <body>
                <img src="data:image/png;base64,{image_base64}" alt="Graph">
            </body>
        </html>
        """
        return html_content
