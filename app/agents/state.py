from typing import TypedDict


class AgentState(TypedDict):
    repo_url: str
    pr_number: int
    code_diff: str
    result: dict
