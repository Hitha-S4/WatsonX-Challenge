"""Router """

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from src.models.project_planner_request import ProjectPlannerRequest

from src.services.project_planner import ProjectPlannerService


class AppInvoke:
    """Agent LLM Router"""

    def __init__(self, service: ProjectPlannerService) -> None:
        self.service = service
        self.router = APIRouter()

        self.router.add_api_route(
            path="/invoke",
            methods=["Post"],
            endpoint=self.invoke,
            summary="Invoke Flight Search Agent App",
        )
        self.router.add_api_route(
            path="/graph",
            methods=["Get"],
            endpoint=self.get_graph,
            summary="get graph",
            response_class=HTMLResponse,
        )

    async def invoke(self, request: ProjectPlannerRequest):
        """invoke"""
        # response = await self.service.invoke(request=request)
        # return response["response"]

        return await self.service.invoke(request=request)

    async def get_graph(self):
        """get graph"""

        return self.service.get_graph()
