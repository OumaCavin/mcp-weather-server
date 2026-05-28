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
- [Prerequisites](#prerequisites)
- [Clone and Setup](#clone-and-setup)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Extending the Server](#extending-the-server)
- [Security Considerations](#security-considerations)
- [Deployment](#deployment)
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

## Prerequisites

Before you begin, ensure you have the following installed on your system:

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python3 | 3.8+ | Required for all modules |
| pip | Latest | For installing dependencies (optional) |
| Git | Any recent version | For cloning the repository |

### System-Specific Installation

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

**macOS:**
```bash
brew install python3 git
```

**Windows:**
1. Download Python from https://www.python.org/downloads/
2. Download Git from https://git-scm.com/download/win

### Verify Installation

```bash
# Verify Python
python3 --version

# Verify Git
git --version
```

### Required API Keys

This project does **not** require any API keys. All tools use simulated data and run locally without external dependencies.

---

## Optional Tools

The following tools are optional but recommended:

| Tool | Purpose | Installation |
|------|---------|--------------|
| pytest | For running unit tests | `pip install pytest` |
| pytest-asyncio | For async test support | `pip install pytest-asyncio` |

---

## Clone and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/OumaCavin/mcp-weather-server.git
cd mcp-weather-server
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.\.venv\Scripts\activate
```

### 3. Verify Setup

```bash
# Verify these files exist:
ls -la

# Expected output should include:
# - mcp_server.py
# - test_client.py
# - requirements.txt
# - README.md
# - .gitignore
```

### 4. Set Up Environment Variables (Optional)

This project does not require environment variables. All configuration is handled internally.

---

## Quick Start

### Running the Server

**Important:** The server reads JSON requests from stdin and outputs JSON responses. It will appear to "hang" if run without input - this is expected behavior. The server is waiting for input.

**Option 1: Run with a test request (recommended for first-time users)**

```bash
# Test tool discovery - this will exit immediately after showing results
echo '{"action": "discover"}' | python3 mcp_server.py

# Or test weather tool
echo '{"action": "execute", "payload": {"tool": "get_weather", "arguments": {"location": "Tokyo"}}}' | python3 mcp_server.py
```

**Option 2: Run the test suite (recommended)**

```bash
# Run all tests at once - the server will work automatically
python3 test_client.py
```

**Option 3: Interactive mode (for advanced users)**

1. **Start the server** - it will wait for input
   ```bash
   python3 mcp_server.py
   ```
2. **Type or paste** a JSON request
3. **Press Enter** to send
4. **View the response**
5. **Press Ctrl+C** to exit

2. **Test Tool Discovery**

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
+-- mcp_server.py        # Main MCP server (CLI interface)
|
+-- web_server.py        # Flask web interface (HTTP API)
|
+-- test_client.py       # Comprehensive test suite
|
+-- requirements.txt     # Python dependencies
|
+-- README.md           # This file
|
+-- .gitignore          # Git ignore patterns
|
+-- dist/               # Deployment-ready files
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

## Deployment

### Live Demo

Access the deployed MCP Weather Server demo: **https://0sfry4l9qbls.space.minimax.io**

This is a static demo showing the MCP server capabilities. For full functionality, run locally or deploy to a cloud platform.

### Local Deployment with Web Interface

For the complete web interface with API endpoints:

```bash
# Clone and setup
git clone https://github.com/OumaCavin/mcp-weather-server.git
cd mcp-weather-server

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install flask

# Run the web server
python web_server.py

# Access at http://localhost:5000
```

---

### Platform-Specific Deployment Guides

#### 1. Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp_server.py web_server.py .

EXPOSE 5000

CMD ["python", "web_server.py"]
```

**Build and Run:**
```bash
# Build image
docker build -t mcp-weather-server .

# Run container
docker run -d -p 5000:5000 --name mcp-server mcp-weather-server
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  mcp-server:
    build: .
    ports:
      - "5000:5000"
    restart: unless-stopped
```

---

#### 2. Heroku Deployment

**Requirements:**
- Heroku CLI installed
- Git initialized

**Steps:**
```bash
# Create Procfile
echo "web: python web_server.py" > Procfile

# Login to Heroku
heroku login

# Create Heroku app
heroku create mcp-weather-server

# Set buildpack for Python
heroku buildpacks:set heroku/python

# Deploy
git push heroku main

# Open app
heroku open
```

**runtime.txt (specify Python version):**
```
python-3.11.0
```

---

#### 3. Railway Deployment

**Steps:**
1. Go to [Railway.app](https://railway.app)
2. Connect your GitHub repository
3. Select the repository
4. Railway will auto-detect Python and deploy
5. Set start command: `python web_server.py`

---

#### 4. Render Deployment

**Steps:**
1. Go to [Render.com](https://render.com)
2. Create a New Web Service
3. Connect your GitHub repository
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python web_server.py`
5. Deploy

---

#### 5. Vercel Deployment

Create `vercel.json`:
```json
{
  "builds": [
    {
      "src": "web_server.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "web_server.py"
    }
  ]
}
```

**Steps:**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

---

#### 6. AWS Lambda Deployment

**lambda_function.py:**
```python
import json
from mcp_server import MCPServer, handle_request

server = MCPServer()

def lambda_handler(event, context):
    body = json.loads(event.get('body', '{}'))
    response = handle_request(body, server)
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
```

**Requirements:**
```bash
pip install flask
zip -r deployment.zip lambda_function.py mcp_server.py
aws lambda create-function --function-name mcp-server ...
```

---

#### 7. Google Cloud Run Deployment

**Steps:**
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/mcp-server

# Deploy to Cloud Run
gcloud run deploy mcp-server --image gcr.io/PROJECT_ID/mcp-server --platform managed
```

---

#### 8. Azure App Service Deployment

**Steps:**
1. Create Web App in Azure Portal
2. Configure deployment method (GitHub/Local Git/FTP)
3. Set startup command: `python web_server.py`

**Azure CLI:**
```bash
az webapp create --resource-group myGroup --plan myPlan --name mcp-server
az webapp up --name mcp-server --location eastus
```

---

### API Endpoints (Web Server)

When deployed with `web_server.py`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/api/discover` | GET | List all available tools |
| `/api/execute` | POST | Execute a tool |
| `/api/health` | GET | Server health check |

**Example API Usage:**
```bash
# Discover tools
curl https://your-server.com/api/discover

# Execute tool
curl -X POST https://your-server.com/api/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "get_weather", "arguments": {"location": "Tokyo"}}'
```

---

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `5000` |
| `DEBUG` | Enable debug mode | `False` |

---

### Health Monitoring

The server provides a `/api/health` endpoint for monitoring:

```json
{
  "status": "healthy",
  "server": "MCP Weather Server",
  "version": "1.0.0"
}
```

---

### Troubleshooting

**Port Already in Use:**
```bash
# Find process using port 5000
lsof -i :5000
# Kill the process
kill -9 PID
```

**Dependencies Not Installing:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Server Not Responding:**
- Check firewall settings
- Verify port is open
- Check logs for errors

---

### Redeployment Checklist

When redeploying to new platforms:

- [ ] Update `requirements.txt` with all dependencies
- [ ] Test locally with `python web_server.py`
- [ ] Verify health endpoint responds
- [ ] Check API endpoints work correctly
- [ ] Update README if new deployment method added

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