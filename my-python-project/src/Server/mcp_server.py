# src/langgraph_mcp_groq/server/mcp_server.py
import sys
sys.path.append("c:/sanjot/python/test/langgraph-mcp-groq")
import asyncio
import json
from typing import List, Dict, Any
from fastmcp import FastMCP
from agents.research_agent import run_research_agent
from agents.coding_agent import run_coding_agent
from agents.chat_agent import run_chat_agent
from utils.config import get_langchain_groq, settings



# Create FastMCP server
mcp_server = FastMCP("LangGraph-Groq-MCP-Server")

# Store conversation histories for chat agent
conversation_store: Dict[str, List[dict]] = {}


@mcp_server.tool()
async def research_assistant(query: str) -> str:
    """
    Research assistant powered by LangGraph and Groq.
    Provides comprehensive research and analysis on any topic.
    
    Args:
        query: The research question or topic to investigate
        
    Returns:
        JSON string with research results, summary, and sources
    """
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


@mcp_server.tool()
async def coding_assistant(task: str, language: str = "Python") -> str:
    """
    Coding assistant powered by LangGraph and Groq.
    Generates code, explanations, tests, and reviews.
    
    Args:
        task: Description of the coding task
        language: Programming language (default: Python)
        
    Returns:
        JSON string with generated code, explanation, tests, and review
    """
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


@mcp_server.tool()
async def chat_assistant(message: str, session_id: str = "default") -> str:
    """
    Chat assistant powered by LangGraph and Groq.
    Maintains conversation history and provides contextual responses.
    
    Args:
        message: User message
        session_id: Session identifier to maintain conversation history
        
    Returns:
        JSON string with response and conversation context
    """
    try:
        # Get conversation history for this session
        conversation_history = conversation_store.get(session_id, [])
        
        # Run chat agent
        result = await run_chat_agent(message, conversation_history)
        
        # Update conversation store
        conversation_store[session_id] = result["messages"]
        
        return json.dumps({
            "status": "success",
            "response": result["response"],
            "session_id": session_id,
            "message_count": len(result["messages"]),
            "conversation_summary": result.get("conversation_summary", "")
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e),
            "message": message,
            "session_id": session_id
        }, indent=2)


@mcp_server.tool()
async def clear_conversation(session_id: str = "default") -> str:
    """
    Clear conversation history for a specific session.
    
    Args:
        session_id: Session identifier to clear
        
    Returns:
        Confirmation message
    """
    try:
        if session_id in conversation_store:
            del conversation_store[session_id]
            return json.dumps({
                "status": "success",
                "message": f"Conversation history cleared for session: {session_id}"
            })
        else:
            return json.dumps({
                "status": "info",
                "message": f"No conversation history found for session: {session_id}"
            })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        })


@mcp_server.tool()
async def list_sessions() -> str:
    """
    List all active conversation sessions.
    
    Returns:
        JSON string with list of active sessions and their message counts
    """
    try:
        sessions = {
            session_id: len(messages) 
            for session_id, messages in conversation_store.items()
        }
        return json.dumps({
            "status": "success",
            "active_sessions": sessions,
            "total_sessions": len(sessions)
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        })


@mcp_server.tool()
async def agent_status() -> str:
    """
    Get status information about all available agents.
    
    Returns:
        JSON string with agent information and server status
    """
    try:
        return json.dumps({
            "status": "success",
            "server": "LangGraph-Groq-MCP-Server",
            "agents": {
                "research_assistant": {
                    "description": "Research and analysis agent",
                    "capabilities": ["research", "analysis", "summarization"]
                },
                "coding_assistant": {
                    "description": "Code generation and review agent",
                    "capabilities": ["code_generation", "explanation", "testing", "review"]
                },
                "chat_assistant": {
                    "description": "Conversational AI agent",
                    "capabilities": ["conversation", "context_awareness", "multi_turn"]
                }
            },
            "llm_model": settings.default_model,
            "active_sessions": len(conversation_store)
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        })
@mcp_server.tool()
async def get_weather(location:str)->str:
    """Get the weather location."""
    return "It's always raining in California"

def main():
    """Main function to run the MCP server"""
    print(f"🚀 Starting LangGraph-Groq MCP Server on {settings.mcp_server_host}:{settings.mcp_server_port}")
    print(f"🤖 Using Groq model: {settings.default_model}")
    print("📡 Available tools:")
    print("   - research_assistant: Research and analysis")
    print("   - coding_assistant: Code generation and review")
    print("   - chat_assistant: Conversational AI")
    print("   - clear_conversation: Clear chat history")
    print("   - list_sessions: List active sessions")
    print("   - agent_status: Get server status")
    
    # Run the server
    # mcp_server.run(
    #     host=settings.mcp_server_host,
    #     port=settings.mcp_server_port
    # )
    mcp_server.run(transport="streamable-http")

if __name__ == "__main__":
    main()