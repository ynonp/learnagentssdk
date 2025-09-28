# FastAPI Template (with Static Assets)

A minimal FastAPI project template that serves an API and static HTML/JS/CSS.

## Project Layout

```
.
├── app/
│   ├── __init__.py
│   └── main.py              # FastAPI app and routes
├── static/
│   ├── index.html           # Frontend entry
│   ├── app.js               # Fetches API message
│   └── styles.css           # Basic styles
├── requirements.txt         # Dependencies
└── README.md
```

## Prerequisites

- Python 3.10+ (tested with 3.12)

## Setup

1) Create a virtual environment

```bash
python3 -m venv .venv
```

2) Activate the environment

- macOS/Linux:
  ```bash
  source .venv/bin/activate
  ```
- Windows (PowerShell):
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

3) Install dependencies

```bash
pip install -r requirements.txt
```

## Run the Server

```bash
uvicorn app.main:app --reload
```

- Open: http://127.0.0.1:8000/
- API endpoint: http://127.0.0.1:8000/api/message

## What It Does

- Serves `static/index.html` at `/`.
- Mounts static files under `/static`.
- Provides `GET /api/message` which returns plain text.

## Notes

- `--reload` enables auto-reload during development.
- To deactivate the virtual environment: `deactivate`.
