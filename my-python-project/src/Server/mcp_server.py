# src/langgraph_mcp_groq/server/mcp_server.py
import sys
sys.path.append("c:/sanjot/python/test/langgraph-mcp-groq")
import asyncio
from fastmcp import FastMCP
from .tools.registry import ALL_TOOLS
from ..utils.config import settings

# Create FastMCP server
mcp_server = FastMCP("LangGraph-Groq-MCP-Server")

# Register all tools dynamically
def register_tools():
    """Register all tools with the MCP server"""
    for tool_name, tool_info in ALL_TOOLS.items():
        # Register the tool function with mcp_server
        mcp_server.tool(name=tool_name)(tool_info["function"])
        print(f"✅ Registered tool: {tool_name} ({tool_info['category']})")

def main():
    """Main function to run the MCP server"""
    print(f"🚀 Starting LangGraph-Groq MCP Server on {settings.mcp_server_host}:{settings.mcp_server_port}")
    print(f"🤖 Using Groq model: {settings.default_model}")
    
    # Register all tools
    print("📡 Registering tools...")
    register_tools()
    
    print(f"✅ Registered {len(ALL_TOOLS)} tools across categories:")
    categories = set(tool["category"] for tool in ALL_TOOLS.values())
    for category in categories:
        tool_count = len([t for t in ALL_TOOLS.values() if t["category"] == category])
        print(f"   - {category}: {tool_count} tools")
    
    # Run the server
    # mcp_server.run(
    #     host=settings.mcp_server_host,
    #     port=settings.mcp_server_port
    # )

    print("🌐 MCP Server is running. Press Ctrl+C to stop." )
    mcp_server.run(transport="streamable-http")

if __name__ == "__main__":
    main()