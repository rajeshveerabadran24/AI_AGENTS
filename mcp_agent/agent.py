import os
from contextlib import AsyncExitStack
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters, SseServerParams

async def create_agent():
    print("Initializing agent...")

    try:
        # Check for env var
        if not os.getenv("GOOGLE_API_KEY"):
            print("Missing GOOGLE_API_KEY in .env")
            raise EnvironmentError("Missing API key")

        common_exit_stack = AsyncExitStack()

        # Start local MCP tool
        try:
            print("Starting local MCP tool...")
            local_tools, _ = await MCPToolset.from_server(
                connection_params=StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        "/Users/jng/adk_agent_samples"
                    ],
                ),
                async_exit_stack=common_exit_stack
            )
            print(f"✅ Loaded local tools: {len(local_tools)}")
        except Exception as e:
            print(f"❌ Error starting local MCP tool: {e}")
            local_tools = []

        # Start remote MCP tool
        try:
            print("Starting remote MCP tool...")
            remote_tools, _ = await MCPToolset.from_server(
                connection_params=SseServerParams(
                    url="http://localhost:8080/sse"
                ),
                async_exit_stack=common_exit_stack
            )
            print(f"Loaded remote tools: {len(remote_tools)}")
        except Exception as e:
            print(f"❌ Error starting remote MCP tool: {e}")
            remote_tools = []

        tools = [*local_tools, *remote_tools]
        if not tools:
            raise RuntimeError("No tools available. Agent will not start.")
 
        agent = LlmAgent(
            model="gemini-2.0-flash",
            name="file_system_agent",
            instruction="Help the user explore and manage their local file system.",
            tools=tools,
        )


        print("Agent created successfully.")
        return agent, common_exit_stack

    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        return None, None

root_agent = create_agent()