import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio

load_dotenv(override=True)


async def main():
    # ---- FETCH MCP ----
    fetch_params = {"command": "uvx", "args": ["mcp-server-fetch"]}

    async with MCPServerStdio(params=fetch_params, client_session_timeout_seconds=60) as server:
        fetch_tools = await server.list_tools()
     #   print("Fetch tools:", fetch_tools)

    # ---- PLAYWRIGHT MCP ----
    playwright_params = {"command": "npx", "args": ["@playwright/mcp@latest"]}

    async with MCPServerStdio(params=playwright_params, client_session_timeout_seconds=60) as server:
        playwright_tools = await server.list_tools()
      #  print("Playwright tools:", playwright_tools)

    # ---- FILESYSTEM MCP ----
    sandbox_path = os.path.abspath(os.path.join(os.getcwd(), "sandbox"))
    os.makedirs(sandbox_path, exist_ok=True)

    files_params = {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", sandbox_path]
    }

    async with MCPServerStdio(params=files_params, client_session_timeout_seconds=60) as server:
        file_tools = await server.list_tools()
    #    print("File tools:", file_tools)

    # ---- AGENT ----
    instructions = """
    You browse the internet to accomplish your instructions.
    You are highly capable at browsing the internet independently to accomplish your task, 
    including accepting all cookies and clicking 'not now' as
    appropriate to get to the content you need. If one website isn't fruitful, try another. 
    Be persistent until you have solved your assignment,
    trying different options and sites as needed.
    When you need to write files, you do that inside the sandbox folder only.
    """
    
    async with MCPServerStdio(params=files_params) as mcp_files:
        async with MCPServerStdio(params=playwright_params) as mcp_browser:

            agent = Agent(
                name="investigator",
                instructions=instructions,
                model="gpt-4.1-mini",
                mcp_servers=[mcp_files, mcp_browser]
            )

            with trace("investigate"):
                result = await Runner.run(
                    agent,
                    "Find a great recipe for South Indian Briyani, then save summary to Briyani.md"
                )

                print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())