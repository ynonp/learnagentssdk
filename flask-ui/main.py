import json
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents import Agent, ItemHelpers, Runner
from openai.types.responses import ResponseTextDeltaEvent

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/client", StaticFiles(directory="client"), name="client")

class ChatRequest(BaseModel):
    message: str
    agent_name: str = "Assistant"
    agent_instructions: str = "You are a helpful assistant."

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("client/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/chat")
async def chat(request: ChatRequest):
    async def generate():
        agent = Agent(
            name=request.agent_name,
            instructions=request.agent_instructions,
        )

        result = Runner.run_streamed(
            agent,
            input=request.message,
        )

        # Send initial message to indicate start
        yield f"data: {json.dumps({'type': 'start', 'message': 'Starting chat...'})}\n\n"

        async for event in result.stream_events():
            # Handle different event types
            if event.type == "raw_response_event":
                if isinstance(event.data, ResponseTextDeltaEvent):
                    # Stream individual tokens
                    token = event.data.delta
                    if token:
                        yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

            elif event.type == "agent_updated_stream_event":
                yield f"data: {json.dumps({'type': 'agent_update', 'agent_name': event.new_agent.name})}\n\n"

            elif event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item":
                    yield f"data: {json.dumps({'type': 'tool_call', 'message': 'Tool was called'})}\n\n"
                elif event.item.type == "tool_call_output_item":
                    yield f"data: {json.dumps({'type': 'tool_output', 'content': str(event.item.output)})}\n\n"
                elif event.item.type == "message_output_item":
                    message_text = ItemHelpers.text_message_output(event.item)
                    yield f"data: {json.dumps({'type': 'message', 'content': message_text})}\n\n"

        # Send completion signal
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8080)
