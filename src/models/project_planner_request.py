from pydantic import BaseModel


class ProjectPlannerRequest(BaseModel):
    project_name: str
    project_desc: str
    csv_path: str
