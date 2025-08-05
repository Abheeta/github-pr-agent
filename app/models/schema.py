from pydantic import BaseModel, HttpUrl


class AnalyzePRRequest(BaseModel):
    repo_url: str
    pr_number: int


class AnalyzePRResponse(BaseModel):
    task_id: str


class StatusResponse(BaseModel):
    task_id: str
    status: str
    result: dict | None = None
    error: str | None = None
