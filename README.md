# MCP Example for LangChain

This repository demonstrates how to use **Model Context Protocol (MCP)** with LangChain to create a multi-server agent system. The project includes two MCP servers (Math and Weather) and a LangChain client that can interact with both servers using their tools.

## Overview

This project showcases:
- **MCP Servers**: Two independent servers providing tools via streamable HTTP transport
  - **Math Server** (Port 8000): Provides basic math operations (add, subtract, multiply, divide)
  - **Weather Server** (Port 8001): Provides weather information for locations
- **LangChain Client**: A client application that connects to multiple MCP servers and uses LangChain agents to orchestrate tool calls
- **FastAPI API Server**: A REST API wrapper around the LangChain agent for HTTP-based interactions

## Architecture

```
┌─────────────────┐
│  LangChain      │
│  Agent          │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│ Math   │ │ Weather  │
│ Server │ │ Server   │
│ :8000  │ │ :8001    │
└────────┘ └──────────┘
```

## Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Google Gemini API key (set in `.env` file)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ddtuong/mcp-workflow.git
cd mcp-workflow
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_google_api_key_here
```

## Usage

### Running the MCP Servers

The MCP servers must be running before starting the client. Each server runs as a separate process.

#### Start Math Server (Port 8000)
```bash
uv run mcp_math
```

#### Start Weather Server (Port 8001)
```bash
uv run mcp_weather
```

Both servers support optional command-line arguments:
- `--port`: Port to listen on (default: 8000 for math, 8001 for weather)
- `--log-level`: Logging level - DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
- `--json-response`: Enable JSON responses instead of SSE streams

Example:
```bash
uv run mcp_math --port 8000 --log-level DEBUG
uv run mcp_weather --port 8001 --log-level INFO
```

### Running the Client

Once both servers are running, start the client:

```bash
uv run client\main.py
```

The client will:
1. Connect to both MCP servers
2. Retrieve available tools from each server
3. Create a LangChain agent with Google Gemini model
4. Execute example queries demonstrating both math and weather tools

### Running with FastAPI

For HTTP-based interactions, you can run the FastAPI API server:

```bash
uv run uvicorn api.server:app --reload
```

The API server provides a REST endpoint:

**POST** `/invoke`
- **Request Body**:
  ```json
  {
    "query": "What's (3 + 5) x 12?"
  }
  ```
- **Response**:
  ```json
  {
    "response": "The answer is 96"
  }
  ```

Example using curl:
```bash
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in Vietnam?"}'
```

## Available Tools

### Math Server Tools

- **add**: Add two numbers together
  - Parameters: `a` (number), `b` (number)
- **subtract**: Subtract the second number from the first
  - Parameters: `a` (number), `b` (number)
- **multiply**: Multiply two numbers together
  - Parameters: `a` (number), `b` (number)
- **divide**: Divide the first number by the second
  - Parameters: `a` (number), `b` (number)

### Weather Server Tools

- **weather**: Get weather information for a specific location
  - Parameters: `location` (string)

## Project Structure

```
mcp-example/
├── mcp_math/          # Math MCP server
│   └── server.py      # Math server implementation
├── mcp_weather/       # Weather MCP server
│   └── server.py      # Weather server implementation
├── client/            # LangChain client
│   └── main.py        # Client application
├── api/               # FastAPI API server
│   └── server.py      # REST API wrapper
├── pyproject.toml     # Project configuration
└── README.md          # This file
```

## How It Works

1. **MCP Servers**: Each server implements the MCP protocol using streamable HTTP transport. They expose tools that can be called by MCP clients.

2. **MultiServerMCPClient**: The LangChain adapter `MultiServerMCPClient` connects to multiple MCP servers simultaneously and aggregates their tools.

3. **LangChain Agent**: The client creates a LangChain agent with the aggregated tools, allowing natural language queries to be processed and appropriate tools to be called automatically.

4. **FastAPI Integration**: The API server provides a RESTful interface to the LangChain agent, making it accessible via HTTP requests.

## Technology Stack

- **MCP**: Model Context Protocol for tool communication
- **LangChain**: Framework for building LLM applications
- **LangChain MCP Adapters**: Integration between LangChain and MCP
- **FastAPI/Starlette**: Web framework for API servers
- **Uvicorn**: ASGI server for running the applications
- **Google Gemini**: LLM model used by the agent

## Development

The servers use Starlette (ASGI framework) and can be extended with additional tools or functionality. To add a new tool:

1. Register it in the `list_tools()` handler
2. Implement the logic in the `call_tool()` handler
3. The tool will automatically be available to LangChain agents
