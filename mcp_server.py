#!/usr/bin/env python3
"""
MCP Weather Server - Model Context Protocol Server Implementation
Author: Cavin Otieno
License: MIT

This server implements the MCP specification for tool discovery and execution.
"""

import json
import sys
import os
import urllib.request
import urllib.error
import urllib.parse
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


# OpenWeatherMap API Key - Get your free key at https://openweathermap.org/api
# For demo purposes, you can use the placeholder below or set WEATHER_API_KEY environment variable
OPENWEATHERMAP_API_KEY = os.environ.get('WEATHER_API_KEY', 'YOUR_API_KEY_HERE')

# List of valid cities for validation (case-insensitive matching)
VALID_CITIES = {
    # Africa
    "nairobi", "cairo", "lagos", "johannesburg", "cape town", "accra", "addis ababa", "dakar", "kinshasa", "dar es salaam",
    # Asia
    "tokyo", "beijing", "shanghai", "mumbai", "delhi", "bangalore", "hong kong", "singapore", "bangkok", "dubai", "riyadh", "istanbul",
    # Europe
    "london", "paris", "berlin", "madrid", "rome", "amsterdam", "vienna", "prague", "stockholm", "oslo", "copenhagen", "helsinki", "dublin", "lisbon", "athens", "moscow",
    # North America
    "new york", "los angeles", "chicago", "houston", "phoenix", "san francisco", "seattle", "miami", "boston", "denver", "toronto", "vancouver", "mexico city", "montreal",
    # South America
    "sao paulo", "rio de janeiro", "buenos aires", "lima", "bogota", "santiago",
    # Oceania
    "sydney", "melbourne", "brisbane", "auckland", "wellington",
    # Caribbean
    "kingston", "havana", "nassau", "san juan"
}


def get_weather_from_api(location: str, units: str = "metric") -> Dict[str, Any]:
    """
    Fetch real weather data from OpenWeatherMap API.

    Args:
        location: City name
        units: 'metric' for Celsius, 'imperial' for Fahrenheit

    Returns:
        Weather data dictionary or error
    """
    api_key = OPENWEATHERMAP_API_KEY

    # If no API key configured, return demo mode notice
    if api_key == 'YOUR_API_KEY_HERE' or not api_key:
        return {
            "mode": "demo",
            "message": "Configure WEATHER_API_KEY environment variable for real weather data",
            "demo_available": True
        }

    # Determine API units
    api_units = "metric" if units == "celsius" else "imperial"

    # Build API URL
    url = f"https://api.openweathermap.org/data/2.5/weather?q={urllib.parse.quote(location)}&appid={api_key}&units={api_units}"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

            # Parse weather data
            weather = data["weather"][0]
            main = data["main"]
            wind = data["wind"]

            return {
                "mode": "live",
                "location": data["name"],
                "country": data["sys"]["country"],
                "temperature": round(main["temp"]),
                "feels_like": round(main["feels_like"]),
                "temp_min": round(main["temp_min"]),
                "temp_max": round(main["temp_max"]),
                "humidity": main["humidity"],
                "pressure": main["pressure"],
                "condition": weather["main"],
                "description": weather["description"].capitalize(),
                "icon": weather["icon"],
                "wind_speed": wind.get("speed", 0),
                "wind_direction": wind.get("deg", 0),
                "visibility": data.get("visibility", "N/A"),
                "sunrise": data["sys"]["sunrise"],
                "sunset": data["sys"]["sunset"],
                "timezone": data["timezone"],
                "units": units
            }
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ValueError(f"City '{location}' not found. Please enter a valid city name.")
        elif e.code == 401:
            raise ValueError("Invalid API key. Please check your OpenWeatherMap API key.")
        else:
            raise ValueError(f"Weather API error: HTTP {e.code}")
    except urllib.error.URLError:
        raise ValueError("Unable to connect to weather service. Please check your internet connection.")
    except Exception as e:
        raise ValueError(f"Weather service error: {str(e)}")


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
        """
        Handle weather tool execution with location validation.

        Validates the location against known cities and fetches real weather data
        from OpenWeatherMap API if configured. Returns helpful error messages
        for invalid locations.
        """
        location = args.get("location", "").strip()
        units = args.get("units", "celsius")

        # Validate location is provided
        if not location:
            raise ValueError("Location is required. Please provide a city name.")

        # Check if location matches any known city (case-insensitive)
        location_lower = location.lower()
        is_valid_city = location_lower in VALID_CITIES

        # Try to get real weather data
        try:
            weather_result = get_weather_from_api(location, units)

            # If API returned demo mode or error, use validated demo
            if weather_result.get("mode") == "demo":
                # Use validated demo data - only for known cities
                if is_valid_city:
                    return {
                        "mode": "demo",
                        "location": location.title(),
                        "temperature": 22 if units == "celsius" else 72,
                        "units": units,
                        "condition": "Sunny",
                        "humidity": 65,
                        "wind_speed": "15 km/h",
                        "message": f"Demo mode: Real API key not configured. Validated city '{location}' accepted.",
                        "api_key_required": True
                    }
                else:
                    # Invalid city - provide helpful error with suggestions
                    suggestions = self._get_city_suggestions(location_lower)
                    raise ValueError(
                        f"'{location}' is not a recognized city. "
                        f"Please enter a valid city name such as: {suggestions}"
                    )

            return weather_result

        except ValueError as e:
            # Re-raise validation errors
            raise
        except Exception as e:
            # For API errors in demo mode, fall back to validated demo
            if is_valid_city:
                return {
                    "mode": "demo_fallback",
                    "location": location.title(),
                    "temperature": 22 if units == "celsius" else 72,
                    "units": units,
                    "condition": "Cloudy",
                    "humidity": 70,
                    "wind_speed": "12 km/h",
                    "message": f"API temporarily unavailable. Using demo data for '{location}'.",
                    "error": str(e)
                }
            else:
                suggestions = self._get_city_suggestions(location_lower)
                raise ValueError(
                    f"'{location}' is not a recognized city. "
                    f"Please enter a valid city name such as: {suggestions}"
                )

    def _get_city_suggestions(self, partial: str) -> str:
        """Get city suggestions based on partial match."""
        matches = [city for city in VALID_CITIES if partial in city]
        if matches:
            return ", ".join(matches[:5])
        return "Nairobi, Tokyo, London, New York, Sydney"

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