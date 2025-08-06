# src/langgraph_mcp_groq/agents/coding_agent.py
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain.schema import HumanMessage, SystemMessage
from utils.config import get_langchain_groq


class CodingState(TypedDict):
    task: str
    language: str
    code: str
    explanation: str
    tests: str
    review: str


def create_coding_agent():
    """Create a coding agent using LangGraph and Groq"""
    llm = get_langchain_groq()

    def code_generation_node(state: CodingState):
        """Generate code based on the task"""
        system_prompt = f"""You are an expert programmer. Generate high-quality code for the given task.
        Language: {state.get('language', 'Python')}
        
        Provide:
        1. Clean, well-commented code
        2. Follow best practices
        3. Include error handling where appropriate
        4. Make code production-ready
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Task: {state['task']}")
        ]
        
        response = llm.invoke(messages)
        
        return {
            **state,
            "code": response.content
        }

    def explanation_node(state: CodingState):
        """Explain the generated code"""
        system_prompt = """Explain the code in simple terms. Cover:
        1. What the code does
        2. How it works
        3. Key components and their purpose
        4. Usage instructions
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Explain this code:\n\n{state['code']}")
        ]
        
        response = llm.invoke(messages)
        
        return {
            **state,
            "explanation": response.content
        }

    def test_generation_node(state: CodingState):
        """Generate tests for the code"""
        system_prompt = f"""Generate comprehensive tests for the provided code.
        Language: {state.get('language', 'Python')}
        
        Include:
        1. Unit tests
        2. Edge cases
        3. Error handling tests
        4. Integration tests if applicable
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Generate tests for:\n\n{state['code']}")
        ]
        
        response = llm.invoke(messages)
        
        return {
            **state,
            "tests": response.content
        }

    def code_review_node(state: CodingState):
        """Review the generated code"""
        system_prompt = """Review the code for:
        1. Code quality
        2. Best practices
        3. Potential improvements
        4. Security considerations
        5. Performance optimizations
        
        Provide constructive feedback and suggestions."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Review this code:\n\n{state['code']}")
        ]
        
        response = llm.invoke(messages)
        
        return {
            **state,
            "review": response.content
        }

    # Build the graph
    workflow = StateGraph(CodingState)
    
    # Add nodes
    workflow.add_node("generate_code", code_generation_node)
    workflow.add_node("explain", explanation_node)
    workflow.add_node("generate_tests", test_generation_node)
    workflow.add_node("review", code_review_node)
    
    # Add edges
    workflow.set_entry_point("generate_code")
    workflow.add_edge("generate_code", "explain")
    workflow.add_edge("explain", "generate_tests")
    workflow.add_edge("generate_tests", "review")
    workflow.add_edge("review", END)
    
    return workflow.compile()


# Create the coding agent instance
coding_agent = create_coding_agent()


async def run_coding_agent(task: str, language: str = "Python") -> dict:
    """Run coding agent with given task"""
    try:
        result = await coding_agent.ainvoke({
            "task": task,
            "language": language,
            "code": "",
            "explanation": "",
            "tests": "",
            "review": ""
        })
        return result
    except Exception as e:
        return {
            "task": task,
            "language": language,
            "code": f"Error generating code: {str(e)}",
            "explanation": "",
            "tests": "",
            "review": f"Code generation failed: {str(e)}"
        }