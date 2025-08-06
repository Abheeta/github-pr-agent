from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class AnalyzePRRequest(BaseModel):
    repo_url: str
    pr_number: int
    github_token: Optional[str] = None
    


class AnalyzePRResponse(BaseModel):
    task_id: str


class Issue(BaseModel):
    type: str
    line: int
    description: str
    suggestion: str


class File(BaseModel):
    name: str
    issues: List[Issue]


class Summary(BaseModel):
    total_files: int
    total_issues: int
    critical_issues: int


class Results(BaseModel):
    files: List[File]
    summary: Summary


class StatusResponse(BaseModel):
    task_id: str
    status: str

class ResultsResponse(BaseModel):
    task_id: str
    status: str
    results: Optional[Results] = None
    error: Optional[str] = None
