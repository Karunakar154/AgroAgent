from langgraph.graph import StateGraph, START, END

from backend.agent.state import AgroAgentState

from backend.agent.nodes import (
    planner_node,
    tool_node,
    verifier_node,
    response_node,
    review_node,
    retry_agent_node
)

from backend.agent.decision import verification_decision


# Create graph
builder = StateGraph(AgroAgentState)


# ==============================
# Add Nodes
# ==============================

builder.add_node(
    "planner",
    planner_node
)

builder.add_node(
    "tools",
    tool_node
)

builder.add_node(
    "verifier",
    verifier_node
)

builder.add_node(
    "response",
    response_node
)

builder.add_node(
    "review",
    review_node
)

builder.add_node(
    "retry",
    retry_agent_node
)


# ==============================
# Connect Graph
# ==============================

builder.add_edge(
    START,
    "planner"
)

builder.add_edge(
    "planner",
    "tools"
)

builder.add_edge(
    "tools",
    "verifier"
)


# ==============================
# Verification Decision
# ==============================

builder.add_conditional_edges(
    "verifier",
    verification_decision,
    {
        "response": "response",
        "review": "review"
    }
)


# ==============================
# Response → END
# ==============================

builder.add_edge(
    "response",
    END
)


# ==============================
# Review → Retry
# ==============================

builder.add_edge(
    "review",
    "retry"
)


# ==============================
# Retry → Planner
# ==============================

builder.add_edge(
    "retry",
    "planner"
)


# ==============================
# Compile Graph
# ==============================

agro_agent = builder.compile()