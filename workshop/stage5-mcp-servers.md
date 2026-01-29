# Stage 5: MCP Server Development

**Time:** 15:00–15:45 (45 minutes)
**Goal:** Build a custom MCP server that extends Claude's capabilities for your domain.

## Learning Objectives

By the end of this stage, you'll understand:
- MCP protocol fundamentals (JSON-RPC over stdio)
- How to implement MCP tools with proper schemas
- Tool discovery and invocation lifecycle
- Error handling and rich diagnostics
- Integration with Claude Code

## What You're Building

An **API Development Toolkit** MCP server with four tools:
1. `validate_endpoint` - HTTP endpoint validation
2. `generate_test_data` - Schema-based test data generation
3. `compare_api_versions` - OpenAPI spec diffing
4. `check_security` - Security vulnerability scanning

## MCP Protocol Overview

### Communication Model

```
Claude Code ←──────→ MCP Server
            JSON-RPC
            (stdio)
```

### Message Flow

1. **Initialize**: Claude asks what server can do
2. **Tool Discovery**: Server lists available tools
3. **Tool Invocation**: Claude calls a specific tool
4. **Response**: Server returns results

### Protocol Structure

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "validate_endpoint",
    "arguments": {"url": "http://localhost:5000/api/health"}
  }
}
```

## Step 1: Set Up the MCP Server Project

Create the project structure:

```bash
mkdir -p ~/.claude/mcp-servers/api-toolkit
cd ~/.claude/mcp-servers/api-toolkit
```

Create `requirements.txt`:

```txt
httpx>=0.27.0
jsonschema>=4.21.0
pydantic>=2.0.0
faker>=20.0.0
```

Install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 2: Implement the Core Server

Create `server.py`:

```python
#!/usr/bin/env python3
"""
API Development Toolkit MCP Server
Provides tools for API validation, testing, and security
"""

import json
import sys
import traceback
from typing import Any, Dict, List
import httpx
from jsonschema import validate, ValidationError, Draft7Validator
from faker import Faker
import re

fake = Faker()

# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

def validate_endpoint(url: str, method: str = "GET", expected_status: int = 200,
                     expected_schema: Dict = None, timeout: float = 5.0) -> Dict[str, Any]:
    """
    Validates an HTTP endpoint against expected behavior

    Returns structured validation results with detailed diagnostics
    """
    try:
        # Make the request
        if method.upper() == "GET":
            response = httpx.get(url, timeout=timeout)
        elif method.upper() == "POST":
            response = httpx.post(url, json={}, timeout=timeout)
        else:
            return {"success": False, "error": f"Unsupported method: {method}"}

        result = {
            "url": url,
            "method": method,
            "status_code": response.status_code,
            "status_match": response.status_code == expected_status,
            "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2),
            "success": True
        }

        # Check status code
        if response.status_code != expected_status:
            result["success"] = False
            result["error"] = f"Status mismatch: expected {expected_status}, got {response.status_code}"
            result["response_preview"] = response.text[:200]
            return result

        # Validate schema if provided
        if expected_schema:
            try:
                response_json = response.json()
                validate(instance=response_json, schema=expected_schema)
                result["schema_valid"] = True
                result["response_body"] = response_json
            except ValidationError as e:
                result["success"] = False
                result["schema_valid"] = False
                result["error"] = f"Schema validation failed: {e.message}"
                result["error_path"] = list(e.path)
                result["response_body"] = response.text[:500]
        else:
            result["response_preview"] = response.text[:200]

        return result

    except httpx.RequestError as e:
        return {
            "url": url,
            "success": False,
            "error": f"Request failed: {str(e)}",
            "error_type": type(e).__name__
        }
    except Exception as e:
        return {
            "url": url,
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }


def generate_test_data(schema: Dict[str, Any], count: int = 1,
                      include_edge_cases: bool = True) -> Dict[str, Any]:
    """
    Generates realistic test data matching a JSON schema

    Returns valid data plus edge cases for comprehensive testing
    """
    try:
        # Validate the schema itself
        Draft7Validator.check_schema(schema)

        results = {
            "valid_cases": [],
            "edge_cases": [],
            "schema": schema
        }

        # Generate valid test data
        for _ in range(count):
            data = _generate_from_schema(schema)
            results["valid_cases"].append(data)

        # Generate edge cases
        if include_edge_cases:
            results["edge_cases"] = _generate_edge_cases(schema)

        return results

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate test data: {str(e)}",
            "traceback": traceback.format_exc()
        }


def _generate_from_schema(schema: Dict[str, Any]) -> Any:
    """Recursively generate data matching schema"""
    schema_type = schema.get("type", "string")

    if schema_type == "object":
        result = {}
        properties = schema.get("properties", {})
        for prop_name, prop_schema in properties.items():
            result[prop_name] = _generate_from_schema(prop_schema)
        return result

    elif schema_type == "array":
        items_schema = schema.get("items", {"type": "string"})
        min_items = schema.get("minItems", 1)
        max_items = schema.get("maxItems", 3)
        count = fake.random_int(min=min_items, max=max_items)
        return [_generate_from_schema(items_schema) for _ in range(count)]

    elif schema_type == "string":
        format_type = schema.get("format")
        if format_type == "email":
            return fake.email()
        elif format_type == "uri":
            return fake.url()
        elif format_type == "date":
            return fake.date()
        else:
            return fake.word()

    elif schema_type == "integer":
        minimum = schema.get("minimum", 0)
        maximum = schema.get("maximum", 1000)
        return fake.random_int(min=minimum, max=maximum)

    elif schema_type == "number":
        return round(fake.random.uniform(0, 1000), 2)

    elif schema_type == "boolean":
        return fake.boolean()

    else:
        return None


def _generate_edge_cases(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate edge case test data"""
    edge_cases = []

    # Empty object
    edge_cases.append({"description": "empty object", "data": {}})

    # Null values
    if schema.get("type") == "object":
        null_case = {}
        for prop in schema.get("properties", {}).keys():
            null_case[prop] = None
        edge_cases.append({"description": "null values", "data": null_case})

    # Boundary values for numbers
    if "minimum" in schema:
        edge_cases.append({
            "description": "minimum value",
            "data": schema["minimum"]
        })
    if "maximum" in schema:
        edge_cases.append({
            "description": "maximum value",
            "data": schema["maximum"]
        })

    return edge_cases


def compare_api_versions(spec_v1: Dict[str, Any], spec_v2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compares two OpenAPI specifications to identify changes

    Returns breaking changes, new features, and deprecations
    """
    try:
        results = {
            "breaking_changes": [],
            "new_endpoints": [],
            "removed_endpoints": [],
            "modified_endpoints": [],
            "summary": {}
        }

        # Extract paths from both specs
        paths_v1 = set(spec_v1.get("paths", {}).keys())
        paths_v2 = set(spec_v2.get("paths", {}).keys())

        # Find new and removed endpoints
        results["new_endpoints"] = list(paths_v2 - paths_v1)
        results["removed_endpoints"] = list(paths_v1 - paths_v2)

        # If endpoints were removed, that's a breaking change
        if results["removed_endpoints"]:
            for endpoint in results["removed_endpoints"]:
                results["breaking_changes"].append({
                    "type": "endpoint_removed",
                    "endpoint": endpoint,
                    "severity": "high"
                })

        # Check modified endpoints
        common_paths = paths_v1 & paths_v2
        for path in common_paths:
            changes = _compare_endpoint(
                spec_v1["paths"][path],
                spec_v2["paths"][path],
                path
            )
            if changes:
                results["modified_endpoints"].append({
                    "endpoint": path,
                    "changes": changes
                })

        # Generate summary
        results["summary"] = {
            "total_breaking_changes": len(results["breaking_changes"]),
            "endpoints_added": len(results["new_endpoints"]),
            "endpoints_removed": len(results["removed_endpoints"]),
            "endpoints_modified": len(results["modified_endpoints"])
        }

        return results

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to compare specs: {str(e)}",
            "traceback": traceback.format_exc()
        }


def _compare_endpoint(endpoint_v1: Dict, endpoint_v2: Dict, path: str) -> List[Dict]:
    """Compare two endpoint definitions"""
    changes = []

    # Compare HTTP methods
    methods_v1 = set(endpoint_v1.keys())
    methods_v2 = set(endpoint_v2.keys())

    removed_methods = methods_v1 - methods_v2
    if removed_methods:
        changes.append({
            "type": "method_removed",
            "methods": list(removed_methods),
            "breaking": True
        })

    added_methods = methods_v2 - methods_v1
    if added_methods:
        changes.append({
            "type": "method_added",
            "methods": list(added_methods),
            "breaking": False
        })

    return changes


def check_security(endpoint_url: str) -> Dict[str, Any]:
    """
    Performs basic security checks on an endpoint

    Checks for: missing auth, verbose errors, CORS issues, rate limiting
    """
    findings = []

    try:
        # Check 1: No authentication required
        response = httpx.get(endpoint_url, timeout=5.0)
        if response.status_code == 200:
            findings.append({
                "severity": "medium",
                "issue": "No authentication required",
                "description": "Endpoint is publicly accessible without auth headers",
                "recommendation": "Add authentication if endpoint handles sensitive data"
            })

        # Check 2: Verbose error messages
        response_404 = httpx.get(endpoint_url + "/nonexistent", timeout=5.0)
        if "traceback" in response_404.text.lower() or "exception" in response_404.text.lower():
            findings.append({
                "severity": "high",
                "issue": "Verbose error messages",
                "description": "Error responses contain stack traces or detailed errors",
                "recommendation": "Disable debug mode in production, sanitize error messages"
            })

        # Check 3: Missing security headers
        security_headers = ["X-Content-Type-Options", "X-Frame-Options", "Strict-Transport-Security"]
        missing_headers = [h for h in security_headers if h not in response.headers]
        if missing_headers:
            findings.append({
                "severity": "low",
                "issue": "Missing security headers",
                "description": f"Missing: {', '.join(missing_headers)}",
                "recommendation": "Add recommended security headers"
            })

        # Check 4: Rate limiting
        # Make 10 rapid requests
        statuses = []
        for _ in range(10):
            r = httpx.get(endpoint_url, timeout=1.0)
            statuses.append(r.status_code)

        if 429 not in statuses:  # 429 = Too Many Requests
            findings.append({
                "severity": "medium",
                "issue": "No rate limiting detected",
                "description": "Endpoint did not return 429 after 10 rapid requests",
                "recommendation": "Implement rate limiting to prevent abuse"
            })

        return {
            "endpoint": endpoint_url,
            "findings": findings,
            "risk_level": _calculate_risk_level(findings),
            "total_issues": len(findings)
        }

    except Exception as e:
        return {
            "endpoint": endpoint_url,
            "error": str(e),
            "success": False
        }


def _calculate_risk_level(findings: List[Dict]) -> str:
    """Calculate overall risk level from findings"""
    if any(f["severity"] == "high" for f in findings):
        return "high"
    elif any(f["severity"] == "medium" for f in findings):
        return "medium"
    elif findings:
        return "low"
    else:
        return "none"


# ============================================================================
# MCP PROTOCOL HANDLERS
# ============================================================================

def handle_initialize(params: Dict) -> Dict:
    """Handle MCP initialize request"""
    return {
        "protocolVersion": "0.1.0",
        "serverInfo": {
            "name": "api-toolkit",
            "version": "1.0.0",
            "description": "API development and validation tools"
        },
        "capabilities": {
            "tools": {}
        }
    }


def handle_tools_list() -> Dict:
    """Return list of available tools"""
    return {
        "tools": [
            {
                "name": "validate_endpoint",
                "description": "Validates an HTTP endpoint against expected behavior (status code, response schema, performance)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "The endpoint URL to validate"},
                        "method": {"type": "string", "description": "HTTP method (GET, POST, etc.)", "default": "GET"},
                        "expected_status": {"type": "integer", "description": "Expected HTTP status code", "default": 200},
                        "expected_schema": {"type": "object", "description": "JSON Schema to validate response against"},
                        "timeout": {"type": "number", "description": "Request timeout in seconds", "default": 5.0}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "generate_test_data",
                "description": "Generates realistic test data matching a JSON schema, including edge cases",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "schema": {"type": "object", "description": "JSON Schema defining the data structure"},
                        "count": {"type": "integer", "description": "Number of valid test cases to generate", "default": 1},
                        "include_edge_cases": {"type": "boolean", "description": "Whether to generate edge cases", "default": True}
                    },
                    "required": ["schema"]
                }
            },
            {
                "name": "compare_api_versions",
                "description": "Compares two OpenAPI specifications to identify breaking changes and new features",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "spec_v1": {"type": "object", "description": "OpenAPI spec version 1"},
                        "spec_v2": {"type": "object", "description": "OpenAPI spec version 2"}
                    },
                    "required": ["spec_v1", "spec_v2"]
                }
            },
            {
                "name": "check_security",
                "description": "Performs basic security checks on an endpoint (auth, error handling, headers, rate limiting)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "endpoint_url": {"type": "string", "description": "The endpoint URL to check"}
                    },
                    "required": ["endpoint_url"]
                }
            }
        ]
    }


def handle_tools_call(tool_name: str, arguments: Dict) -> Dict:
    """Execute tool and return results"""
    try:
        if tool_name == "validate_endpoint":
            result = validate_endpoint(**arguments)
        elif tool_name == "generate_test_data":
            result = generate_test_data(**arguments)
        elif tool_name == "compare_api_versions":
            result = compare_api_versions(**arguments)
        elif tool_name == "check_security":
            result = check_security(**arguments)
        else:
            return {
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                }
            }

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }
            ]
        }

    except Exception as e:
        return {
            "error": {
                "code": -32603,
                "message": f"Tool execution failed: {str(e)}",
                "data": {"traceback": traceback.format_exc()}
            }
        }


# ============================================================================
# MAIN SERVER LOOP
# ============================================================================

def main():
    """Main MCP server event loop"""
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            # Route to appropriate handler
            if method == "initialize":
                response = handle_initialize(params)
            elif method == "tools/list":
                response = handle_tools_list()
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                response = handle_tools_call(tool_name, arguments)
            else:
                response = {
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }

            # Send response
            result = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": response if "error" not in response else None,
                "error": response.get("error")
            }

            # Remove None values
            result = {k: v for k, v in result.items() if v is not None}

            print(json.dumps(result), flush=True)

        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}",
                    "data": {"traceback": traceback.format_exc()}
                }
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()
```

Make it executable:

```bash
chmod +x server.py
```

## Step 3: Configure Claude Code

Edit `~/.claude/config.json`:

```json
{
  "mcpServers": {
    "api-toolkit": {
      "command": "python3",
      "args": ["/Users/YOUR_USERNAME/.claude/mcp-servers/api-toolkit/server.py"]
    }
  }
}
```

Replace `YOUR_USERNAME` with your actual username.

Restart Claude Code.

## Step 4: Test the MCP Server

Test each tool:

```
Use the api-toolkit MCP server to validate http://localhost:5000/api/destinations
```

```
Use the api-toolkit to generate test data for this schema:
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "email": {"type": "string", "format": "email"},
    "age": {"type": "integer", "minimum": 0, "maximum": 120}
  }
}
```

```
Use the api-toolkit to check security of http://localhost:5000/api/bookings
```

## Step 5: Create the `/api-audit` Skill

Create a skill that uses your MCP server:

```bash
mkdir ~/.claude/skills/api-audit
cd api-audit
```

Create `skill.json`:

```json
{
  "name": "api-audit",
  "version": "1.0.0",
  "description": "Comprehensive API audit using the api-toolkit MCP server",
  "author": "Your Name",
  "invocation": "/api-audit"
}
```

Create `prompt.txt`:

```txt
You are an API auditor. Use the api-toolkit MCP server to comprehensively audit all API endpoints.

PROCESS:

1. Find all API endpoints (use Explore or Grep)
2. For each endpoint:
   - Validate it's accessible (validate_endpoint)
   - Check security (check_security)
3. Generate test data for POST endpoints
4. Create comprehensive report: api-audit-report.md

REPORT FORMAT:
- Executive summary
- Per-endpoint findings
- Security issues (ranked by severity)
- Performance metrics
- Recommendations

Use the api-toolkit MCP server tools extensively.
```

Test it:

```
/api-audit
```

## Success Criteria ✅

- [ ] MCP server implements all 4 tools
- [ ] Server responds to MCP protocol messages
- [ ] Claude Code can discover tools
- [ ] All tools return structured results
- [ ] `/api-audit` skill uses the MCP server
- [ ] You understand JSON-RPC basics

## Troubleshooting

**Problem:** Server doesn't start
- **Solution:** Check Python path in config
- Test manually: `python3 server.py` (then send JSON on stdin)
- Check dependencies installed

**Problem:** Tools not discovered
- **Solution:** Verify `tools/list` returns correct schema
- Check JSON format is valid
- Restart Claude Code

**Problem:** Tool execution fails
- **Solution:** Check argument types match schema
- Add logging to server.py
- Return rich error messages

## Going Deeper (Optional)

### Challenge 1: Async Tools

Modify tools to run asynchronously for better performance:

```python
import asyncio

async def validate_endpoint_async(url: str) -> Dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        # ... rest of validation
```

### Challenge 2: Streaming Results

For long-running tools, stream partial results:

```python
def scan_all_endpoints(base_url: str):
    # Discover endpoints
    for endpoint in endpoints:
        # Yield partial result
        yield {"endpoint": endpoint, "status": "scanning..."}
        # Complete scan
        yield {"endpoint": endpoint, "result": result}
```

### Challenge 3: Caching

Add caching to avoid redundant HTTP requests:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def validate_endpoint(url: str, ...):
    # Cached for same URL + params
```

### Challenge 4: More Tools

Add additional tools:
- `generate_openapi_spec` - Infer OpenAPI spec from code
- `mock_api` - Create mock API server from spec
- `load_test` - Perform load testing
- `fuzz_endpoint` - Fuzzing for vulnerabilities

## Key Concepts Learned

### MCP Protocol
- JSON-RPC 2.0 over stdio
- Request-response pattern
- Tool discovery and invocation

### Tool Design
- Clear, focused purpose
- Well-defined input schema
- Structured output
- Rich error messages

### Integration Patterns
- Skills orchestrate MCP tools
- MCP tools extend Claude's capabilities
- Compose tools for complex workflows

## Stage 5 Complete! 🎉

You now have:
- A fully functional MCP server
- 4 domain-specific tools
- Understanding of MCP protocol
- A skill that leverages your MCP server

## What's Next?

In [Stage 6: Integration & Reflection](./stage6-integration.md), you'll integrate everything you've built and prepare for daily use!

---

**Navigation:**
⬅️ [Back: Stage 4](./stage4-workflow-skills.md) | [Overview](./README.md) | ➡️ [Next: Stage 6](./stage6-integration.md)
