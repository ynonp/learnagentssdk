import asyncio

from agents import Agent, Runner, ImageGenerationTool

agent = Agent(
    name="Assistant",
    tools=[
        ImageGenerationTool(
            tool_config={
                "type": "image_generation",
            }
        ),
    ],
)

async def main():
    result = await Runner.run(agent, "Create an picture of a coffee shop in Tel Aviv")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
