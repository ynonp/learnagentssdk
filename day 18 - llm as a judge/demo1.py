import asyncio
from dataclasses import dataclass
from typing import Literal

from agents import Agent, Runner, trace, SQLiteSession

"""
This example shows the LLM as a judge pattern. The first agent generates an outline for a story.
The second agent judges the outline and provides feedback. We loop until the judge is satisfied
with the outline.
"""

story_outline_generator = Agent(
    name="story_outline_generator",
    instructions=(
        "You generate a very short story outline based on the user's input. "
        "If there is any feedback provided, use it to improve the outline."
    ),
)


@dataclass
class EvaluationFeedback:
    feedback: str
    score: Literal["pass", "needs_improvement", "fail"]


evaluator = Agent(
    name="evaluator",
    instructions=(
        "You evaluate a story outline and decide if it's good enough. "
        "If it's not good enough, you provide feedback on what needs to be improved. "
        "Never give it a pass on the first try. After 5 attempts, you can give it a pass if the story outline is good enough - do not go for perfection"
    ),
    output_type=EvaluationFeedback,
)


async def main() -> None:
    writer_session = SQLiteSession("story")
    judge_session = SQLiteSession("judge")

    msg = input("What kind of story would you like to hear? ")

    latest_outline: str | None = None

    # We'll run the entire workflow in a single trace
    with trace("LLM as a judge"):
        while True:
            story_outline_result = await Runner.run(
                story_outline_generator,
                msg,
                session=writer_session
            )

            latest_outline = story_outline_result.final_output
            print("Story outline generated")

            evaluator_result = await Runner.run(evaluator, msg, session=judge_session)
            result: EvaluationFeedback = evaluator_result.final_output

            print(f"Evaluator score: {result.score}")

            if result.score == "pass":
                print("Story outline is good enough, exiting.")
                break

            print("Re-running with feedback")
            await writer_session.add_items([{"content": f"Feedback: {result.feedback}", "role": "user"}])

    print(f"Final story outline: {latest_outline}")


if __name__ == "__main__":
    asyncio.run(main())