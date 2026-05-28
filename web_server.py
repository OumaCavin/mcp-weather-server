"""
MCP Web Server - HTTP Interface for MCP Server
Author: Cavin Otieno
License: MIT

This module provides a web interface for the MCP server, enabling HTTP-based
tool discovery and execution.
"""

from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Import MCP server components
from mcp_server import MCPServer, create_response, handle_request

# Initialize MCP server
server = MCPServer()


@app.route('/')
def index():
    """Serve the MCP Web Interface."""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Weather Server - Web Interface</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .card {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        h1 { color: #667eea; margin-bottom: 10px; font-size: 2em; }
        h2 { color: #333; margin-bottom: 20px; font-size: 1.5em; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        .badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        .badge-python { background: #3776AB; color: white; }
        .badge-mcp { background: #4CAF50; color: white; }
        .badge-mit { background: #FF9800; color: white; }
        pre {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 14px;
            line-height: 1.6;
        }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: 600; }
        select, input, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        select:focus, input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea { min-height: 120px; font-family: monospace; }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        #response {
            background: #f8f9fa;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            min-height: 150px;
            font-family: monospace;
            white-space: pre-wrap;
        }
        .tool-card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }
        .tool-name { font-size: 18px; font-weight: 700; color: #667eea; margin-bottom: 5px; }
        .tool-desc { color: #666; margin-bottom: 10px; }
        .tool-params { font-family: monospace; font-size: 14px; color: #888; }
        .success { border-left-color: #4CAF50; }
        .error { border-left-color: #f44336; }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .feature {
            background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }
        .feature-icon { font-size: 2em; margin-bottom: 10px; }
        .feature-title { font-weight: 600; color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>MCP Weather Server</h1>
            <div style="margin-bottom: 20px;">
                <span class="badge badge-python">Python 3.8+</span>
                <span class="badge badge-mcp">MCP 1.0</span>
                <span class="badge badge-mit">MIT License</span>
            </div>
            <p style="color: #666; line-height: 1.6;">
                A Model Context Protocol server that enables AI models to discover and execute external tools.
                This web interface allows you to test all available tools.
            </p>
        </div>

        <div class="card">
            <h2>Available Tools</h2>
            <div id="tools-list">
                <div class="loading" style="margin: 20px auto;"></div>
            </div>
        </div>

        <div class="card">
            <h2>Execute Tool</h2>
            <form id="tool-form">
                <div class="form-group">
                    <label for="tool-select">Select Tool</label>
                    <select id="tool-select" required>
                        <option value="">Choose a tool...</option>
                        <option value="get_weather">Weather Tool</option>
                        <option value="calculate">Calculator Tool</option>
                        <option value="process_text">Text Processor</option>
                    </select>
                </div>

                <div id="get_weather-fields" style="display: none;">
                    <div class="form-group">
                        <label for="weather-location">Location</label>
                        <input type="text" id="weather-location" placeholder="e.g., Tokyo, San Francisco, London">
                    </div>
                    <div class="form-group">
                        <label for="weather-units">Temperature Units</label>
                        <select id="weather-units">
                            <option value="celsius">Celsius</option>
                            <option value="fahrenheit">Fahrenheit</option>
                        </select>
                    </div>
                </div>

                <div id="calculate-fields" style="display: none;">
                    <div class="form-group">
                        <label for="calc-expression">Mathematical Expression</label>
                        <input type="text" id="calc-expression" placeholder="e.g., 25 * 4 + 10">
                    </div>
                </div>

                <div id="process_text-fields" style="display: none;">
                    <div class="form-group">
                        <label for="text-content">Text</label>
                        <textarea id="text-content" placeholder="Enter text to process..."></textarea>
                    </div>
                    <div class="form-group">
                        <label for="text-operation">Operation</label>
                        <select id="text-operation">
                            <option value="uppercase">UPPERCASE</option>
                            <option value="lowercase">lowercase</option>
                            <option value="reverse">Reverse</option>
                            <option value="length">Get Length</option>
                        </select>
                    </div>
                </div>

                <button type="submit" class="btn" id="submit-btn">Execute Tool</button>
            </form>
        </div>

        <div class="card">
            <h2>Response</h2>
            <div id="response">Select a tool and click Execute to see the result here...</div>
        </div>

        <div class="card">
            <h2>Features</h2>
            <div class="features">
                <div class="feature">
                    <div class="feature-icon">&#128300;</div>
                    <div class="feature-title">Tool Discovery</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">&#9889;</div>
                    <div class="feature-title">Fast Execution</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">&#128274;</div>
                    <div class="feature-title">Secure</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">&#128187;</div>
                    <div class="feature-title">No Dependencies</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Load tools on page load
        fetch('/api/discover')
            .then(r => r.json())
            .then(data => {
                const tools = data.data.tools;
                let html = '';
                tools.forEach(tool => {
                    const params = Object.keys(tool.inputSchema.properties || {}).join(', ');
                    html += `
                        <div class="tool-card">
                            <div class="tool-name">${tool.name}</div>
                            <div class="tool-desc">${tool.description}</div>
                            <div class="tool-params">Parameters: ${params || 'none'}</div>
                        </div>
                    `;
                });
                document.getElementById('tools-list').innerHTML = html;
            });

        // Tool selection handler
        document.getElementById('tool-select').addEventListener('change', function() {
            const tool = this.value;
            document.querySelectorAll('[id$="-fields"]').forEach(el => el.style.display = 'none');
            if (tool) {
                const fieldsEl = document.getElementById(tool + '-fields');
                if (fieldsEl) fieldsEl.style.display = 'block';
            }
        });

        // Form submission
        document.getElementById('tool-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const tool = document.getElementById('tool-select').value;
            const btn = document.getElementById('submit-btn');
            const responseEl = document.getElementById('response');

            btn.disabled = true;
            btn.innerHTML = '<span class="loading"></span> Executing...';

            let arguments = {};

            if (tool === 'get_weather') {
                arguments = {
                    location: document.getElementById('weather-location').value || 'Unknown',
                    units: document.getElementById('weather-units').value
                };
            } else if (tool === 'calculate') {
                arguments = {
                    expression: document.getElementById('calc-expression').value
                };
            } else if (tool === 'process_text') {
                arguments = {
                    text: document.getElementById('text-content').value,
                    operation: document.getElementById('text-operation').value
                };
            }

            fetch('/api/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tool, arguments })
            })
            .then(r => r.json())
            .then(data => {
                responseEl.innerHTML = JSON.stringify(data, null, 2);
                responseEl.className = data.data.success ? 'success' : 'error';
            })
            .catch(err => {
                responseEl.innerHTML = 'Error: ' + err.message;
                responseEl.className = 'error';
            })
            .finally(() => {
                btn.disabled = false;
                btn.innerHTML = 'Execute Tool';
            });
        });
    </script>
</body>
</html>
'''


@app.route('/api/discover')
def discover():
    """Handle tool discovery requests."""
    request_data = {"action": "discover"}
    response = handle_request(request_data, server)
    return jsonify(response)


@app.route('/api/execute', methods=['POST'])
def execute():
    """Handle tool execution requests."""
    data = request.get_json()
    tool_name = data.get('tool')
    arguments = data.get('arguments', {})

    request_data = {
        "action": "execute",
        "payload": {
            "tool": tool_name,
            "arguments": arguments
        }
    }

    response = handle_request(request_data, server)
    return jsonify(response)


@app.route('/api/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "server": "MCP Weather Server",
        "version": "1.0.0"
    })


if __name__ == '__main__':
    print("Starting MCP Web Server...")
    print("Access the web interface at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)