import asyncio
from agents import Agent, Runner
from pydantic import BaseModel

class ShellInfo(BaseModel):
    name

async def main():
    agent = Agent(
        name="Assistant",
        instructions="Answer questions about /ets/shells",
    )

    shells = open('/etc/shells').read()
    result = await Runner.run(agent, [
        {"role": "user", "content": f"File: /etc/shells\n\n{shells}"},
        {"role": "user", "content": "what shells are installed?"}
    ])
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())