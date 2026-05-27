# MCP Weather Server

A Model Context Protocol (MCP) server implementation that enables AI models and agents to discover and execute external tools in a secure and predictable way.

**Author:** Cavin Otieno
**License:** MIT

## Overview

The Model Context Protocol is a standardized specification that allows AI models and agents to interact with external tools and services. This project implements the **server-side** of this interaction, allowing AI systems to:

1. **Discover Tools** - Query available tools on the server
2. **Execute Tools** - Run specific tools with provided arguments

## How MCP Works

```
┌─────────────┐                      ┌──────────────────┐
│   AI Model  │                      │   MCP Server     │
└─────────────┘                      └──────────────────┘
      │                                     │
      │  1. Discovery Request               │
      │  "Do you have a tool for weather?"   │
      ├─────────────────────────────────────►
      │                                     │
      │  2. Tool List Response               │
      │  [get_weather, calculate, ...]      │
      ◄─────────────────────────────────────┤
      │                                     │
      │  3. Execution Request                │
      │  "Execute get_weather for 'SF'"     │
      ├─────────────────────────────────────►
      │                                     │
      │  4. Tool Result                      │
      │  {temp: 22, condition: "Cloudy"}     │
      ◄─────────────────────────────────────┤
```

## Installation

```bash
# Clone the repository
git clone https://github.com/OumaCavin/mcp-weather-server.git
cd mcp-weather-server

# No additional dependencies required
# Uses only Python standard library
```

## Quick Start

### Running the Server

The server reads JSON requests from stdin and outputs JSON responses:

```bash
python mcp_server.py
```

### Available Tools

The server provides three built-in tools:

| Tool Name | Description | Required Parameters |
|-----------|-------------|---------------------|
| `get_weather` | Get current weather for a location | `location` (string) |
| `calculate` | Perform arithmetic calculations | `expression` (string) |
| `process_text` | Transform text (uppercase, lowercase, reverse, length) | `text`, `operation` |

## API Reference

### 1. Tool Discovery

List all available tools on the server.

**Request:**
```json
{
  "action": "discover"
}
```

**Expected Response:**
```json
{
  "mcpVersion": "1.0",
  "type": "discovery",
  "data": {
    "tools": [
      {
        "name": "get_weather",
        "description": "Get current weather information for a specified location",
        "inputSchema": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city name or location to get weather for"
            },
            "units": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"]
            }
          },
          "required": ["location"]
        },
        "toolType": "weather"
      },
      {
        "name": "calculate",
        "description": "Perform arithmetic calculations",
        "inputSchema": {...},
        "toolType": "calculator"
      },
      {
        "name": "process_text",
        "description": "Process and transform text",
        "inputSchema": {...},
        "toolType": "text_processor"
      }
    ]
  }
}
```

### 2. Tool Execution

Execute a specific tool with arguments.

**Request:**
```json
{
  "action": "execute",
  "payload": {
    "tool": "get_weather",
    "arguments": {
      "location": "San Francisco",
      "units": "celsius"
    }
  }
}
```

**Expected Response:**
```json
{
  "mcpVersion": "1.0",
  "type": "execution",
  "data": {
    "success": true,
    "data": {
      "location": "San Francisco",
      "temperature": 22,
      "units": "celsius",
      "condition": "Partly Cloudy",
      "humidity": 65,
      "wind_speed": "15 km/h"
    },
    "error": null
  }
}
```

### 3. Calculator Execution

**Request:**
```json
{
  "action": "execute",
  "payload": {
    "tool": "calculate",
    "arguments": {
      "expression": "25 * 4 + 10"
    }
  }
}
```

**Expected Response:**
```json
{
  "mcpVersion": "1.0",
  "type": "execution",
  "data": {
    "success": true,
    "data": {
      "expression": "25 * 4 + 10",
      "result": 110
    },
    "error": null
  }
}
```

### 4. Text Processor

**Request:**
```json
{
  "action": "execute",
  "payload": {
    "tool": "process_text",
    "arguments": {
      "text": "Hello World",
      "operation": "reverse"
    }
  }
}
```

**Expected Response:**
```json
{
  "mcpVersion": "1.0",
  "type": "execution",
  "data": {
    "success": true,
    "data": {
      "original_text": "Hello World",
      "operation": "reverse",
      "result": "dlroW olleH"
    },
    "error": null
  }
}
```

### 5. Error Handling

**Request:**
```json
{
  "action": "execute",
  "payload": {
    "tool": "non_existent_tool",
    "arguments": {}
  }
}
```

**Expected Response:**
```json
{
  "mcpVersion": "1.0",
  "type": "execution",
  "data": {
    "success": false,
    "data": null,
    "error": "Tool 'non_existent_tool' not found"
  }
}
```

## Testing

### Run Test Suite

Execute the comprehensive test client:

```bash
python test_client.py
```

**Expected Output:**
```
************************************************************
MCP WEATHER SERVER - TEST SUITE
Author: Cavin Otieno
************************************************************

============================================================
TEST 1: TOOL DISCOVERY
============================================================
Request: 'Do you have a tool for weather?'
------------------------------------------------------------
Response:
{
  "mcpVersion": "1.0",
  "type": "discovery",
  "data": {
    "tools": [...]
  }
}

============================================================
TEST 2: WEATHER TOOL EXECUTION
============================================================
Request: 'Please execute weather tool for location San Francisco'
------------------------------------------------------------
Response:
{
  "mcpVersion": "1.0",
  "type": "execution",
  "data": {
    "success": true,
    "data": {
      "location": "San Francisco",
      "temperature": 22,
      "units": "celsius",
      "condition": "Partly Cloudy",
      "humidity": 65,
      "wind_speed": "15 km/h"
    },
    "error": null
  }
}

...

============================================================
TEST SUMMARY
============================================================
[PASS] Tool Discovery
[PASS] Weather Execution
[PASS] Calculator Execution
[PASS] Text Processor
[PASS] Error Handling
[PASS] Get Tool Info
============================================================
```

### Unit Tests with pytest

```bash
# Install pytest
pip install pytest

# Run tests
pytest test_client.py -v
```

### Manual Testing

Test tool discovery:
```bash
echo '{"action": "discover"}' | python mcp_server.py
```

Test weather execution:
```bash
echo '{"action": "execute", "payload": {"tool": "get_weather", "arguments": {"location": "Tokyo"}}}' | python mcp_server.py
```

Test calculator:
```bash
echo '{"action": "execute", "payload": {"tool": "calculate", "arguments": {"expression": "100 / 5"}}}' | python mcp_server.py
```

## Project Structure

```
mcp-weather-server/
├── mcp_server.py        # Main MCP server implementation
├── test_client.py       # Comprehensive test suite
├── requirements.txt     # Dependencies (minimal)
├── README.md           # This file
└── .git/              # Git repository
```

## Extending the Server

Add new tools by registering them in the `_register_builtin_tools` method:

```python
def _register_builtin_tools(self) -> None:
    super()._register_builtin_tools()

    self.register_tool(Tool(
        name="my_new_tool",
        description="Description of what the tool does",
        input_schema={
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "..."}
            },
            "required": ["param1"]
        },
        tool_type="custom",
        handler=self._handle_my_new_tool
    ))

def _handle_my_new_tool(self, args: Dict[str, Any]) -> Dict[str, Any]:
    # Implement tool logic here
    return {"result": "..."}
```

## Security Considerations

- **Input Validation**: The calculator tool only allows safe characters (+-*/.() 0-9)
- **No External Network Calls**: All tools run locally by default
- **Sandboxed Execution**: Tool handlers run in controlled environment

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please ensure all tests pass before submitting pull requests.

---

**Author:** Cavin Otieno
**GitHub:** https://github.com/OumaCavin/mcp-weather-server