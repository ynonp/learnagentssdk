from optparse import Option

import agents.run
from typing_extensions import TypedDict
from agents import Agent, function_tool, Runner, SQLiteSession, RunContextWrapper, run_demo_loop, trace, set_trace_processors
from agents.extensions.models.litellm_model import LitellmModel
from pydantic import BaseModel
from typing import Optional
from langsmith.wrappers import OpenAIAgentsTracingProcessor

import requests
import os
import asyncio


class UserContext(BaseModel):
    name: Optional[str]
    favorite_programming_language: Optional[str]

@function_tool
async def set_name(wrapper: RunContextWrapper[UserContext], name: str) -> str:
    """Save user name"""
    wrapper.context.name = name
    return f"User name set to {name}"

@function_tool
async def set_favorite_programming_language(wrapper: RunContextWrapper[UserContext], favorite_programming_language: str) -> str:
    wrapper.context.favorite_programming_language = favorite_programming_language
    return f"Favorite programming language set to {favorite_programming_language}"


agent = Agent(
    name="Assistant",
    model=LitellmModel(model="github/gpt-4.1", api_key=os.environ["GITHUB_TOKEN"]),
    instructions="You are a programming teacher and you want to welcome students to your class. Find out what their name and favorite programming languages are and save the information using the provided tools. Be gentle with the students and ask just one question at a time",
    tools=[set_name, set_favorite_programming_language],
)

async def main():
    session = SQLiteSession("info")
    ctx = UserContext(name=None, favorite_programming_language=None)

    with trace(workflow_name="GetUserDetails"):
        next_message = "Start the conversation with the student."
        while True:
            result = await Runner.run(agent, next_message, session=session, context=ctx)
            print(result.final_output)
            if ctx.name is not None and ctx.favorite_programming_language is not None:
                break

            next_message = input()

    print(ctx)

if __name__ == "__main__":
    set_trace_processors([OpenAIAgentsTracingProcessor()])
    asyncio.run(main())
