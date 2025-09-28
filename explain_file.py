import asyncio
from agents import Agent, Runner, function_tool

@function_tool()
def read_shells_file():
    """
    Reads the file /etc/shells and returns the full content
    """
    print("Tool Call: read_shells_file")
    with open('/etc/shells', 'r', encoding='utf8') as f:
        return f.read()

async def main():
    agent = Agent(
        name="Assistant",
        tools=[read_shells_file],
        instructions="Answer questions about the file /etc/shells",
    )

    result = await Runner.run(agent, "What shells are installed?")
    print(result.to_input_list())
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())