import asyncio
from agents import Agent, Runner, function_tool
from agents.mcp.server import MCPServerStdio, MCPServerStreamableHttp

fetch_server = MCPServerStreamableHttp(
    params={"url": "https://remote.mcpservers.org/fetch/mcp"}
)


async def main():
    await fetch_server.connect()

    agent = Agent(
        name="Assistant",
        mcp_servers=[fetch_server],
        instructions="You are a helpful assistant",
    )

    result = await Runner.run(agent, "What's new today according to ynet?")
    print(result.to_input_list())
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())