import asyncio
from agents import Agent, Runner, function_tool

@function_tool()
def create_empty_file(filename: str):
    """
    Creates a new empty file
    :param filename: the filename to check
    """
    print("Tool Call: create_empty_file")

@function_tool()
def check_file_exists(filename: str) -> bool:
    """
    Check if a file exists
    :param filename: the filename to check
    :return: True if exists
    """
    print("Tool Call: check_file_exists")
    return False

async def main():
    agent = Agent(
        name="Assistant",
        tools=[create_empty_file, check_file_exists],
        instructions="You are a mission critical filesystem agent. Some operations may fail. You need to verify every action worked and retry failed operations",
    )

    result = await Runner.run(agent, "Create an empty file named test.txt")
    print(result.to_input_list())
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())