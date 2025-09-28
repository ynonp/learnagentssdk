import asyncio

from agents import Agent, handoff, Runner, SQLiteSession, RunContextWrapper
from pydantic import BaseModel, Field

french_agent = Agent(
    name="French Translator",
    instructions="Translate everything to french"
)
spanish_agent = Agent(
    name="Spanish Translator",
    instructions="Translate everything to Spanish")

class TranslationInput(BaseModel):
    text_to_translate: str = Field(..., description="the text to translate")

async def on_handoff(ctx, input_data: TranslationInput):
    print(f"Translation agent called with text: {input_data.text_to_translate}")


triage_agent = Agent(name="Triage agent", handoffs=[
    handoff(agent=french_agent, input_type=TranslationInput, on_handoff=on_handoff),
    handoff(agent=spanish_agent, input_type=TranslationInput, on_handoff=on_handoff)
])

async def main():
    session = SQLiteSession("handoffs", "handoffs.db")
    result = await Runner.run(triage_agent, "translate to French: 'hello world'", session=session)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
