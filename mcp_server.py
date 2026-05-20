#!/usr/bin/env python3
"""
MCP Weather Server - Model Context Protocol Server Implementation
Author: Cavin Otieno
License: MIT

This server implements the MCP specification for tool discovery and execution.
"""

import json
import sys
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class ToolType(Enum):
    """Enumeration of available tool types."""
    WEATHER = "weather"
    CALCULATOR = "calculator"
    TEXT_PROCESSOR = "text_processor"


@dataclass
class Tool:
    """Represents a tool that can be discovered and executed via MCP."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    tool_type: str
    handler: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
            "toolType": self.tool_type
        }


@dataclass
class ToolResult:
    """Result of tool execution."""
    success: bool
    data: Any
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error
        }


class MCPServer:
    """
    Model Context Protocol Server Implementation.

    This server handles:
    - Tool discovery (listing available tools)
    - Tool execution (running requested tools)
    """

    def __init__(self):
        """Initialize the MCP server with available tools."""
        self.tools: Dict[str, Tool] = {}
        self._register_builtin_tools()

    def _register_builtin_tools(self) -> None:
        """Register built-in tools with the server."""
        # Weather tool
        self.register_tool(Tool(
            name="get_weather",
            description="Get current weather information for a specified location",
            input_schema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name or location to get weather for"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "default": "celsius",
                        "description": "Temperature units"
                    }
                },
                "required": ["location"]
            },
            tool_type="weather",
            handler=self._handle_weather
        ))

        # Calculator tool
        self.register_tool(Tool(
            name="calculate",
            description="Perform arithmetic calculations",
            input_schema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate"
                    }
                },
                "required": ["expression"]
            },
            tool_type="calculator",
            handler=self._handle_calculate
        ))

        # Text processor tool
        self.register_tool(Tool(
            name="process_text",
            description="Process and transform text (uppercase, lowercase, reverse)",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to process"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["uppercase", "lowercase", "reverse", "length"],
                        "description": "Operation to perform on text"
                    }
                },
                "required": ["text", "operation"]
            },
            tool_type="text_processor",
            handler=self._handle_text_process
        ))

    def register_tool(self, tool: Tool) -> None:
        """Register a new tool with the server."""
        self.tools[tool.name] = tool

    def discover_tools(self) -> List[Dict[str, Any]]:
        """
        Discovery phase: List all available tools.

        This is called when an AI model asks "Do you have a tool for weather?"
        The server responds with a list of all available tools.

        Returns:
            List of tool definitions
        """
        return [tool.to_dict() for tool in self.tools.values()]

    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """
        Get a specific tool by name.

        Args:
            tool_name: Name of the tool to retrieve

        Returns:
            Tool object if found, None otherwise
        """
        return self.tools.get(tool_name)

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """
        Execute a tool with the provided arguments.

        This is called when the AI makes a second request like:
        "Please execute your weather tool for the location 'San Francisco'"

        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool

        Returns:
            ToolResult with success status and data or error
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                data=None,
                error=f"Tool '{tool_name}' not found"
            )

        if not tool.handler:
            return ToolResult(
                success=False,
                data=None,
                error=f"Tool '{tool_name}' has no handler defined"
            )

        try:
            result = tool.handler(arguments)
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )

    def _handle_weather(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle weather tool execution."""
        location = args.get("location", "Unknown")
        units = args.get("units", "celsius")

        # Simulated weather data (in production, this would call a real weather API)
        weather_data = {
            "location": location,
            "temperature": 22 if units == "celsius" else 72,
            "units": units,
            "condition": "Partly Cloudy",
            "humidity": 65,
            "wind_speed": "15 km/h"
        }
        return weather_data

    def _handle_calculate(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle calculator tool execution."""
        expression = args.get("expression", "")

        try:
            # Safe evaluation - only allow basic arithmetic
            allowed_chars = set("0123456789+-*/.() ")
            if not all(c in allowed_chars for c in expression):
                raise ValueError("Invalid characters in expression")

            result = eval(expression)  # Safe because we filtered allowed_chars
            return {"expression": expression, "result": result}
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")

    def _handle_text_process(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle text processing tool execution."""
        text = args.get("text", "")
        operation = args.get("operation", "uppercase")

        operations = {
            "uppercase": text.upper(),
            "lowercase": text.lower(),
            "reverse": text[::-1],
            "length": len(text)
        }

        result = operations.get(operation, text.upper())
        return {"original_text": text, "operation": operation, "result": result}


def create_response(request_type: str, data: Any) -> Dict[str, Any]:
    """
    Create a standardized MCP response.

    Args:
        request_type: Type of response (discovery, execution, error)
        data: Response data

    Returns:
        Formatted response dictionary
    """
    return {
        "mcpVersion": "1.0",
        "type": request_type,
        "data": data
    }


def handle_request(request: Dict[str, Any], server: MCPServer) -> Dict[str, Any]:
    """
    Handle an incoming MCP request.

    Args:
        request: Request dictionary with 'action' and 'payload'
        server: MCPServer instance

    Returns:
        Response dictionary
    """
    action = request.get("action")
    payload = request.get("payload", {})

    if action == "discover":
        tools = server.discover_tools()
        return create_response("discovery", {"tools": tools})

    elif action == "execute":
        tool_name = payload.get("tool")
        arguments = payload.get("arguments", {})
        result = server.execute_tool(tool_name, arguments)
        return create_response("execution", result.to_dict())

    elif action == "get_tool":
        tool_name = payload.get("tool")
        tool = server.get_tool(tool_name)
        if tool:
            return create_response("tool_info", tool.to_dict())
        return create_response("error", {"message": f"Tool '{tool_name}' not found"})

    else:
        return create_response("error", {"message": f"Unknown action: {action}"})


def main():
    """Main entry point for the MCP server."""
    server = MCPServer()

    # Read requests from stdin
    try:
        request_json = sys.stdin.read()
        if request_json.strip():
            request = json.loads(request_json)
            response = handle_request(request, server)
            print(json.dumps(response, indent=2))
    except json.JSONDecodeError as e:
        error_response = create_response("error", {"message": f"Invalid JSON: {str(e)}"})
        print(json.dumps(error_response, indent=2))
    except Exception as e:
        error_response = create_response("error", {"message": str(e)})
        print(json.dumps(error_response, indent=2))


if __name__ == "__main__":
    main()