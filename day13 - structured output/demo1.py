import asyncio

from pydantic import BaseModel
from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel
import os
import json

agent = Agent(
    name="Calendar extractor",
    model=LitellmModel(model="github/DeepSeek-R1", api_key=os.environ["GITHUB_TOKEN"]),
    instructions="""
    Extract calendar events from text. Return JSON object of format:
    {
      name: str,
      date: str,
      participants: list[str]
    }    
    """,
)

async def main():
    result = await Runner.run(agent, "We're having a party this Saturday night, 9:00pm with Mark and Dana")
    data = json.loads(result.final_output)
    print(data)

if __name__ == "__main__":
    asyncio.run(main())
