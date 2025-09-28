# Flask Chat Agent

A streaming chat application built with Flask and the Lean Agents SDK.

## Features

- Real-time streaming responses from AI agents
- Configurable agent name and instructions
- Clean, responsive web interface
- Vanilla JavaScript (no build step required)
- Server-Sent Events for real-time updates

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask application:
```bash
python main.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Configure your agent by setting:
   - Agent Name (e.g., "Assistant", "Joker", "Helper")
   - Agent Instructions (e.g., "You are a helpful assistant", "Tell me jokes")

2. Type your message in the chat input

3. Click "Send" or press Enter to send your message

4. Watch as the AI agent streams its response in real-time

## File Structure

```
flask-ui/
├── main.py              # Flask application with streaming endpoints
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── client/             # Frontend files (served as static/templates)
    ├── index.html      # Main HTML page
    ├── style.css       # Styling
    └── script.js       # JavaScript for chat functionality
```

## API Endpoints

- `GET /` - Serves the main chat interface
- `POST /chat` - Streaming chat endpoint that accepts JSON with:
  - `message`: User's message
  - `agent_name`: Name of the agent
  - `agent_instructions`: Instructions for the agent

## Technical Details

- Uses Server-Sent Events (SSE) for real-time streaming
- Handles different event types from the agents SDK:
  - Token streaming for real-time text generation
  - Tool calls and outputs
  - Agent updates
  - Message completion
- Responsive design that works on desktop and mobile
- Error handling for network issues and streaming problems
