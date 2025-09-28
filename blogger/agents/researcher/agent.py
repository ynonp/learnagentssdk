from agents import Agent, Runner
from pydantic import BaseModel, Field
from jinja2 import Environment, FileSystemLoader

class BlogPostIdea(BaseModel):
    title: str = Field(..., title="Title", description="The title of the blog post"),
    main_concepts: list[str] = Field(..., title="Main Concepts", description="Main concepts for the post")

env = Environment(loader=FileSystemLoader("agents/researcher"))
template = env.get_template("instructions.md")

market_research_agent = Agent(
    name="MarketResearcher",
    output_type=list[BlogPostIdea],
    instructions=template.render()
)
