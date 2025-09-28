import asyncio

from agents import Agent, Runner, SQLiteSession

async def main():
    agent = Agent(name="Assistant", instructions="Reply very concisely.")
    user_message = input("> ")
    result = await Runner.run(agent, user_message)
    print(result.final_output)

    while True:
        print(f"Debug: messages = {result.to_input_list()}")
        user_message = input("> ")
        result = await Runner.run(agent, result.to_input_list() + [{"role": "user", "content": user_message}])
        print(result.final_output)


if __name__ == '__main__':
    asyncio.run(main())

