from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="APP_", env_file_encoding="utf-8", extra="ignore"
    )
    MODE: str = Field(default="Prod")
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    LOG_LEVEL: str = Field(default="INFO")
    FASTAPI_WORKERS: int = Field(default=10)
    WATSONX_API_ENDPOINT: str
    WATSONX_PROJECT_ID: str
    WATSONX_API_KEY: str
    JIRA_EMAIL: str
    JIRA_API_TOKEN: str
    CSV_PATH: str = Field(default="src/config/task_subtask_list.csv")
    EMPLOYEE_DATA: str = Field(default="src/config/team_data.csv")
