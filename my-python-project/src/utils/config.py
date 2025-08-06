import os
from typing import Optional
from dotenv import load_dotenv
#from pydantic import BaseSettings
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv("config/settings.env")


class Settings(BaseSettings):
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    mcp_server_host: str = os.getenv("MCP_SERVER_HOST", "localhost")
    mcp_server_port: int = int(os.getenv("MCP_SERVER_PORT", "8000"))
    default_model: str = os.getenv("DEFAULT_MODEL", "lllama3-8b-8192")
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    max_tokens: int = int(os.getenv("MAX_TOKENS", "4096"))

    class Config:
        env_file = "config/settings.env"


# Global settings instance
settings = Settings()


def get_groq_client():
    """Get configured Groq client"""
    from groq import Groq
    return Groq(api_key=settings.groq_api_key)


def get_langchain_groq():
    """Get LangChain Groq LLM"""
    from langchain_groq import ChatGroq
    #os.environ["GROQ_API_KEY"]=""
    return ChatGroq(
        groq_api_key="",
        model_name="llama3-8b-8192",
        #temperature=settings.temperature,
        #max_tokens=settings.max_tokens,
    )