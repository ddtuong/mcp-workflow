"""
Simple MCP server example using streamable HTTP transport.

This module demonstrates a basic MCP server implementation using streamable HTTP
transport with basic math operations (addition, subtraction, multiplication, division).
"""

import contextlib
import logging
from collections.abc import AsyncIterator

import click
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

logger = logging.getLogger(__name__)

@click.command()
@click.option("--port", default=8000, help="Port to listen on for HTTP")
@click.option("--log-level", default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
@click.option("--json-response", is_flag=True, default=False, help="Enable JSON responses instead of SSE streams")
def main(port: int, log_level: str, json_response: bool) -> int:
    """
    Run the MCP server with streamable HTTP transport.

    Args:
        port: Port to listen on for HTTP requests.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        json_response: Enable JSON responses instead of SSE streams.
    
    Returns:
        Exit code (0 for success, 1 for failure).
    """
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    app = Server("mcp-streamable-http-stateless-math")

    @app.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        Handel tool calls for math operations.

        Args:
            name: Name of the tool to call.
            arguments: Dictionary of arguments for the tool.
        
        Returns:
            List of content objects with the tool result.

        Raises:
            ValueError: If the tool name is not recognized.
        """
        print("Received tool call:", name, "with arguments:", arguments)
        if name == "add":
            return [
                types.TextContent(
                    type="text",
                    text=str(arguments["a"] + arguments["b"]),
                )
            ]
        elif name == "subtract":
            return [
                types.TextContent(
                    type="text",
                    text=str(arguments["a"] - arguments["b"]),
                )
            ]
        elif name == "multiply":
            return [
                types.TextContent(
                    type="text",
                    text=str(arguments["a"] * arguments["b"]),
                )
            ]
        elif name == "divide":
            return [
                types.TextContent(
                    type="text",
                    text=str(arguments["a"] / arguments["b"]),
                )
            ]
        else:
            raise ValueError(f"Unknown tool: {name}")
        
    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """
        List all available tools provided by this server.

        Returns:
            List of tool definitions for all available tools.
        """
        return [
            types.Tool(
                name="add",
                description="Add two numbers together.",
                inputSchema={
                    "type": "object",
                    "required": ["a", "b"],
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "The first number to add.",
                            },
                        "b": {
                            "type": "number",
                            "description": "The second number to add.",
                            },
                    },
                },
            ),
            types.Tool(
                name="subtract",
                description="Subtract the second number from the first number.",
                inputSchema={
                    "type": "object",
                    "required": ["a", "b"],
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "The first number to subtract.",
                            },
                        "b": {
                            "type": "number",
                            "description": "The second number to subtract.",
                            },
                    },
                },
            ),
            types.Tool(
                name="multiply",
                description="Multiply two numbers together.",
                inputSchema={
                    "type": "object",
                    "required": ["a", "b"],
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "The first number to multiply.",
                            },
                        "b": {
                            "type": "number",
                            "description": "The second number to multiply.",
                            },
                    },
                },
            ),
            types.Tool(
                name="divide",
                description="Divide the first number by the second number.",
                inputSchema={
                    "type": "object",
                    "required": ["a", "b"],
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "The first number to divide.",
                            },
                        "b": {
                            "type": "number",
                            "description": "The second number to divide.",
                            },  
                    },
                },
            ),
        ]
    
    # create the session manager with true stateless mode
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,
        json_response=json_response,
        stateless=True
    )

    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        """Handle streamable HTTP requests through the session manager.

        Args:
            scope: ASGI scope object.
            receive: ASGI receive callable.
            send: ASGI send callable.
        """
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager lifecycle.

        Args:
            app: The Starlette application instance.

        Yields:
            None during the application lifetime.
        """
        async with session_manager.run():
            logger.info("Application started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                logger.info("Application shutting down...")

    # Create an ASGI application using the transport
    starlette_app = Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    import uvicorn

    uvicorn.run(starlette_app, host="0.0.0.0", port=port)

    return 0

