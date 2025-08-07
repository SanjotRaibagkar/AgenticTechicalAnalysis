# ================================================================
# src/langgraph_mcp_groq/server/tools/research_tools.py
from ...agents.research_agent import run_research_agent
import json


async def research_assistant(query: str) -> str:
    """Research assistant powered by LangGraph and Groq"""
    try:
        result = await run_research_agent(query)
        return json.dumps({
            "status": "success",
            "query": result["query"],
            "research_results": result["research_results"],
            "summary": result["summary"],
            "sources": result["sources"]
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e),
            "query": query
        }, indent=2)


RESEARCH_TOOLS = {
    "research_assistant": {
        "function": research_assistant,
        "description": "Research and analysis agent",
        "category": "Research"
    }
}
