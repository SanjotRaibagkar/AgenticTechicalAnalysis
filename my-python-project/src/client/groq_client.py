# src/langgraph_mcp_groq/client/groq_client.py
import asyncio
import json
import uuid
from typing import Dict, Any
import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.prompt import Prompt
import httpx
from ..utils.config import settings, get_groq_client

console = Console()


class GroqMCPClient:
    """Groq-powered client for interacting with MCP server"""
    
    def __init__(self):
        self.groq_client = get_groq_client()
        self.mcp_url = f"http://{settings.mcp_server_host}:{settings.mcp_server_port}"
        self.session_id = str(uuid.uuid4())
        self.conversation_history = []
    
    async def call_mcp_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.mcp_url}/tools/{tool_name}",
                    json=kwargs,
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def groq_enhanced_query(self, user_input: str) -> str:
        """Use Groq to enhance user queries and determine best agent"""
        system_prompt = """You are a query router and enhancer. Given a user input, determine:

1. Which agent would be best suited (research_assistant, coding_assistant, or chat_assistant)
2. Enhance the query to be more specific and actionable
3. Return a JSON response with:
   - "agent": the best agent to use
   - "enhanced_query": improved version of the query
   - "reasoning": why you chose this agent

Available agents:
- research_assistant: For research, analysis, information gathering
- coding_assistant: For programming tasks, code generation, technical problems
- chat_assistant: For general conversation, questions, casual interactions"""

        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                model=settings.default_model,
                temperature=0.3,
                max_tokens=500
            )
            
            # Try to parse JSON response
            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "agent": "chat_assistant",
                    "enhanced_query": user_input,
                    "reasoning": "Defaulting to chat agent due to parsing error"
                }
        except Exception as e:
            return {
                "agent": "chat_assistant", 
                "enhanced_query": user_input,
                "reasoning": f"Error with Groq routing: {str(e)}"
            }
    
    async def research_mode(self):
        """Interactive research mode"""
        console.print(Panel("🔬 Research Assistant Mode", style="blue bold"))
        console.print("Ask research questions. Type 'back' to return to main menu.\n")
        
        while True:
            query = Prompt.ask("Research query")
            if query.lower() == 'back':
                break
            
            console.print("🔍 Researching...", style="yellow")
            result = await self.call_mcp_tool("research_assistant", query=query)
            
            if "error" in result:
                console.print(f"❌ Error: {result['error']}", style="red")
            else:
                try:
                    data = json.loads(result.get("result", "{}"))
                    if data.get("status") == "success":
                        console.print(Panel(
                            Markdown(data["research_results"]),
                            title=f"Research Results: {data['query']}",
                            style="green"
                        ))
                        console.print(Panel(
                            data["summary"],
                            title="Summary",
                            style="blue"
                        ))
                    else:
                        console.print(f"❌ Research failed: {data.get('error', 'Unknown error')}", style="red")
                except json.JSONDecodeError:
                    console.print(f"📄 Raw result: {result}", style="yellow")
            
            console.print()
    
    async def coding_mode(self):
        """Interactive coding mode"""
        console.print(Panel("💻 Coding Assistant Mode", style="green bold"))
        console.print("Describe coding tasks. Type 'back' to return to main menu.\n")
        
        while True:
            task = Prompt.ask("Coding task")
            if task.lower() == 'back':
                break
            
            language = Prompt.ask("Programming language", default="Python")
            
            console.print("⚡ Generating code...", style="yellow")
            result = await self.call_mcp_tool("coding_assistant", task=task, language=language)
            
            if "error" in result:
                console.print(f"❌ Error: {result['error']}", style="red")
            else:
                try:
                    data = json.loads(result.get("result", "{}"))
                    if data.get("status") == "success":
                        # Display code
                        console.print(Panel(
                            Syntax(data["code"], language.lower(), theme="monokai"),
                            title=f"Generated Code - {data['task']}",
                            style="green"
                        ))
                        
                        # Display explanation
                        console.print(Panel(
                            Markdown(data["explanation"]),
                            title="Code Explanation",
                            style="blue"
                        ))
                        
                        # Ask if user wants to see tests and review
                        show_more = Prompt.ask("Show tests and review? (y/n)", default="y")
                        if show_more.lower() == 'y':
                            console.print(Panel(
                                Syntax(data["tests"], language.lower(), theme="monokai"),
                                title="Generated Tests",
                                style="cyan"
                            ))
                            console.print(Panel(
                                Markdown(data["review"]),
                                title="Code Review",
                                style="magenta"
                            ))
                    else:
                        console.print(f"❌ Coding failed: {data.get('error', 'Unknown error')}", style="red")
                except json.JSONDecodeError:
                    console.print(f"📄 Raw result: {result}", style="yellow")
            
            console.print()
    
    async def chat_mode(self):
        """Interactive chat mode"""
        console.print(Panel("💬 Chat Assistant Mode", style="cyan bold"))
        console.print(f"Session ID: {self.session_id}")
        console.print("Start chatting! Type 'back' to return to main menu.\n")
        
        while True:
            message = Prompt.ask("You")
            if message.lower() == 'back':
                break
            
            console.print("🤖 Thinking...", style="yellow")
            result = await self.call_mcp_tool("chat_assistant", message=message, session_id=self.session_id)
            
            if "error" in result:
                console.print(f"❌ Error: {result['error']}", style="red")
            else:
                try:
                    data = json.loads(result.get("result", "{}"))
                    if data.get("status") == "success":
                        console.print(Panel(
                            Markdown(data["response"]),
                            title="Assistant",
                            style="green"
                        ))
                        
                        # Show conversation summary if available
                        if data.get("conversation_summary"):
                            console.print(f"💭 Conversation summary: {data['conversation_summary']}", style="dim")
                    else:
                        console.print(f"❌ Chat failed: {data.get('error', 'Unknown error')}", style="red")
                except json.JSONDecodeError:
                    console.print(f"📄 Raw result: {result}", style="yellow")
            
            console.print()
    
    async def smart_mode(self):
        """Smart mode - uses Groq to route queries to best agent"""
        console.print(Panel("🧠 Smart Assistant Mode", style="magenta bold"))
        console.print("Ask anything! I'll route your query to the best agent.\n")
        console.print("Type 'back' to return to main menu.\n")
        
        while True:
            user_input = Prompt.ask("Ask anything")
            if user_input.lower() == 'back':
                break
            
            # Use Groq to enhance and route the query
            console.print("🧠 Analyzing your request...", style="yellow")
            routing_info = await self.groq_enhanced_query(user_input)
            
            agent = routing_info.get("agent", "chat_assistant")
            enhanced_query = routing_info.get("enhanced_query", user_input)
            reasoning = routing_info.get("reasoning", "No reasoning provided")
            
            console.print(f"🎯 Routing to: {agent}", style="blue")
            console.print(f"💡 Reasoning: {reasoning}", style="dim")
            console.print(f"📝 Enhanced query: {enhanced_query}", style="dim")
            console.print()
            
            # Call the appropriate agent
            if agent == "research_assistant":
                result = await self.call_mcp_tool("research_assistant", query=enhanced_query)
            elif agent == "coding_assistant":
                # For coding, try to extract language from enhanced query
                language = "Python"  # Default
                if any(lang in enhanced_query.lower() for lang in ["javascript", "js"]):
                    language = "JavaScript"
                elif any(lang in enhanced_query.lower() for lang in ["java"]):
                    language = "Java"
                elif any(lang in enhanced_query.lower() for lang in ["cpp", "c++"]):
                    language = "C++"
                
                result = await self.call_mcp_tool("coding_assistant", task=enhanced_query, language=language)
            else:
                result = await self.call_mcp_tool("chat_assistant", message=enhanced_query, session_id=self.session_id)
            
            # Display results based on agent type
            if "error" in result:
                console.print(f"❌ Error: {result['error']}", style="red")
            else:
                await self._display_agent_result(agent, result)
            
            console.print()
    
    async def _display_agent_result(self, agent: str, result: Dict[str, Any]):
        """Display results based on agent type"""
        try:
            data = json.loads(result.get("result", "{}"))
            if data.get("status") != "success":
                console.print(f"❌ Failed: {data.get('error', 'Unknown error')}", style="red")
                return
            
            if agent == "research_assistant":
                console.print(Panel(
                    Markdown(data["research_results"]),
                    title="Research Results",
                    style="green"
                ))
            elif agent == "coding_assistant":
                console.print(Panel(
                    Syntax(data["code"], data["language"].lower(), theme="monokai"),
                    title="Generated Code",
                    style="green"
                ))
                console.print(Panel(
                    Markdown(data["explanation"]),
                    title="Explanation",
                    style="blue"
                ))
            else:  # chat_assistant
                console.print(Panel(
                    Markdown(data["response"]),
                    title="Assistant Response",
                    style="green"
                ))
        except json.JSONDecodeError:
            console.print(f"📄 Raw result: {result}", style="yellow")
    
    async def server_status(self):
        """Check server status"""
        console.print("📡 Checking server status...", style="yellow")
        result = await self.call_mcp_tool("agent_status")
        
        if "error" in result:
            console.print(f"❌ Server Error: {result['error']}", style="red")
        else:
            try:
                data = json.loads(result.get("result", "{}"))
                if data.get("status") == "success":
                    console.print(Panel(
                        json.dumps(data, indent=2),
                        title="Server Status",
                        style="green"
                    ))
                else:
                    console.print(f"❌ Status check failed: {data.get('error', 'Unknown error')}", style="red")
            except json.JSONDecodeError:
                console.print(f"📄 Raw result: {result}", style="yellow")
    
    async def clear_chat_history(self):
        """Clear chat history"""
        result = await self.call_mcp_tool("clear_conversation", session_id=self.session_id)
        
        if "error" in result:
            console.print(f"❌ Error: {result['error']}", style="red")
        else:
            try:
                data = json.loads(result.get("result", "{}"))
                console.print(f"✅ {data.get('message', 'History cleared')}", style="green")
            except json.JSONDecodeError:
                console.print("✅ Chat history cleared", style="green")
    
    async def main_menu(self):
        """Main interactive menu"""
        console.print(Panel(
            "🚀 LangGraph-Groq MCP Client\n\n"
            "Choose your interaction mode:",
            title="Welcome",
            style="bold blue"
        ))
        
        while True:
            console.print("\n📋 Available modes:")
            console.print("1. 🧠 Smart Mode (Auto-route to best agent)")
            console.print("2. 🔬 Research Assistant")
            console.print("3. 💻 Coding Assistant") 
            console.print("4. 💬 Chat Assistant")
            console.print("5. 📡 Server Status")
            console.print("6. 🗑️  Clear Chat History")
            console.print("7. 🚪 Exit")
            
            choice = Prompt.ask("Select mode", choices=["1", "2", "3", "4", "5", "6", "7"])
            
            if choice == "1":
                await self.smart_mode()
            elif choice == "2":
                await self.research_mode()
            elif choice == "3":
                await self.coding_mode()
            elif choice == "4":
                await self.chat_mode()
            elif choice == "5":
                await self.server_status()
            elif choice == "6":
                await self.clear_chat_history()
            elif choice == "7":
                console.print("👋 Goodbye!", style="green bold")
                break


@click.command()
@click.option('--host', default=None, help='MCP server host')
@click.option('--port', default=None, type=int, help='MCP server port')
def main(host, port):
    """
    Groq-powered client for LangGraph MCP Server
    """
    # Override settings if provided
    if host:
        settings.mcp_server_host = host
    if port:
        settings.mcp_server_port = port
    
    # Check if Groq API key is configured
    if not settings.groq_api_key:
        console.print("❌ GROQ_API_KEY not found in environment!", style="red bold")
        console.print("Please set your Groq API key in config/settings.env", style="yellow")
        return
    
    console.print(f"🌐 Connecting to MCP server at {settings.mcp_server_host}:{settings.mcp_server_port}")
    console.print(f"🤖 Using Groq model: {settings.default_model}")
    
    # Run the client
    client = GroqMCPClient()
    asyncio.run(client.main_menu())


if __name__ == "__main__":
    main()