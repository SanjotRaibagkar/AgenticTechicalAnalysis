# src/langgraph_mcp_groq/server/tools/registry.py
"""
Tool Registry for clean tool management
"""
from .video_tools import VIDEO_TOOLS
from .research_tools import RESEARCH_TOOLS
from .coding_tools import CODING_TOOLS
from .chat_tools import CHAT_TOOLS
from ..utils.config import settings
import json


async def agent_status() -> str:
    """Get status information about all available agents"""
    try:
        all_tools = {**VIDEO_TOOLS, **RESEARCH_TOOLS, **CODING_TOOLS, **CHAT_TOOLS}
        
        agents_info = {}
        for tool_name, tool_info in all_tools.items():
            agents_info[tool_name] = {
                "description": tool_info["description"],
                "category": tool_info["category"]
            }
        
        # Special handling for video tools
        if "video_strategy_analyzer" in agents_info:
            agents_info["video_strategy_analyzer"]["capabilities"] = [
                "video_transcription", "visual_analysis", "strategy_extraction",
                "actionable_insights", "document_generation", "implementation_recommendations"
            ]
            agents_info["video_strategy_analyzer"]["supported_formats"] = [
                ".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"
            ]
        
        return json.dumps({
            "status": "success",
            "server": "LangGraph-Groq-MCP-Server",
            "agents": agents_info,
            "llm_model": settings.default_model,
            "total_tools": len(all_tools),
            "categories": list(set(tool["category"] for tool in all_tools.values()))
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        })


# Combine all tools
ALL_TOOLS = {
    **VIDEO_TOOLS,
    **RESEARCH_TOOLS, 
    **CODING_TOOLS,
    **CHAT_TOOLS,
    "agent_status": {
        "function": agent_status,
        "description": "Get server status and agent information",
        "category": "System"
    }
}
