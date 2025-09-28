from __future__ import annotations

import random
from typing import List, Literal, Optional, Dict
from fastapi import APIRouter, HTTPException, WebSocket, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator
from openai.types.responses import ResponseTextDeltaEvent
from openai.types.responses.response_input_item_param import Message, ResponseInputItemParam
from agents import Agent, Runner, trace, function_tool, RunContextWrapper

router = APIRouter()

Mark = Literal["X", "O"]

class WebsocketContext:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

@function_tool
async def play(ctx: RunContextWrapper[WebsocketContext], row: int, column: int):
    """Make a move in the tic tac toe game at the specified row and column (0-2)"""
    websocket = ctx.context.websocket
    await websocket.send_json({
        "action": "play", 
        "payload": {"row": row, "column": column}
    })
    return f"Played at row {row}, column {column}"


assistant = Agent(
    name="game_assistant",
    tools=[play],
    instructions=(
        "You are a friendly assistant helping the user play tic tac toe. You can make moves in the game by calling the play function."        
    ),
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def add_client(self, client_id: str, websocket: WebSocket):
        """Add a new client connection"""
        self.active_connections[client_id] = websocket
    
    def remove_client(self, client_id: str):
        """Remove a client connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    def get_websocket(self, client_id: str) -> Optional[WebSocket]:
        """Get websocket connection for a client"""
        return self.active_connections.get(client_id)
    
    async def send_personal_message(self, message: dict, client_id: str):
        """Send a message to a specific client"""
        websocket = self.get_websocket(client_id)
        if websocket:
            await websocket.send_json(message)

connection_manager = ConnectionManager()


class NextMoveRequest(BaseModel):
    board: List[Optional[Mark]] = Field(..., min_length=9, max_length=9)

    @validator("board")
    def validate_board(cls, v: List[Optional[Mark]]) -> List[Optional[Mark]]:
        if len(v) != 9:
            raise ValueError("board must have exactly 9 cells")
        return v


class NextMoveResponse(BaseModel):
    index: int


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatCompletionRequest(BaseModel):
    payload: List[ChatMessage]


@router.post("/api/next_move", response_model=NextMoveResponse)
def next_move(payload: NextMoveRequest) -> NextMoveResponse:
    """Return a random empty cell index for the computer move.

    - Expects `board` as a list of 9 items with values 'X', 'O', or null.
    - Responds with `index` in [0, 8] where the computer should play.
    """
    empties = [i for i, cell in enumerate(payload.board) if cell is None]
    if not empties:
        raise HTTPException(status_code=400, detail="No empty squares available")
    idx = random.choice(empties)
    return NextMoveResponse(index=idx)

@router.post('/api/complete')
async def complete(request: ChatCompletionRequest, client_id: str = Query(...)):
    """Stream the assistant's response using Server-Sent Events."""
    # Convert Pydantic models to dictionaries for JSON serialization
    messages = [message.model_dump() for message in request.payload]
    websocket = connection_manager.get_websocket(client_id)
    
    if not websocket:
        raise HTTPException(status_code=400, detail="WebSocket connection not found for client_id")

    async def generate_stream():
        result = Runner.run_streamed(assistant, messages, WebsocketContext(websocket))
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                # Send the delta as Server-Sent Events format
                yield f"data: {event.data.delta}\n\n"
        
        # Send end of stream marker
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    await connection_manager.add_client(client_id, websocket)
    try:
        while True:
            # Keep the connection alive and listen for any messages
            data = await websocket.receive_text()
            # Echo back for debugging purposes
            await websocket.send_json({"type": "echo", "data": data})
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        connection_manager.remove_client(client_id)
