# src/langgraph_mcp_groq/agents/research_agent.py
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain.schema import HumanMessage, SystemMessage
from utils.config import get_langchain_groq


class ResearchState(TypedDict):
    query: str
    research_results: str
    sources: List[str]
    summary: str


def create_research_agent():
    """Create a research agent using LangGraph and Groq"""
    llm = get_langchain_groq()

    def research_node(state: ResearchState):
        """Research node that analyzes queries and provides insights"""
        system_prompt = """You are a research assistant. Given a query, provide:
        1. Comprehensive analysis of the topic
        2. Key insights and findings
        3. Potential sources or areas for further research
        
        Be thorough but concise. Focus on accuracy and relevance."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Research query: {state['query']}")
        ]
        #print("****************************************************************************************")
        
        response = llm.invoke(messages)
        #print("Research response:", response.content)

        #print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&7777777777")
        return {
            "query": state["query"],
            "research_results": response.content,
            "sources": ["Groq LLM Analysis", "Knowledge Base"],
            "summary": response.content[:200] + "..." if len(response.content) > 200 else response.content
        }

    def summarize_node(state: ResearchState):
        """Summarize research findings"""
        system_prompt = """Create a concise summary of the research findings. 
        Focus on the most important points and actionable insights."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Summarize this research: {state['research_results']}")
        ]
        
        response = llm.invoke(messages)
        
        return {
            **state,
            "summary": response.content
        }

    # Build the graph
    workflow = StateGraph(ResearchState)
    
    # Add nodes
    workflow.add_node("research", research_node)
    workflow.add_node("summarize", summarize_node)
    
    # Add edges
    workflow.set_entry_point("research")
    workflow.add_edge("research", "summarize")
    workflow.add_edge("summarize", END)
    
    return workflow.compile()


# Create the research agent instance
research_agent = create_research_agent()


async def run_research_agent(query: str) -> dict:
    """Run research agent with given query"""
    try:
        result = await research_agent.ainvoke({
            "query": query,
            "research_results": "",
            "sources": [],
            "summary": ""
        })
        return result
    except Exception as e:
        return {
            "query": query,
            "research_results": f"Error during research: {str(e)}",
            "sources": [],
            "summary": f"Research failed: {str(e)}"
        }