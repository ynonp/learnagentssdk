from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="FastAPI Template")

# Serve static files (HTML/JS/CSS)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

try:
    # Import and register API routes (e.g., tic-tac-toe)
    from .routes_tictactoe import router as tictactoe_router

    app.include_router(tictactoe_router)
except Exception:
    # If routes are missing during initial scaffolding, continue serving static.
    pass


@app.get("/", include_in_schema=False)
def index():
    """Serve the main HTML page."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/message", response_class=PlainTextResponse)
def get_message() -> str:
    """Return a simple text message."""
    return "Hello from FastAPI!"
