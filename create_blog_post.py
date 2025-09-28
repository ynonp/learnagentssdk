import asyncio
from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel
import os
from pydantic import BaseModel, Field
import random
class BlogPostIdea(BaseModel):
    title: str = Field(..., title="Title", description="The title of the blog post"),
    main_concepts: list[str] = Field(..., title="Main Concepts", description="Main concepts for the post")

class BlogPost(BaseModel):
    title: str = Field(..., title="Title", description="The title of the blog post"),
    content: str = Field(..., title="Content", description="Actual blog post content in markdown format")

async def main(general_topic: str):
    market_research_agent = Agent(
        name="MarketResearcher",
        model=LitellmModel(model="github/gpt-4.1", api_key=os.environ["GITHUB_TOKEN"]),
        output_type=list[BlogPostIdea],
        instructions="""
        You are a market researcher and your job is to suggest cool ideas for blog posts.
        I will send you ideas and you will help me turn them into engaging posts,
        Or I will send you topics and you will help to focus me on the best viral ideas in these niches.        
        """
    )

    result = await Runner.run(market_research_agent, f"Create 5 blog posts subject lines and main concept for: {general_topic}")
    selected_idea = random.sample(result.final_output, 1)[0]

    writer = Agent(
        name="Writer",
        model=LitellmModel(model="github/gpt-4.1", api_key=os.environ["GITHUB_TOKEN"]),
        instructions="""
        You are a copywriter creating engaging and viral blog posts.
        """,
    )
    post = await Runner.run(writer, f"Create a blog post from the following JSON data: {selected_idea.model_dump()}")
    print(post.final_output)

if __name__ == "__main__":
     asyncio.run(main("dogs"))