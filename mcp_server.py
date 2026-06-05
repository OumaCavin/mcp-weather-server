#!/usr/bin/env python3
"""
MCP Weather Server - Model Context Protocol Server Implementation
Author: Cavin Otieno
License: MIT

This server implements the MCP specification for tool discovery and execution.
Features comprehensive error handling and transaction-style operations.
"""

import json
import sys
import os
import logging
import urllib.request
import urllib.error
import urllib.parse
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager

# Configure logging for better debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MCPWeatherServer')

# OpenWeatherMap API Key - Get your free key at https://openweathermap.org/api
OPENWEATHERMAP_API_KEY = os.environ.get('WEATHER_API_KEY', 'YOUR_API_KEY_HERE')

# Comprehensive list of valid cities for quick demo fallback
VALID_CITIES = {
    # Africa - Extended coverage
    "nairobi", "cairo", "lagos", "johannesburg", "cape town", "accra", "addis ababa",
    "dakar", "kinshasa", "dar es salaam", "abidjan", "yaounde", "douala", "algeria",
    "tunis", "casablanca", "marrakech", "kigali", "kampala", "lusaka", "harare",
    "maputo", "luanda", "abuja", "freetown", "monrovia", "bamako",
    # Asia - Major cities
    "tokyo", "beijing", "shanghai", "mumbai", "delhi", "bangalore", "hong kong",
    "singapore", "bangkok", "dubai", "riyadh", "istanbul", "osaka", "seoul", "taipei",
    "manila", "jakarta", "kuala lumpur", "hanoi", "ho chi minh city", "kolkata",
    # Europe
    "london", "paris", "berlin", "madrid", "rome", "amsterdam", "vienna", "prague",
    "stockholm", "oslo", "copenhagen", "helsinki", "dublin", "lisbon", "athens", "moscow",
    "zurich", "warsaw", "brussels", "budapest", "bucharest", "kyiv", "minsk",
    # North America
    "new york", "los angeles", "chicago", "houston", "phoenix", "san francisco",
    "seattle", "miami", "boston", "denver", "toronto", "vancouver", "mexico city",
    "montreal", "atlanta", "dallas", "san diego", "las vegas", "austin", "portland",
    # South America
    "sao paulo", "rio de janeiro", "buenos aires", "lima", "bogota", "santiago",
    "caracas", "medellin", "quito", "montevideo", "asuncion",
    # Oceania
    "sydney", "melbourne", "brisbane", "auckland", "wellington", "perth", "adelaide",
    # Caribbean
    "kingston", "havana", "nassau", "san juan", "santo domingo", "port au prince"
}


@contextmanager
def api_transaction(location: str, operation: str = "fetch"):
    """
    Context manager for API operations with automatic cleanup and error handling.
    Implements transaction-style pattern for reliable API calls.
    """
    transaction_id = f"{operation}_{location}_{id(object())}"
    logger.info(f"Starting transaction {transaction_id}")
    try:
        yield transaction_id
        logger.info(f"Transaction {transaction_id} completed successfully")
    except Exception as e:
        logger.error(f"Transaction {transaction_id} failed: {str(e)}")
        raise
    finally:
        logger.debug(f"Transaction {transaction_id} cleanup complete")


def get_weather_from_api(location: str, units: str = "metric") -> Dict[str, Any]:
    """
    Fetch real weather data from OpenWeatherMap API with transaction handling.

    Args:
        location: City name
        units: 'metric' for Celsius, 'imperial' for Fahrenheit

    Returns:
        Weather data dictionary or error
    """
    with api_transaction(location, "weather_fetch"):
        api_key = OPENWEATHERMAP_API_KEY

        # Validate API key configuration
        if not api_key or api_key == 'YOUR_API_KEY_HERE':
            logger.info(f"Demo mode triggered for location: {location}")
            return {
                "mode": "demo",
                "message": "Configure WEATHER_API_KEY environment variable for real weather data",
                "demo_available": True
            }

        # Validate units parameter
        if units not in ("celsius", "fahrenheit"):
            logger.warning(f"Invalid units parameter: {units}, defaulting to celsius")
            units = "celsius"

        api_units = "metric" if units == "celsius" else "imperial"

        # Build and validate URL
        encoded_location = urllib.parse.quote(location)
        url = f"https://api.openweathermap.org/data/2.5/weather?q={encoded_location}&appid={api_key}&units={api_units}"

        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                # Validate response status
                if response.status != 200:
                    raise ValueError(f"Unexpected response status: {response.status}")

                data = json.loads(response.read().decode())

                # Validate required data fields
                if "weather" not in data or "main" not in data:
                    raise ValueError("Invalid API response: missing required fields")

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
            error_messages = {
                404: f"City '{location}' not found in OpenWeatherMap database",
                401: "Invalid API key. Please check your WEATHER_API_KEY",
                429: "Rate limit exceeded. Please try again later",
                500: "OpenWeatherMap service temporarily unavailable",
                503: "OpenWeatherMap service is down"
            }
            message = error_messages.get(e.code, f"Weather API error: HTTP {e.code}")
            logger.error(f"HTTP error for {location}: {message}")
            raise ValueError(message)

        except urllib.error.URLError as e:
            logger.error(f"Network error for {location}: {str(e)}")
            raise ValueError("Unable to connect to weather service. Please check your internet connection.")

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error for {location}: {str(e)}")
            raise ValueError("Invalid response from weather service")

        except Exception as e:
            logger.error(f"Unexpected error for {location}: {str(e)}")
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
        logger.info("Initializing MCP Weather Server")
        self.tools: Dict[str, Tool] = {}
        self.request_count = 0
        self._register_builtin_tools()
        logger.info(f"Server initialized with {len(self.tools)} tools")

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
        logger.info(f"Registering tool: {tool.name}")
        self.tools[tool.name] = tool

    def discover_tools(self) -> List[Dict[str, Any]]:
        """
        Discovery phase: List all available tools.

        Returns:
            List of tool definitions
        """
        self.request_count += 1
        logger.info(f"Tool discovery request #{self.request_count}")
        return [tool.to_dict() for tool in self.tools.values()]

    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """
        Get a specific tool by name.

        Args:
            tool_name: Name of the tool to retrieve

        Returns:
            Tool object if found, None otherwise
        """
        tool = self.tools.get(tool_name)
        if not tool:
            logger.warning(f"Tool not found: {tool_name}")
        return tool

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """
        Execute a tool with the provided arguments.
        Implements transaction-style execution with error handling.

        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool

        Returns:
            ToolResult with success status and data or error
        """
        self.request_count += 1
        transaction_id = f"execute_{tool_name}_{self.request_count}"
        logger.info(f"Starting execution {transaction_id}")

        try:
            # Validate tool exists
            tool = self.get_tool(tool_name)
            if not tool:
                logger.error(f"Tool '{tool_name}' not found")
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Tool '{tool_name}' not found. Available tools: {', '.join(self.tools.keys())}"
                )

            # Validate handler exists
            if not tool.handler:
                logger.error(f"Tool '{tool_name}' has no handler defined")
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Tool '{tool_name}' has no handler defined"
                )

            # Execute tool with transaction block
            logger.info(f"Executing tool '{tool_name}' with arguments: {arguments}")
            result = tool.handler(arguments)
            logger.info(f"Tool '{tool_name}' executed successfully")
            return ToolResult(success=True, data=result)

        except ValueError as e:
            logger.error(f"Validation error in {transaction_id}: {str(e)}")
            return ToolResult(success=False, data=None, error=str(e))

        except Exception as e:
            logger.error(f"Execution error in {transaction_id}: {str(e)}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Tool execution failed: {str(e)}"
            )

    def _handle_weather(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle weather tool execution with comprehensive error handling.
        """
        logger.info("Processing weather request")
        location = args.get("location", "").strip()
        units = args.get("units", "celsius")

        # Validate location is provided
        if not location:
            logger.error("Weather request missing location")
            raise ValueError("Location is required. Please provide a city name.")

        # Validate units parameter
        if units not in ("celsius", "fahrenheit"):
            logger.warning(f"Invalid units '{units}', defaulting to celsius")
            units = "celsius"

        # Check if location matches known cities
        location_lower = location.lower()
        is_valid_city = location_lower in VALID_CITIES

        if is_valid_city:
            logger.info(f"Location '{location}' found in validated cities list")
        else:
            logger.info(f"Location '{location}' not in validated list, will use API")

        # Get weather data with transaction
        try:
            with api_transaction(location, "weather_get"):
                weather_result = get_weather_from_api(location, units)

                # Handle demo mode
                if weather_result.get("mode") == "demo":
                    logger.info(f"Demo mode for location: {location}")
                    return {
                        "mode": "demo",
                        "location": location.title(),
                        "temperature": 22 if units == "celsius" else 72,
                        "units": units,
                        "condition": "Sunny" if is_valid_city else "Unknown",
                        "humidity": 65,
                        "wind_speed": "15 km/h",
                        "message": f"Demo mode: Real API key not configured. Data for '{location}' is simulated.",
                        "api_key_required": True,
                        "validated": is_valid_city,
                        "suggestion": "Set WEATHER_API_KEY environment variable for real weather data from OpenWeatherMap"
                    }

                logger.info(f"Live weather data retrieved for: {location}")
                return weather_result

        except ValueError as e:
            logger.error(f"Weather API error: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected weather error: {str(e)}")
            # Fall back to demo data for any city
            return {
                "mode": "demo_fallback",
                "location": location.title(),
                "temperature": 22 if units == "celsius" else 72,
                "units": units,
                "condition": "Cloudy",
                "humidity": 70,
                "wind_speed": "12 km/h",
                "message": f"API temporarily unavailable. Using demo data for '{location}'.",
                "validated": is_valid_city,
                "error": str(e)
            }

    def _get_city_suggestions(self, partial: str) -> str:
        """Get city suggestions based on partial match."""
        matches = [city for city in VALID_CITIES if partial in city]
        if matches:
            return ", ".join(matches[:5])
        return "Nairobi, Tokyo, London, New York, Sydney"

    def _handle_calculate(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle calculator tool execution with safe evaluation."""
        expression = args.get("expression", "")
        logger.info(f"Processing calculation: {expression}")

        if not expression:
            raise ValueError("Expression is required for calculator tool")

        try:
            # Safe evaluation - only allow basic arithmetic
            allowed_chars = set("0123456789+-*/.() ")
            if not all(c in allowed_chars for c in expression):
                logger.error(f"Invalid characters in expression: {expression}")
                raise ValueError("Invalid characters in expression. Only numbers and +-*/(). are allowed.")

            result = eval(expression)
            logger.info(f"Calculation result: {result}")
            return {"expression": expression, "result": result}

        except ZeroDivisionError:
            logger.error("Division by zero attempted")
            raise ValueError("Division by zero is not allowed")

        except SyntaxError as e:
            logger.error(f"Invalid expression syntax: {str(e)}")
            raise ValueError(f"Invalid expression syntax: {str(e)}")

        except Exception as e:
            logger.error(f"Calculation error: {str(e)}")
            raise ValueError(f"Calculation error: {str(e)}")

    def _handle_text_process(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle text processing tool execution."""
        text = args.get("text", "")
        operation = args.get("operation", "uppercase")
        logger.info(f"Processing text: '{text}' with operation: {operation}")

        if not text:
            logger.warning("Empty text provided, returning empty result")
            return {"original_text": "", "operation": operation, "result": ""}

        valid_operations = ["uppercase", "lowercase", "reverse", "length"]
        if operation not in valid_operations:
            logger.warning(f"Unknown operation '{operation}', defaulting to uppercase")
            operation = "uppercase"

        operations = {
            "uppercase": text.upper(),
            "lowercase": text.lower(),
            "reverse": text[::-1],
            "length": len(text)
        }

        result = operations.get(operation, text.upper())
        logger.info(f"Text processing complete: {result}")
        return {"original_text": text, "operation": operation, "result": result}


def create_response(request_type: str, data: Any) -> Dict[str, Any]:
    """
    Create a standardized MCP response.

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
    Handle an incoming MCP request with error handling.

    Returns:
        Response dictionary
    """
    action = request.get("action")
    payload = request.get("payload", {})
    logger.info(f"Handling MCP request: action={action}")

    try:
        if action == "discover":
            tools = server.discover_tools()
            return create_response("discovery", {"tools": tools})

        elif action == "execute":
            tool_name = payload.get("tool")
            arguments = payload.get("arguments", {})

            if not tool_name:
                logger.error("Execute request missing 'tool' field")
                return create_response("error", {"message": "Tool name is required"})

            result = server.execute_tool(tool_name, arguments)
            return create_response("execution", result.to_dict())

        elif action == "get_tool":
            tool_name = payload.get("tool")
            if not tool_name:
                return create_response("error", {"message": "Tool name is required"})

            tool = server.get_tool(tool_name)
            if tool:
                return create_response("tool_info", tool.to_dict())
            return create_response("error", {"message": f"Tool '{tool_name}' not found"})

        else:
            logger.error(f"Unknown action: {action}")
            return create_response("error", {"message": f"Unknown action: {action}"})

    except Exception as e:
        logger.error(f"Request handling error: {str(e)}")
        return create_response("error", {"message": f"Request handling failed: {str(e)}"})


def main():
    """Main entry point for the MCP server."""
    logger.info("Starting MCP Weather Server")
    server = MCPServer()

    try:
        # Read requests from stdin
        request_json = sys.stdin.read()

        if not request_json or not request_json.strip():
            logger.warning("Empty request received")
            print(json.dumps(create_response("error", {"message": "Empty request"}), indent=2))
            return

        try:
            request = json.loads(request_json)
            response = handle_request(request, server)
            print(json.dumps(response, indent=2))

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {str(e)}")
            error_response = create_response("error", {"message": f"Invalid JSON: {str(e)}"})
            print(json.dumps(error_response, indent=2))

    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
        print(json.dumps(create_response("info", {"message": "Server shutdown requested"}), indent=2))

    except Exception as e:
        logger.error(f"Unexpected server error: {str(e)}")
        error_response = create_response("error", {"message": f"Server error: {str(e)}"})
        print(json.dumps(error_response, indent=2))

    finally:
        logger.info("MCP Weather Server shutdown complete")


if __name__ == "__main__":
    main()