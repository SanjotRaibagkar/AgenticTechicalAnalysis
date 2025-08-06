# src/langgraph_mcp_groq/agents/chat_agent.py
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from utils.config import get_langchain_groq


class ChatState(TypedDict):
    messages: List[dict]
    current_message: str
    response: str
    conversation_summary: str


def create_chat_agent():
    """Create a conversational chat agent using LangGraph and Groq"""
    llm = get_langchain_groq()

    def chat_node(state: ChatState):
        """Main chat node that handles conversations"""
        system_prompt = """You are a helpful, knowledgeable, and friendly AI assistant. 
        Engage in natural conversation while being informative and helpful. 
        
        Guidelines:
        - Be conversational and engaging
        - Provide accurate and useful information
        - Ask follow-up questions when appropriate
        - Maintain context from previous messages
        - Be concise but thorough
        """
        
        # Convert message history to LangChain format
        chat_messages = [SystemMessage(content=system_prompt)]
        
        for msg in state.get("messages", []):
            if msg["role"] == "user":
                chat_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                chat_messages.append(AIMessage(content=msg["content"]))
        
        # Add current message
        chat_messages.append(HumanMessage(content=state["current_message"]))
        
        response = llm.invoke(chat_messages)
        print ("************************************************************88")
        print("Chat response:", response.content)
        # Update message history
        updated_messages = state.get("messages", [])
        updated_messages.append({"role": "user", "content": state["current_message"]})
        updated_messages.append({"role": "assistant", "content": response.content})
        
        return {
            "messages": updated_messages,
            "current_message": state["current_message"],
            "response": response.content,
            "conversation_summary": state.get("conversation_summary", "")
        }

    def summarize_conversation_node(state: ChatState):
        """Summarize the conversation periodically"""
        if len(state["messages"]) > 10:  # Summarize after 10+ messages
            system_prompt = """Summarize this conversation concisely. 
            Focus on key topics discussed and important information shared."""
            
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in state["messages"][-10:]  # Last 10 messages
            ])
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Conversation to summarize:\n{conversation_text}")
            ]
            
            summary_response = llm.invoke(messages)
            
            return {
                **state,
                "conversation_summary": summary_response.content
            }
        
        return state

    # Build the graph
    workflow = StateGraph(ChatState)
    
    # Add nodes
    workflow.add_node("chat", chat_node)
    workflow.add_node("summarize", summarize_conversation_node)
    
    # Add edges
    workflow.set_entry_point("chat")
    workflow.add_edge("chat", "summarize")
    workflow.add_edge("summarize", END)
    
    return workflow.compile()


# Create the chat agent instance
chat_agent = create_chat_agent()


async def run_chat_agent(message: str, conversation_history: List[dict] = None) -> dict:
    """Run chat agent with given message and history"""
    try:
        result = await chat_agent.ainvoke({
            "messages": conversation_history or [],
            "current_message": message,
            "response": "",
            "conversation_summary": ""
        })
        return result
    except Exception as e:
        return {
            "messages": conversation_history or [],
            "current_message": message,
            "response": f"Error in chat: {str(e)}",
            "conversation_summary": ""
        }