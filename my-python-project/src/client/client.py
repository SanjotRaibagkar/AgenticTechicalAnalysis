import asyncio
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from utils.config import get_langchain_groq
from utils.config import settings

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent


mcp_server_host = "127.0.0.1"
mcp_server_port = 8000

mcp_url = f"http://{mcp_server_host}:{mcp_server_port}"
#self.mcp_url = f"http://127.0.0.1:800"

conversation_history = []
"GROQ_API_KEY"== ""


async def main():
    client=MultiServerMCPClient(
        {
        
            "chat_assistant": {
                "url": "http://localhost:8000/mcp",  # Ensure server is running here
                "transport": "streamable_http",
            }

        }
    )
    import os
    os.environ["GROQ_API_KEY"]=""
    tools = await client.get_tools()
    #print("Available tools:", tools)
    model =ChatGroq(model="llama3-8b-8192")
    agent = create_react_agent(
        model=model,
        tools=tools
        
    )

    research_response = await agent.ainvoke(
         {"messages": [{"role": "user", "content": "please chat with me on  usa"}]},
    )
    print("Research Response:", research_response)
asyncio.run(main())
