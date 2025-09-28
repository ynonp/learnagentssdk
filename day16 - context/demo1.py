from typing_extensions import TypedDict
from agents import Agent, function_tool, Runner, SQLiteSession, RunContextWrapper
from agents.extensions.models.litellm_model import LitellmModel
from pydantic import BaseModel

import requests
import os
import asyncio

class AssistantContext(BaseModel):
    weather_api_url: str
    weather_api_key: str

class Location(TypedDict):
    lat: float
    long: float

@function_tool
async def fetch_weather(wrapper: RunContextWrapper[AssistantContext], location: Location) -> str:
    base_url = wrapper.context.weather_api_url
    params = {
        "lat": location["lat"],
        "lon": location["long"],
        "appid": wrapper.context.weather_api_key,
        "units": "metric"
    }

    # Run the synchronous requests call in a thread pool
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, requests.get, base_url, params)
    response.raise_for_status()

    data = response.json()
    weather_desc = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]

    return f"Weather: {weather_desc.title()}, Temperature: {temp}°C (feels like {feels_like}°C), Humidity: {humidity}%"



agent = Agent(
    name="Assistant",
    model=LitellmModel(model="github/gpt-4.1", api_key=os.environ["GITHUB_TOKEN"]),
    tools=[fetch_weather],
)

async def main():
    session = SQLiteSession("weather", "weather.db")
    ctx = AssistantContext(weather_api_key=os.getenv("OPENWEATHER_API_KEY"), weather_api_url="https://api.openweathermap.org/data/2.5/weather")
    result = await Runner.run(agent, "I'm planning a trip to Israel, what is the weather in Tel Aviv, Jerusalem, Haifa and Eilat today?", session=session, context=ctx)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
