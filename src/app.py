import asyncio
import logging

from fastapi import FastAPI
# from opensearchpy import AsyncOpenSearch, OpenSearch
import uvicorn

from src.settings.app_settings import AppSettings
from src.orchestrators.graph import ProjectPlannerGraph
from src.routers.app_invoke import AppInvoke
from src.services.project_planner import ProjectPlannerService
from src.models.graph_state import GraphState


class ProjectPlannerApp:

    def __init__(self, settings: AppSettings) -> None:
        self.logger = logging.getLogger(__name__)
        self.settings = settings
        self.graph_manager = ProjectPlannerGraph(model=GraphState, settings=self.settings, logger = self.logger)
        self.graph = self.graph_manager.create_graph()

        self.app_orchestration = ProjectPlannerService(graph_app=self.graph, settings=self.settings)

        self.app_invoke_router = AppInvoke(service=self.app_orchestration)

        # self.os_client = self.get_os_client()
        # self.async_os_client = self.get_async_os_client()

        self.rest_app = self._create_rest_app()
        self.rest_server = self._create_rest_server()

    def _create_rest_app(self):
        app = FastAPI()
        # app.add_middleware(
        #     CORSMiddleware,
        #     allow_origins=["*"],
        #     allow_credentials=True,
        #     allow_methods=["*"],
        #     allow_headers=["*"],
        # )
        app.include_router(router=self.app_invoke_router.router)


        return app

    # def create_os_connection(self):
    #     """Create an Opensearch client"""
    #     os_client = OpenSearch(
    #         hosts=[
    #             {
    #                 "host": self.settings.DB_HOST,
    #                 "port": self.settings.DB_PORT,
    #             }
    #         ],
    #         http_compress=True,
    #         http_auth=(
    #             self.settings.DB_USERNAME,
    #             self.settings.DB_PASSWORD,
    #         ),
    #         use_ssl=self.settings.DB_SSL,
    #         verify_certs=False,
    #         ssl_assert_hostname=False,
    #         ssl_show_warn=False,
    #         pool_maxsize=self.settings.DB_POOL_SIZE,
    #     )
    #     return os_client

    # def create_async_os_connection(self):
    #     """Create an Opensearch client"""
    #     os_client = AsyncOpenSearch(
    #         hosts=[
    #             {
    #                 "host": self.settings.DB_HOST,
    #                 "port": self.settings.DB_PORT,
    #             }
    #         ],
    #         http_compress=True,
    #         http_auth=(
    #             self.settings.DB_USERNAME,
    #             self.settings.DB_PASSWORD,
    #         ),
    #         use_ssl=self.settings.DB_SSL,
    #         verify_certs=False,
    #         ssl_assert_hostname=False,
    #         ssl_show_warn=False,
    #         maxsize=self.settings.DB_POOL_SIZE,
    #     )
    #     return os_client

    # def get_os_client(self):
    #     try:
    #         os_client = self.create_os_connection()
    #         return os_client
    #     except Exception as e:
    #         self.logger.error(f"Unable to establish connection to OpenSearch: {str(e)}")
    #         raise e

    # def get_async_os_client(self):
    #     try:
    #         async_os_client = self.create_async_os_connection()
    #         return async_os_client
    #     except Exception as e:
    #         self.logger.error(
    #             f"Unable to establish connection to AsyncOpenSearch: {str(e)}"
    #         )
    #         raise e

    async def run(self):
        asyncio.create_task(self._start_http_server())

    async def stop(self):
        """stop stops the app"""
        await self.rest_server.shutdown()
        # await self.async_os_client.close()
        # self.os_client.close()

    async def _start_http_server(self):
        await self.rest_server.serve()

    def _create_rest_server(self):
        uvicorn_config = self._server_config()
        return uvicorn.Server(uvicorn_config)

    def _server_config(self):
        config = uvicorn.Config(
            app=self.rest_app,
            host=self.settings.HOST,
            port=self.settings.PORT,
            log_config=None,
            use_colors=False,
            log_level=self.settings.LOG_LEVEL.lower(),
            ssl_version=5,
            workers=self.settings.FASTAPI_WORKERS,
        )
        return config