from typing_extensions import TypedDict
from agents import Agent, function_tool, Runner, SQLiteSession, FunctionToolResult, ToolsToFinalOutputResult
from agents.extensions.models.litellm_model import LitellmModel
from uuid import uuid4
import random
import os
import asyncio

boxes = [
    {
        "id": str(uuid4()),
        "has_treasure": random.random() > 0.9
    } for _ in range(20)
]

@function_tool
async def open_box(id: str) -> bool:
    """Open a box and search for the treasure inside. Returns True if found"""
    return next(b['has_treasure'] for b in boxes if b['id'] == id)

@function_tool
async def get_box_ids() -> list[str]:
    return [b['id'] for b in boxes]

def custom_tool_use_behavior(context, tool_results: list[FunctionToolResult]) -> ToolsToFinalOutputResult:
    print(context)
    for result in tool_results:
        if result.tool.name == "open_box":
            return ToolsToFinalOutputResult(is_final_output=True, final_output=result.output)
    # Otherwise, continue
    return ToolsToFinalOutputResult(is_final_output=False)

agent = Agent(
    name="Assistant",
    model=LitellmModel(model="github/gpt-4.1", api_key=os.environ["GITHUB_TOKEN"]),
    tools=[open_box, get_box_ids],
    tool_use_behavior=custom_tool_use_behavior
)

async def main():
    session = SQLiteSession("boxes", "boxes.db")
    result = await Runner.run(agent, """
    Let's play a game. You are given 3 boxes and you need to find the treasure hidden in one of them. You can open any box you want
    to look inside.
    Use open_box tool to open boxes and find the treasure. 
    Try to find it by opening the miniumum number of boxes.
    """, session=session, max_turns=3)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
