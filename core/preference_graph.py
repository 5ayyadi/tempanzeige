"""LangGraph workflow for preference extraction."""

import logging
from langgraph.graph import StateGraph, START, END

from llm.states import PreferenceState
from llm.nodes import extract_preference_node, confirm_preference_node

logger = logging.getLogger(__name__)

def route_next_action(state: PreferenceState) -> str:
    """Route to the next action based on state."""
    logger.info(f"Routing with state: next_action={state.next_action}, is_complete={state.is_complete}")
    
    if state.next_action == "extract":
        logger.info("Routing to: extract")
        return "extract"
    elif state.next_action == "confirm":
        logger.info("Routing to: confirm")
        return "confirm"
    elif state.next_action == "end" or state.is_complete:
        logger.info("Routing to: END")
        return END
    else:
        logger.info("Default routing to: END")
        return END

def create_preference_graph() -> StateGraph:
    """Create the preference extraction graph."""
    graph = StateGraph(PreferenceState)
    
    graph.add_node("extract", extract_preference_node)
    graph.add_node("confirm", confirm_preference_node)
    
    graph.add_edge(START, "extract")
    graph.add_conditional_edges("extract", route_next_action)
    graph.add_conditional_edges("confirm", route_next_action)
    
    return graph.compile()
