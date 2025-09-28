# AGENTS.md - Coding Assistant Guidelines

## Development Commands
- Setup: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Run server: `uvicorn app.main:app --reload`
- Test (if exists): `pytest -q` or `pytest tests/test_specific.py::test_function`
- No linting/formatting tools configured yet

## Code Style (FastAPI + Python)
- Follow PEP 8, 4-space indentation
- Naming: `snake_case` functions/vars, `PascalCase` classes, `SCREAMING_SNAKE_CASE` constants
- Imports: `from __future__ import annotations` first, then stdlib → third-party → local
- Types: Use type hints with explicit return types (e.g., `-> NextMoveResponse`)
- Pydantic models for request/response validation with Field() and validators
- Error handling: Use FastAPI HTTPException with specific status codes

## Project Structure
- `app/main.py`: Main FastAPI app with static file mounting
- `app/routes_*.py`: Feature-specific routers (include in main.py)
- `static/`: Frontend HTML/JS/CSS
- WebSocket patterns: Use ConnectionManager class for client management

## Key Patterns
- Async endpoints for streaming/WebSocket operations
- Pydantic BaseModel with validators for data validation  
- Function tools with `@function_tool` decorator for agent integration
- Use `Optional[Type]` for nullable fields, `Literal` for enums
