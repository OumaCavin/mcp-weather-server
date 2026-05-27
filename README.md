# MCP Weather Server

![MCP Architecture Banner](https://cdn.dida.do/blog/mcp-architecture-(2).png)

---

## Technology Stack

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Protocol](https://img.shields.io/badge/Protocol-MCP%201.0-blue?style=for-the-badge)
![Standard](https://img.shields.io/badge/Standard-JSON%20RPC-orange?style=for-the-badge)

---

**Author:** Cavin Otieno

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Extending the Server](#extending-the-server)
- [Security Considerations](#security-considerations)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

A Model Context Protocol (MCP) server implementation that enables AI models and agents to discover and execute external tools in a secure and predictable way.

### What is MCP?

The Model Context Protocol is a standardized specification that allows AI models and agents to interact with external tools and services. This project implements the **server-side** of this interaction, allowing AI systems to:

1. **Discover Tools** - Query available tools on the server
2. **Execute Tools** - Run specific tools with provided arguments

### How MCP Works

```
+-------------------+                     +-----------------------+
|                   |                     |                       |
|    AI Model       |                     |     MCP Server        |
|                   |                     |                       |
+--------+----------+                     +--------+--------------+
         |                                        |
         |  1. Discovery Request                  |
         |  "Do you have tools available?"       |
         +-------------------------------------->
         |                                        |
         |  2. Tool List Response                 |
         |  [get_weather, calculate, ...]        |
         <--------------------------------------+
         |                                        |
         |  3. Execution Request                 |
         |  "Run get_weather for 'Tokyo'"        |
         +-------------------------------------->
         |                                        |
         |  4. Tool Result                        |
         |  {temp: 22, condition: "Sunny"}        |
         <--------------------------------------+
         |                                        |
```

---

## Features

- **Tool Discovery**: List all available tools on the server
- **Tool Execution**: Execute any registered tool with custom arguments
- **Multiple Tool Types**: Weather, Calculator, Text Processor
- **JSON RPC Protocol**: Standardized request/response format
- **Error Handling**: Graceful handling of invalid requests
- **Extensible**: Easy to add new tools
- **No External Dependencies**: Uses only Python standard library

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Git

### Step-by-Step Installation

1. **Clone the Repository**

```bash
git clone https://github.com/OumaCavin/mcp-weather-server.git
cd mcp-weather-server
```

2. **Verify Python Installation**

```bash
# Check Python version (should be 3.8+)
python3 --version

# If Python is not installed, install it:
# Ubuntu/Debian:
sudo apt update && sudo apt install python3 python3-pip

# macOS:
brew install python3

# Windows:
# Download from https://www.python.org/downloads/
```

3. **Verify Project Files**

```bash
# After cloning, verify these files exist:
ls -la

# Expected output:
# -rw-r--r--  mcp_server.py
# -rw-r--r--  test_client.py
# -rw-r--r--  requirements.txt
# -rw-r--r--  README.md
# -rw-r--r--  .gitignore
```

---

## Quick Start

### Running the Server

The server reads JSON requests from stdin and outputs JSON responses.

1. **Start the Server**

```bash
python3 mcp_server.py
```

2. **Test Tool Discovery**

```bash
echo '{"action": "discover"}' | python3 mcp_server.py
```

3. **Test Weather Tool**

```bash
echo '{"action": "execute", "payload": {"tool": "get_weather", "arguments": {"location": "Tokyo", "units": "celsius"}}}' | python3 mcp_server.py
```

### Available Tools

| Tool Name | Description | Required Parameters |
|-----------|-------------|---------------------|
| `get_weather` | Get current weather for a location | `location` (string) |
| `calculate` | Perform arithmetic calculations | `expression` (string) |
| `process_text` | Transform text (uppercase, lowercase, reverse, length) | `text`, `operation` |

---

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
        "inputSchema": {
          "type": "object",
          "properties": {
            "expression": {
              "type": "string",
              "description": "Mathematical expression to evaluate"
            }
          },
          "required": ["expression"]
        },
        "toolType": "calculator"
      },
      {
        "name": "process_text",
        "description": "Process and transform text (uppercase, lowercase, reverse, length)",
        "inputSchema": {
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

---

## Testing

### Run Test Suite

Execute the comprehensive test client to verify all functionality:

```bash
# Run all tests
python3 test_client.py
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

============================================================
TEST 3: CALCULATOR TOOL EXECUTION
============================================================
Request: 'Please calculate 25 * 4 + 10'
------------------------------------------------------------
Response:
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

============================================================
TEST 4: TEXT PROCESSOR TOOL EXECUTION
============================================================
Request: 'Reverse the text Hello World'
------------------------------------------------------------
Response:
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

============================================================
TEST 5: ERROR HANDLING
============================================================
Request: 'Execute non-existent tool get_time'
------------------------------------------------------------
Response:
{
  "mcpVersion": "1.0",
  "type": "execution",
  "data": {
    "success": false,
    "data": null,
    "error": "Tool 'get_time' not found"
  }
}

============================================================
TEST 6: GET TOOL INFORMATION
============================================================
Request: 'Get details for weather tool'
------------------------------------------------------------
Response:
{
  "mcpVersion": "1.0",
  "type": "tool_info",
  "data": {
    "name": "get_weather",
    "description": "Get current weather information for a specified location",
    "inputSchema": {...},
    "toolType": "weather"
  }
}

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

### Unit Tests with pytest (Optional)

```bash
# Install pytest (optional, not required for basic testing)
pip3 install pytest pytest-asyncio

# Run tests
pytest test_client.py -v
```

### Manual Testing Examples

Test tool discovery:
```bash
echo '{"action": "discover"}' | python3 mcp_server.py
```

Test weather execution:
```bash
echo '{"action": "execute", "payload": {"tool": "get_weather", "arguments": {"location": "Tokyo"}}}' | python3 mcp_server.py
```

Test calculator:
```bash
echo '{"action": "execute", "payload": {"tool": "calculate", "arguments": {"expression": "100 / 5"}}}' | python3 mcp_server.py
```

Test text processing:
```bash
echo '{"action": "execute", "payload": {"tool": "process_text", "arguments": {"text": "Hello", "operation": "uppercase"}}}' | python3 mcp_server.py
```

---

## Project Structure

```
mcp-weather-server/
|
+-- mcp_server.py        # Main MCP server implementation
|
+-- test_client.py       # Comprehensive test suite
|
+-- requirements.txt     # Dependencies (minimal, standard library only)
|
+-- README.md           # This file
|
+-- .gitignore          # Git ignore patterns
|
+-- .git/               # Git repository
```

---

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

---

## Security Considerations

- **Input Validation**: The calculator tool only allows safe characters (+-*/.() 0-9)
- **No External Network Calls**: All tools run locally by default
- **Sandboxed Execution**: Tool handlers run in controlled environment

---

## Contributing

Contributions welcome! Please follow these steps:

1. **Fork the Repository**
2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. **Make Your Changes**
4. **Run Tests**
   ```bash
   python3 test_client.py
   ```
5. **Commit Changes** (Follow conventional commit format)
   ```bash
   git commit -m "feat(tool): add my new tool"
   ```
6. **Push to Your Fork**
   ```bash
   git push origin feature/my-new-feature
   ```
7. **Create Pull Request**

---

## License

<details>
<summary><b>MIT License</b></summary>

Copyright (c) 2024 Cavin Otieno

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

</details>

---

## Support

For questions or support, please open an issue on GitHub.

---

**Author:** Cavin Otieno
**GitHub:** https://github.com/OumaCavin/mcp-weather-server
**License:** MIT