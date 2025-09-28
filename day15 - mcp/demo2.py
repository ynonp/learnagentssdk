import asyncio
from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerStreamableHttp
from agents.model_settings import ModelSettings


async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to answer the questions.",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    result = await Runner.run(agent, "Summarize the top stories from ynet today. URL is: https://www.ynet.co.il/news/category/184")
    print(result.to_input_list())
    print(result.final_output)


async def main():
    async with MCPServerStreamableHttp(
        name="Streamable HTTP Python Server",
        cache_tools_list=True,
        params={
            "url": "https://remote.mcpservers.org/fetch/mcp",
        },
    ) as server:
        await run(server)


if __name__ == "__main__":
    asyncio.run(main())
