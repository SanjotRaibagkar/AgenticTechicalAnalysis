import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from langgraph_mcp_groq.agents.research_agent import run_research_agent
from langgraph_mcp_groq.agents.coding_agent import run_coding_agent
from langgraph_mcp_groq.agents.chat_agent import run_chat_agent


@pytest.mark.asyncio
async def test_research_agent():
    """Test research agent basic functionality"""
    with patch('langgraph_mcp_groq.utils.config.get_langchain_groq') as mock_llm:
        mock_response = AsyncMock()
        mock_response.content = "Test research results"
        mock_llm.return_value.invoke.return_value = mock_response
        
        result = await run_research_agent("test query")
        
        assert result["query"] == "test query"
        assert "research_results" in result
        assert "summary" in result


@pytest.mark.asyncio
async def test_coding_agent():
    """Test coding agent basic functionality"""
    with patch('langgraph_mcp_groq.utils.config.get_langchain_groq') as mock_llm:
        mock_response = AsyncMock()
        mock_response.content = "def test(): pass"
        mock_llm.return_value.invoke.return_value = mock_response
        
        result = await run_coding_agent("create a test function", "Python")
        
        assert result["task"] == "create a test function"
        assert result["language"] == "Python"
        assert "code" in result


@pytest.mark.asyncio
async def test_chat_agent():
    """Test chat agent basic functionality"""
    with patch('langgraph_mcp_groq.utils.config.get_langchain_groq') as mock_llm:
        mock_response = AsyncMock()
        mock_response.content = "Hello! How can I help you?"
        mock_llm.return_value.invoke.return_value = mock_response
        
        result = await run_chat_agent("Hello")
        
        assert len(result["messages"]) == 2  # User + Assistant
        assert result["response"] == "Hello! How can I help you?"

