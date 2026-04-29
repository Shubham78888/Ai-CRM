"""
LangGraph-based AI Agent for CRM Interactions
Manages HCP interaction workflows using state machines
"""

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from agent.tools import (
    log_interaction_tool,
    edit_interaction_tool,
    suggest_followup_tool,
    summarize_tool,
    fetch_history_tool,
    extract_sentiment,
    extract_action_items
)
import operator
from datetime import datetime


# ==================== STATE DEFINITION ====================

class AgentState(TypedDict):
    """State schema for CRM agent workflow"""
    input: str
    current_data: dict
    route: str
    result: dict
    interaction_id: int
    timestamp: str
    errors: Annotated[list, operator.add]


# ==================== ROUTER NODE ====================

def route_user_intent(state: AgentState) -> AgentState:
    """
    Intelligently route user input to appropriate tool
    Based on keywords and context
    Priority: edit > summary > history > suggest > log (default)
    """
    user_input = state["input"].lower()
    
    # 1. EDIT - user wants to modify existing data
    if any(word in user_input for word in ["edit", "modify", "update", "change"]):
        route = "edit"
    
    # 2. SUMMARY - user wants a summary
    elif any(word in user_input for word in ["summary", "summarize", "brief", "overview"]):
        route = "summarize"
    
    # 3. HISTORY - user wants past interactions
    elif any(word in user_input for word in ["history", "previous", "past", "before", "last time"]):
        route = "history"
    
    # 4. SUGGEST - user explicitly asking for suggestions/recommendations
    # Only if they explicitly ask, not if they're just describing an interaction
    elif any(word in user_input for word in ["suggest", "what should", "recommend me", "any suggestion", "what do you think", "next step"]):
        route = "suggest"
    
    # 5. LOG - Default for describing interactions (doctor name, products, recommendations, etc.)
    else:
        route = "log"
    
    return {**state, "route": route, "timestamp": datetime.now().isoformat()}


# ==================== TOOL NODES ====================

def log_interaction_node(state: AgentState) -> AgentState:
    """Execute log interaction tool"""
    try:
        result = log_interaction_tool(state["input"], state.get("current_data", {}))
        
        # Extract action items for enrichment (but preserve LLM sentiment)
        if "discussion_summary" in result and not result.get("sentiment"):
            # Only extract sentiment if LLM didn't provide one
            result["sentiment"] = extract_sentiment(result.get("discussion_summary", ""))
        
        if "discussion_summary" in result:
            result["action_items"] = extract_action_items(result.get("discussion_summary", ""))
        
        return {
            **state,
            "result": result,
            "interaction_id": result.get("db_id"),
            "current_data": result
        }
    except Exception as e:
        return {
            **state,
            "result": {"status": "error", "message": str(e)},
            "errors": [f"Log interaction error: {str(e)}"]
        }


def edit_interaction_node(state: AgentState) -> AgentState:
    """Execute edit interaction tool"""
    try:
        result = edit_interaction_tool(
            state["input"],
            state.get("current_data", {}),
            interaction_id=state.get("interaction_id")
        )
        
        return {
            **state,
            "result": result,
            "current_data": result
        }
    except Exception as e:
        return {
            **state,
            "result": {"status": "error", "message": str(e)},
            "errors": [f"Edit interaction error: {str(e)}"]
        }


def suggest_followup_node(state: AgentState) -> AgentState:
    """Execute suggest follow-up tool"""
    try:
        result = suggest_followup_tool(
            state["input"],
            state.get("current_data", {}).get("hcp_name", "")
        )
        
        return {
            **state,
            "result": result
        }
    except Exception as e:
        return {
            **state,
            "result": {"status": "error", "message": str(e)},
            "errors": [f"Follow-up suggestion error: {str(e)}"]
        }


def summarize_node(state: AgentState) -> AgentState:
    """Execute summarization tool"""
    try:
        result = summarize_tool(
            state["input"],
            products=state.get("current_data", {}).get("products_discussed", [])
        )
        
        return {
            **state,
            "result": result,
            "current_data": {**state.get("current_data", {}), **result}
        }
    except Exception as e:
        return {
            **state,
            "result": {"status": "error", "message": str(e)},
            "errors": [f"Summarization error: {str(e)}"]
        }


def history_node(state: AgentState) -> AgentState:
    """Execute history fetch tool"""
    try:
        # For history requests, ALWAYS prioritize extracting from user input
        # Don't use current_data.hcp_name because it might be from a different doctor
        import re
        
        hcp_name = ""
        
        # Try to extract from user input with improved regex
        # Match patterns like: "Dr. Patel", "Dr Patel", "doctor patel", "with patel"
        patterns = [
            r"(?:with|doctor|dr\.?)\s+([A-Za-z\s]+?)(?:\s+(?:the|a|and|or|but)|$)",
            r"(?:doctor|dr\.?|hcp|professional)\s+([A-Za-z\s]+?)(?:\s+(?:at|in|on)|$)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)"  # Fallback: capitalize patterns
        ]
        
        for pattern in patterns:
            match = re.search(pattern, state["input"], re.IGNORECASE)
            if match:
                hcp_name = match.group(1).strip()
                if hcp_name and hcp_name.lower() not in ["history", "me", "show", "the"]:
                    break
        
        # Fallback to current_data only if nothing extracted from input
        if not hcp_name:
            hcp_name = state.get("current_data", {}).get("hcp_name", "")
        
        # Clean up the extracted name
        if hcp_name:
            hcp_name = hcp_name.strip().title()
        else:
            hcp_name = "Default"
        
        result = fetch_history_tool(hcp_name)
        
        return {
            **state,
            "result": result
        }
    except Exception as e:
        return {
            **state,
            "result": {"status": "error", "message": str(e)},
            "errors": [f"History fetch error: {str(e)}"]
        }


# ==================== CONDITIONAL ROUTING ====================

def route_to_tool(state: AgentState) -> str:
    """Determine which tool node to execute based on route"""
    route_map = {
        "log": "log_tool",
        "edit": "edit_tool",
        "suggest": "suggest_tool",
        "summarize": "summarize_tool",
        "history": "history_tool"
    }
    return route_map.get(state["route"], "log_tool")


# ==================== GRAPH CONSTRUCTION ====================

def create_agent_graph():
    """Build the LangGraph state machine"""
    
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("router", route_user_intent)
    graph.add_node("log_tool", log_interaction_node)
    graph.add_node("edit_tool", edit_interaction_node)
    graph.add_node("suggest_tool", suggest_followup_node)
    graph.add_node("summarize_tool", summarize_node)
    graph.add_node("history_tool", history_node)
    
    # Add edges
    graph.add_edge(START, "router")
    graph.add_conditional_edges(
        "router",
        route_to_tool,
        {
            "log_tool": "log_tool",
            "edit_tool": "edit_tool",
            "suggest_tool": "suggest_tool",
            "summarize_tool": "summarize_tool",
            "history_tool": "history_tool"
        }
    )
    
    # All tools lead to end
    graph.add_edge("log_tool", END)
    graph.add_edge("edit_tool", END)
    graph.add_edge("suggest_tool", END)
    graph.add_edge("summarize_tool", END)
    graph.add_edge("history_tool", END)
    
    return graph.compile()


# ==================== AGENT EXECUTION ====================

# Compile the graph
agent_graph = create_agent_graph()


def run_agent(user_input: str, current_data: dict = None) -> dict:
    """
    Execute the LangGraph agent for CRM interactions
    
    Args:
        user_input: User's natural language input
        current_data: Current form/interaction data context
    
    Returns:
        Structured response from the appropriate tool
    """
    if current_data is None:
        current_data = {}
    
    # Initialize state
    initial_state: AgentState = {
        "input": user_input,
        "current_data": current_data,
        "route": "",
        "result": {},
        "interaction_id": 0,
        "timestamp": datetime.now().isoformat(),
        "errors": []
    }
    
    try:
        # Execute the graph
        final_state = agent_graph.invoke(initial_state)
        
        # Return the result with metadata
        response = {
            **final_state["result"],
            "agent_metadata": {
                "route": final_state["route"],
                "timestamp": final_state["timestamp"],
                "interaction_id": final_state.get("interaction_id"),
                "errors": final_state.get("errors", [])
            }
        }
        
        return response
    
    except Exception as e:
        print(f"Agent execution error: {e}")
        return {
            "status": "error",
            "message": f"Agent execution failed: {str(e)}",
            "agent_metadata": {
                "timestamp": datetime.now().isoformat(),
                "errors": [str(e)]
            }
        }