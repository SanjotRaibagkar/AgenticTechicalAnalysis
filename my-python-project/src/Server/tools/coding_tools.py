# src/langgraph_mcp_groq/server/tools/coding_tools.py
from ...agents.coding_agent import run_coding_agent
import json


async def coding_assistant(task: str, language: str = "Python") -> str:
    """Coding assistant powered by LangGraph and Groq"""
    try:
        result = await run_coding_agent(task, language)
        return json.dumps({
            "status": "success",
            "task": result["task"],
            "language": result["language"],
            "code": result["code"],
            "explanation": result["explanation"],
            "tests": result["tests"],
            "review": result["review"]
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e),
            "task": task,
            "language": language
        }, indent=2)


CODING_TOOLS = {
    "coding_assistant": {
        "function": coding_assistant,
        "description": "Code generation and review agent",
        "category": "Coding"
    }
}

