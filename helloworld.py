import asyncio
from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel
import os

async def main():
    models = [
        # "openrouter/moonshotai/kimi-k2",
        # "openrouter/z-ai/glm-4.5",
        # "openrouter/cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
        # "openrouter/inception/mercury",
        "openrouter/google/gemini-2.5-pro"
    ]

    for model in models:
        agent = Agent(
            name="Assistant",
            model=LitellmModel(model=model),
            instructions="You only respond in haikus.",
        )

        print(f"Model: {model}")
        result = await Runner.run(agent, "Tell me about recursion in programming.")
        print(result.final_output)
        print("---")

if __name__ == "__main__":
    asyncio.run(main())