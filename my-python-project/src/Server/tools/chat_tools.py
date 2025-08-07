# src/langgraph_mcp_groq/server/tools/chat_tools.py
from ...agents.chat_agent import run_chat_agent
import json
from typing import List, Dict

# Store conversation histories for chat agent
conversation_store: Dict[str, List[dict]] = {}


async def chat_assistant(message: str, session_id: str = "default") -> str:
    """Chat assistant powered by LangGraph and Groq"""
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


async def clear_conversation(session_id: str = "default") -> str:
    """Clear conversation history for a specific session"""
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


async def list_sessions() -> str:
    """List all active conversation sessions"""
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


CHAT_TOOLS = {
    "chat_assistant": {
        "function": chat_assistant,
        "description": "Conversational AI agent",
        "category": "Chat"
    },
    "clear_conversation": {
        "function": clear_conversation,
        "description": "Clear chat history",
        "category": "Chat"
    },
    "list_sessions": {
        "function": list_sessions,
        "description": "List active chat sessions",
        "category": "Chat"
    }
}
