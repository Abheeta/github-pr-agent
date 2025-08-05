from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.tools import fetch_diff, analyze_code_diff


def fetch_diff_node(state: AgentState) -> AgentState:
    diff = fetch_diff.run(repo_url=state["repo_url"], pr_number=state["pr_number"])
    return {**state, "code_diff": diff}


def analyze_node(state: AgentState) -> AgentState:
    result = analyze_code_diff.run(code_diff=state["code_diff"])
    return {**state, "result": result}


# Build the graph
graph_builder = StateGraph(AgentState)

graph_builder.add_node("fetch_diff", fetch_diff_node)
graph_builder.add_node("analyze_code", analyze_node)

graph_builder.set_entry_point("fetch_diff")
graph_builder.add_edge("fetch_diff", "analyze_code")
graph_builder.add_edge("analyze_code", END)

graph = graph_builder.compile()
