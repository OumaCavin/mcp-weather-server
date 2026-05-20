#!/usr/bin/env python3
"""
MCP Test Client - Tests the MCP Weather Server
Author: Cavin Otieno
License: MIT

This client demonstrates the MCP server interaction pattern:
1. Tool Discovery - Query available tools
2. Tool Execution - Run specific tools with arguments
"""

import json
import sys
from typing import Any, Dict
import subprocess


def run_mcp_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute an MCP request by running the server with the request.

    Args:
        request: MCP request dictionary

    Returns:
        Response dictionary from the server
    """
    try:
        result = subprocess.run(
            [sys.executable, "mcp_server.py"],
            input=json.dumps(request),
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return {
                "error": True,
                "message": f"Server error: {result.stderr}",
                "stdout": result.stdout
            }

        return json.loads(result.stdout)

    except subprocess.TimeoutExpired:
        return {"error": True, "message": "Server request timed out"}
    except Exception as e:
        return {"error": True, "message": str(e)}


def test_discovery():
    """Test 1: Tool Discovery - List all available tools."""
    print("=" * 60)
    print("TEST 1: TOOL DISCOVERY")
    print("=" * 60)
    print("Request: 'Do you have a tool for weather?'")
    print("-" * 60)

    request = {"action": "discover"}
    response = run_mcp_request(request)

    print("Response:")
    print(json.dumps(response, indent=2))
    print()

    return response


def test_weather_execution():
    """Test 2: Weather Tool Execution."""
    print("=" * 60)
    print("TEST 2: WEATHER TOOL EXECUTION")
    print("=" * 60)
    print("Request: 'Please execute weather tool for location San Francisco'")
    print("-" * 60)

    request = {
        "action": "execute",
        "payload": {
            "tool": "get_weather",
            "arguments": {
                "location": "San Francisco",
                "units": "celsius"
            }
        }
    }
    response = run_mcp_request(request)

    print("Response:")
    print(json.dumps(response, indent=2))
    print()

    return response


def test_calculator_execution():
    """Test 3: Calculator Tool Execution."""
    print("=" * 60)
    print("TEST 3: CALCULATOR TOOL EXECUTION")
    print("=" * 60)
    print("Request: 'Please calculate 25 * 4 + 10'")
    print("-" * 60)

    request = {
        "action": "execute",
        "payload": {
            "tool": "calculate",
            "arguments": {
                "expression": "25 * 4 + 10"
            }
        }
    }
    response = run_mcp_request(request)

    print("Response:")
    print(json.dumps(response, indent=2))
    print()

    return response


def test_text_processor():
    """Test 4: Text Processor Tool Execution."""
    print("=" * 60)
    print("TEST 4: TEXT PROCESSOR TOOL EXECUTION")
    print("=" * 60)
    print("Request: 'Reverse the text Hello World'")
    print("-" * 60)

    request = {
        "action": "execute",
        "payload": {
            "tool": "process_text",
            "arguments": {
                "text": "Hello World",
                "operation": "reverse"
            }
        }
    }
    response = run_mcp_request(request)

    print("Response:")
    print(json.dumps(response, indent=2))
    print()

    return response


def test_error_handling():
    """Test 5: Error Handling - Non-existent tool."""
    print("=" * 60)
    print("TEST 5: ERROR HANDLING")
    print("=" * 60)
    print("Request: 'Execute non-existent tool get_time'")
    print("-" * 60)

    request = {
        "action": "execute",
        "payload": {
            "tool": "get_time",
            "arguments": {}
        }
    }
    response = run_mcp_request(request)

    print("Response:")
    print(json.dumps(response, indent=2))
    print()

    return response


def test_get_tool_info():
    """Test 6: Get specific tool information."""
    print("=" * 60)
    print("TEST 6: GET TOOL INFORMATION")
    print("=" * 60)
    print("Request: 'Get details for weather tool'")
    print("-" * 60)

    request = {
        "action": "get_tool",
        "payload": {
            "tool": "get_weather"
        }
    }
    response = run_mcp_request(request)

    print("Response:")
    print(json.dumps(response, indent=2))
    print()

    return response


def run_all_tests():
    """Run all MCP server tests."""
    print()
    print("*" * 60)
    print("MCP WEATHER SERVER - TEST SUITE")
    print("Author: Cavin Otieno")
    print("*" * 60)
    print()

    tests = [
        ("Tool Discovery", test_discovery),
        ("Weather Execution", test_weather_execution),
        ("Calculator Execution", test_calculator_execution),
        ("Text Processor", test_text_processor),
        ("Error Handling", test_error_handling),
        ("Get Tool Info", test_get_tool_info)
    ]

    results = {}
    for name, test_func in tests:
        try:
            response = test_func()
            results[name] = "PASS" if "error" not in response else "FAIL"
        except Exception as e:
            results[name] = f"ERROR: {str(e)}"

    # Print summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, result in results.items():
        status = "✓" if result == "PASS" else "✗"
        print(f"{status} {name}: {result}")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()