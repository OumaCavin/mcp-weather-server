"""
MCP Web Server - HTTP Interface for MCP Server
Author: Cavin Otieno
License: MIT

This module provides a web interface for the MCP server, enabling HTTP-based
tool discovery and execution with comprehensive error handling.
"""

from flask import Flask, request, jsonify
import json
import logging
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MCPWebServer')

app = Flask(__name__)

# Import MCP server components
try:
    from mcp_server import MCPServer, create_response, handle_request
    server = MCPServer()
    logger.info("MCP Server initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize MCP Server: {str(e)}")
    server = None


def require_server(f):
    """Decorator to ensure MCP server is initialized."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if server is None:
            logger.error("Request received but MCP server not initialized")
            return jsonify({
                "error": "Server initialization failed",
                "message": "MCP server is not available. Please check server logs."
            }), 503
        return f(*args, **kwargs)
    return decorated_function


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    logger.warning(f"404 error: {request.path}")
    return jsonify({
        "error": "Endpoint not found",
        "message": f"The requested endpoint {request.path} does not exist",
        "available_endpoints": ["/", "/api/discover", "/api/execute", "/api/health"]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred. Please try again later."
    }), 500


@app.errorhandler(Exception)
def handle_exception(error):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(error)}")
    return jsonify({
        "error": "Unhandled exception",
        "message": str(error)
    }), 500


@app.route('/')
def index():
    """Serve the MCP Web Interface."""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Weather Server - Web Interface | Cavin Otieno</title>
    <meta name="description" content="A Model Context Protocol server for AI tool discovery and execution. Developed by Cavin Otieno.">
    <meta name="author" content="Cavin Otieno">
    <meta name="copyright" content="Copyright (c) 2024 Cavin Otieno">
    <link rel="canonical" href="https://github.com/OumaCavin/mcp-weather-server">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); min-height: 100vh; padding: 20px; color: #e0e0e0; }
        .container { max-width: 900px; margin: 0 auto; }
        .card { background: rgba(255,255,255,0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 30px; margin-bottom: 20px; }
        h1 { color: #00d9ff; margin-bottom: 10px; font-size: 2em; text-shadow: 0 0 20px rgba(0,217,255,0.3); }
        h2 { color: #fff; margin-bottom: 20px; font-size: 1.5em; border-bottom: 2px solid #00d9ff; padding-bottom: 10px; }
        h3 { color: #00d9ff; margin: 20px 0 10px; font-size: 1.2em; }
        .badge { display: inline-block; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: 600; margin-right: 10px; margin-bottom: 10px; }
        .badge-python { background: #3776AB; color: white; }
        .badge-mcp { background: #4CAF50; color: white; }
        .badge-mit { background: #FF9800; color: white; }
        .badge-version { background: #9c27b0; color: white; }
        p { color: #b0b0b0; line-height: 1.6; margin-bottom: 15px; }
        pre { background: #0d1117; color: #c9d1d9; padding: 20px; border-radius: 8px; overflow-x: auto; font-family: 'Fira Code', 'Monaco', 'Menlo', monospace; font-size: 14px; line-height: 1.6; border: 1px solid #30363d; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #fff; font-weight: 600; }
        select, input, textarea { width: 100%; padding: 12px; border: 2px solid #30363d; border-radius: 8px; font-size: 16px; background: #0d1117; color: #c9d1d9; transition: border-color 0.3s; }
        select:focus, input:focus, textarea:focus { outline: none; border-color: #00d9ff; }
        textarea { min-height: 120px; font-family: monospace; }
        .btn { background: linear-gradient(135deg, #00d9ff 0%, #0099cc 100%); color: #0d1117; border: none; padding: 15px 30px; border-radius: 8px; font-size: 16px; font-weight: 700; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; width: 100%; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(0,217,255,0.4); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        #response { background: #0d1117; border: 2px solid #30363d; border-radius: 8px; padding: 20px; min-height: 150px; font-family: monospace; white-space: pre-wrap; color: #c9d1d9; }
        .tool-card { background: rgba(0,217,255,0.1); border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 4px solid #00d9ff; }
        .tool-name { font-size: 18px; font-weight: 700; color: #00d9ff; margin-bottom: 5px; }
        .tool-desc { color: #b0b0b0; margin-bottom: 10px; }
        .tool-params { font-family: monospace; font-size: 14px; color: #888; }
        .success { border-left-color: #4CAF50; }
        .error { border-left-color: #f44336; }
        .loading { display: inline-block; width: 20px; height: 20px; border: 3px solid #30363d; border-top: 3px solid #00d9ff; border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .feature { background: rgba(0,217,255,0.1); padding: 20px; border-radius: 12px; text-align: center; border: 1px solid rgba(0,217,255,0.2); }
        .feature-icon { font-size: 2em; margin-bottom: 10px; }
        .feature-title { font-weight: 600; color: #fff; }
        .api-section { background: rgba(0,217,255,0.05); border-radius: 8px; padding: 15px; margin-bottom: 15px; border: 1px solid rgba(0,217,255,0.1); }
        .api-method { display: inline-block; padding: 5px 10px; border-radius: 5px; font-weight: 700; font-size: 12px; margin-right: 10px; }
        .get { background: #4CAF50; color: white; }
        .post { background: #2196F3; color: white; }
        .api-endpoint { font-family: monospace; font-size: 14px; color: #c9d1d9; }
        .attribution { text-align: center; padding: 30px; background: rgba(0,0,0,0.3); border-radius: 12px; margin-top: 20px; }
        .attribution h3 { color: #00d9ff; margin-bottom: 15px; border: none; padding: 0; }
        .attribution p { color: #888; font-size: 14px; }
        .attribution a { color: #00d9ff; text-decoration: none; }
        .attribution a:hover { text-decoration: underline; }
        .author-card { display: inline-block; background: rgba(0,217,255,0.1); padding: 20px 30px; border-radius: 12px; text-align: center; border: 1px solid rgba(0,217,255,0.2); }
        .author-avatar { width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, #00d9ff, #0099cc); display: flex; align-items: center; justify-content: center; font-size: 32px; font-weight: bold; color: #0d1117; margin: 0 auto 15px; }
        .author-name { font-size: 20px; font-weight: 700; color: #fff; margin-bottom: 5px; }
        .author-username { color: #00d9ff; font-size: 14px; }
        .author-email { color: #888; font-size: 12px; margin-top: 5px; }
        .license-badge { background: rgba(255,152,0,0.2); color: #FF9800; padding: 5px 15px; border-radius: 20px; font-size: 12px; display: inline-block; margin-top: 10px; }
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
                <span class="badge badge-version">v1.0.0</span>
            </div>
            <p>A Model Context Protocol server enabling AI models to discover and execute external tools through a web interface. This demo shows simulated responses representing the MCP server functionality.</p>
            <p><strong>Developer:</strong> <a href="https://github.com/OumaCavin" target="_blank" style="color: #00d9ff;">Cavin Otieno</a></p>
        </div>

        <div class="card">
            <h2>API Endpoints</h2>
            <div class="api-section">
                <span class="api-method get">GET</span>
                <span class="api-endpoint">/ - Web Interface</span>
            </div>
            <div class="api-section">
                <span class="api-method get">GET</span>
                <span class="api-endpoint">/api/discover - List all available tools</span>
            </div>
            <div class="api-section">
                <span class="api-method post">POST</span>
                <span class="api-endpoint">/api/execute - Execute a tool with arguments</span>
            </div>
            <div class="api-section">
                <span class="api-method get">GET</span>
                <span class="api-endpoint">/api/health - Server health check</span>
            </div>
        </div>

        <div class="card">
            <h2>Available Tools</h2>
            <div id="tools-list">
                <div class="loading" style="margin: 20px auto;"></div>
            </div>
        </div>

        <div class="card">
            <h2>Try It Out</h2>
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
            <h2>Response Preview</h2>
            <div id="response">Select a tool to see a demo response...</div>
        </div>

        <div class="card">
            <h2>Features</h2>
            <div class="features">
                <div class="feature"><div class="feature-icon">&#128300;</div><div class="feature-title">Tool Discovery</div></div>
                <div class="feature"><div class="feature-icon">&#9889;</div><div class="feature-title">Fast Execution</div></div>
                <div class="feature"><div class="feature-icon">&#128274;</div><div class="feature-title">Secure</div></div>
                <div class="feature"><div class="feature-icon">&#128187;</div><div class="feature-title">No Dependencies</div></div>
            </div>
        </div>

        <div class="card">
            <h2>Run Locally</h2>
            <p>To use the full MCP server functionality, run locally with Flask:</p>
            <pre># Clone the repository
git clone https://github.com/OumaCavin/mcp-weather-server.git
cd mcp-weather-server

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install flask

# Run the web server
python web_server.py

# Open http://localhost:5000</pre>
        </div>

        <div class="attribution">
            <h3>Developer Attribution</h3>
            <div class="author-card">
                <div class="author-avatar">CO</div>
                <div class="author-name">Cavin Otieno</div>
                <div class="author-username">@OumaCavin</div>
                <div class="author-email">cavin.otieno012@gmail.com</div>
                <div class="license-badge">MIT License</div>
            </div>
            <p style="margin-top: 20px;">
                <a href="https://github.com/OumaCavin/mcp-weather-server" target="_blank">View on GitHub</a> |
                <a href="https://github.com/OumaCavin" target="_blank">GitHub Profile</a>
            </p>
            <p style="margin-top: 15px; font-size: 12px;">
                &copy; <span id="copyright-year"></span> Cavin Otieno. All rights reserved.<br>
                This project is licensed under the MIT License.
            </p>
        </div>
    </div>

    <script>
        // Set dynamic copyright year
        document.getElementById('copyright-year').textContent = new Date().getFullYear();

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

            if (!tool) {
                responseEl.innerHTML = JSON.stringify({
                    mcpVersion: '1.0',
                    type: 'execution',
                    data: { success: false, data: null, error: 'Please select a tool first' }
                }, null, 2);
                responseEl.className = 'error';
                return;
            }

            btn.disabled = true;
            btn.innerHTML = '<span class="loading"></span> Executing...';

            let arguments = {};

            if (tool === 'get_weather') {
                arguments = {
                    location: document.getElementById('weather-location').value || 'Tokyo',
                    units: document.getElementById('weather-units').value
                };
            } else if (tool === 'calculate') {
                arguments = {
                    expression: document.getElementById('calc-expression').value || '25 * 4 + 10'
                };
            } else if (tool === 'process_text') {
                arguments = {
                    text: document.getElementById('text-content').value || 'Hello World',
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
                responseEl.innerHTML = JSON.stringify({
                    mcpVersion: '1.0',
                    type: 'execution',
                    data: { success: false, data: null, error: 'Error: ' + err.message }
                }, null, 2);
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
@require_server
def discover():
    """Handle tool discovery requests with error handling."""
    logger.info("Processing tool discovery request")
    try:
        request_data = {"action": "discover"}
        response = handle_request(request_data, server)
        logger.info("Tool discovery completed successfully")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Tool discovery failed: {str(e)}")
        return jsonify({
            "error": "Discovery failed",
            "message": str(e)
        }), 500


@app.route('/api/execute', methods=['POST'])
@require_server
def execute():
    """Handle tool execution requests with comprehensive error handling."""
    logger.info("Processing tool execution request")
    try:
        # Validate request content type
        if not request.is_json:
            logger.error("Invalid content type: expected JSON")
            return jsonify({
                "error": "Invalid request",
                "message": "Content-Type must be application/json"
            }), 400

        data = request.get_json()

        # Validate required fields
        if not data:
            logger.error("Empty request body")
            return jsonify({
                "error": "Invalid request",
                "message": "Request body is required"
            }), 400

        tool_name = data.get('tool')
        if not tool_name:
            logger.error("Missing 'tool' field in request")
            return jsonify({
                "error": "Invalid request",
                "message": "The 'tool' field is required"
            }), 400

        arguments = data.get('arguments', {})

        # Validate arguments type
        if not isinstance(arguments, dict):
            logger.error(f"Invalid arguments type: {type(arguments)}")
            return jsonify({
                "error": "Invalid request",
                "message": "Arguments must be an object/dictionary"
            }), 400

        request_data = {
            "action": "execute",
            "payload": {
                "tool": tool_name,
                "arguments": arguments
            }
        }

        response = handle_request(request_data, server)
        logger.info(f"Tool execution completed for: {tool_name}")
        return jsonify(response)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return jsonify({
            "error": "Invalid JSON",
            "message": f"Failed to parse JSON: {str(e)}"
        }), 400

    except Exception as e:
        logger.error(f"Tool execution failed: {str(e)}")
        return jsonify({
            "error": "Execution failed",
            "message": str(e)
        }), 500


@app.route('/api/health')
@require_server
def health():
    """Health check endpoint with detailed status."""
    logger.info("Health check requested")
    try:
        # Check if server is functional
        tools = server.discover_tools()
        return jsonify({
            "status": "healthy",
            "server": "MCP Weather Server",
            "version": "1.0.0",
            "tools_available": len(tools),
            "uptime": "operational"
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "server": "MCP Weather Server",
            "error": str(e)
        }), 503


if __name__ == '__main__':
    print("Starting MCP Web Server...")
    print("Access the web interface at: http://localhost:5000")
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"Failed to start server: {str(e)}")
        logger.error(f"Server startup failed: {str(e)}")