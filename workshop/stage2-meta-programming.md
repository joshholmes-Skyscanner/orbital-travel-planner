# Stage 2: Meta-Programming & Self-Validation

**Time:** 11:00–12:00 (60 minutes)
**Goal:** Build a skill that orchestrates multiple agents and validates its own work using external tools.

## Learning Objectives

By the end of this stage, you'll be able to:
- Create skills that coordinate multiple agents sequentially
- Pass structured data between agents
- Build self-validating loops that fix their own errors
- Create a custom MCP server for validation
- Understand fix-verify-repeat patterns

## Part A: Multi-Agent Skill (30 minutes)

### What You're Building

A `/validate-api` skill that orchestrates three agents to analyze and validate API endpoints:
1. **Explore agent**: Finds all API endpoints
2. **Plan agent**: Designs a validation strategy
3. **General-purpose agent**: Generates test cases

### Step 1: Create the Skill Directory

```bash
cd ~/.claude/skills
mkdir validate-api
cd validate-api
```

### Step 2: Create the Skill Manifest

Create `skill.json`:

```json
{
  "name": "validate-api",
  "version": "1.0.0",
  "description": "Orchestrates multiple agents to find, analyze, and validate API endpoints",
  "author": "Your Name",
  "invocation": "/validate-api"
}
```

### Step 3: Create the Orchestration Prompt

Create `prompt.txt`:

```txt
You are an API validation orchestrator. Your job is to coordinate multiple agents to comprehensively analyze API endpoints.

IMPORTANT: Follow these steps SEQUENTIALLY. Each agent must complete before the next starts.

Step 1: EXPLORE PHASE
- Spawn an Explore agent with this task: "Find all API endpoints in the codebase. Look for:
  - Flask/FastAPI route decorators (@app.route, @router.get, etc.)
  - Endpoint paths and HTTP methods
  - Request/response models
  Write findings to api-endpoints.json as a structured list"

Step 2: PLAN PHASE (Wait for Step 1 to complete)
- Read api-endpoints.json to see what was found
- Spawn a Plan agent with this task: "Given the API endpoints in api-endpoints.json, design a validation strategy:
  - What should be tested for each endpoint?
  - What are potential security issues?
  - What edge cases should be checked?
  Write the strategy to validation-plan.json"

Step 3: EXECUTE PHASE (Wait for Step 2 to complete)
- Read validation-plan.json
- Spawn a general-purpose agent with this task: "Using the validation plan in validation-plan.json, generate concrete test cases:
  - Create sample requests for each endpoint
  - Include valid, invalid, and edge cases
  - Specify expected responses
  Write test cases to test-cases.json"

Step 4: REPORT PHASE (Wait for Step 3 to complete)
- Read all three JSON files
- Create a comprehensive markdown report: api-validation-report.md
- Include: endpoints found, validation strategy, test cases, and recommendations

CRITICAL RULES:
- Agents must run SEQUENTIALLY, not in parallel
- Each agent writes to a specific JSON file
- Verify each file exists before proceeding
- If an agent fails, report the error and stop
- Use structured JSON for agent communication
```

### Step 4: Test the Skill

In Claude Code:

```
/validate-api
```

Watch the orchestration happen:
1. Explore agent discovers endpoints
2. Plan agent designs validation
3. General-purpose agent generates tests
4. Final report is created

### Step 5: Examine the Outputs

Check the generated files:

```bash
cat api-endpoints.json
cat validation-plan.json
cat test-cases.json
cat api-validation-report.md
```

### Step 6: Verify Sequential Execution

Notice how each agent waits for the previous one. This is because:
- Agent 2 needs the output from Agent 1
- Agent 3 needs the output from Agent 2
- Dependencies enforce sequential execution

### Success Criteria ✅

- [ ] `/validate-api` skill exists and can be invoked
- [ ] Three agents spawn sequentially (not in parallel)
- [ ] Each agent writes to its designated JSON file
- [ ] Final report includes all findings
- [ ] You understand how to pass data between agents

### Troubleshooting

**Problem:** Agents run in parallel instead of sequentially
- **Solution:** Ensure the prompt explicitly says to wait
- Each step should read the previous step's output file

**Problem:** Agent can't find previous agent's output
- **Solution:** Check file paths are absolute or relative to current dir
- Verify files were actually created

**Problem:** Skill times out
- **Solution:** Simplify agent tasks
- Break into smaller steps if needed

## Part B: Self-Validating Loop (30 minutes)

### What You're Building

1. An MCP server that validates HTTP endpoints
2. A `/implement-verified` skill that implements features and fixes itself if validation fails

### Step 1: Create the Validation MCP Server

Create `~/.claude/mcp-servers/api-validator/`:

```bash
mkdir -p ~/.claude/mcp-servers/api-validator
cd ~/.claude/mcp-servers/api-validator
```

Create `server.py`:

```python
#!/usr/bin/env python3
"""
API Validation MCP Server
Provides tools to validate HTTP endpoints
"""

import json
import sys
from typing import Any
import httpx
from jsonschema import validate, ValidationError

def validate_endpoint(url: str, expected_status: int = 200, expected_schema: dict = None) -> dict:
    """
    Validates an HTTP endpoint

    Args:
        url: The endpoint URL to validate
        expected_status: Expected HTTP status code
        expected_schema: Optional JSON schema to validate response against

    Returns:
        Dict with validation results
    """
    try:
        # Make the request
        response = httpx.get(url, timeout=5.0)

        result = {
            "url": url,
            "status_code": response.status_code,
            "status_match": response.status_code == expected_status,
            "response_time_ms": response.elapsed.total_seconds() * 1000,
            "success": True
        }

        # Check status code
        if response.status_code != expected_status:
            result["success"] = False
            result["error"] = f"Status mismatch: expected {expected_status}, got {response.status_code}"
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
                result["response_body"] = response.text[:500]  # Truncate
        else:
            result["response_body"] = response.text[:500]

        return result

    except Exception as e:
        return {
            "url": url,
            "success": False,
            "error": str(e)
        }

# MCP Protocol Implementation
def handle_initialize(params: dict) -> dict:
    """Handle initialize request"""
    return {
        "protocolVersion": "0.1.0",
        "serverInfo": {
            "name": "api-validator",
            "version": "1.0.0"
        },
        "capabilities": {
            "tools": {}
        }
    }

def handle_tools_list() -> dict:
    """Return available tools"""
    return {
        "tools": [
            {
                "name": "validate_endpoint",
                "description": "Validates an HTTP endpoint against expected status and schema",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The endpoint URL to validate"
                        },
                        "expected_status": {
                            "type": "integer",
                            "description": "Expected HTTP status code",
                            "default": 200
                        },
                        "expected_schema": {
                            "type": "object",
                            "description": "JSON Schema to validate response against",
                            "default": None
                        }
                    },
                    "required": ["url"]
                }
            }
        ]
    }

def handle_tools_call(tool_name: str, arguments: dict) -> dict:
    """Execute tool call"""
    if tool_name == "validate_endpoint":
        result = validate_endpoint(**arguments)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }
            ]
        }
    else:
        return {
            "error": {
                "code": -32601,
                "message": f"Unknown tool: {tool_name}"
            }
        }

def main():
    """Main MCP server loop"""
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

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

            result = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": response
            }

            print(json.dumps(result), flush=True)

        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    main()
```

Create `requirements.txt`:

```txt
httpx>=0.27.0
jsonschema>=4.21.0
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Make it executable:

```bash
chmod +x server.py
```

### Step 2: Add MCP Server to Claude Config

Edit `~/.claude/config.json`:

```json
{
  "mcpServers": {
    "api-validator": {
      "command": "python3",
      "args": ["/Users/YOUR_USERNAME/.claude/mcp-servers/api-validator/server.py"]
    }
  }
}
```

Replace `YOUR_USERNAME` with your actual username.

Restart Claude Code.

### Step 3: Test the MCP Server

```
Use the api-validator MCP server to validate http://localhost:5000/health
```

Claude should invoke your MCP server and return validation results.

### Step 4: Create the Self-Validating Skill

Create `~/.claude/skills/implement-verified/`:

```bash
mkdir ~/.claude/skills/implement-verified
cd implement-verified
```

Create `skill.json`:

```json
{
  "name": "implement-verified",
  "version": "1.0.0",
  "description": "Implements features with automatic validation and self-correction",
  "author": "Your Name",
  "invocation": "/implement-verified"
}
```

Create `prompt.txt`:

```txt
You are a self-validating implementation assistant. You implement features and automatically verify they work correctly.

PROCESS:
1. Ask the user for the feature description
2. Implement the feature
3. Validate using the api-validator MCP server
4. If validation fails, analyze the error and fix it
5. Repeat validation up to 3 times or until success

VALIDATION LOOP:
- After implementing, IMMEDIATELY validate
- Parse validation errors carefully
- Form specific hypotheses about what's wrong
- Make targeted fixes (don't rewrite everything)
- Track attempts: stop after 3 failed attempts

EXAMPLE FLOW:
User: "Add a /health endpoint that returns {status: ok}"

Attempt 1: Implement the endpoint
→ Validate with api-validator
→ If fails: analyze error, fix specific issue

Attempt 2: Validate again
→ If fails: try different fix approach

Attempt 3: Final validation
→ If still fails: report detailed diagnostics to user

SUCCESS: Report validation passed and show final code

IMPORTANT:
- Use the api-validator MCP server (validate_endpoint tool)
- Don't give up after first failure
- Learn from each validation error
- Keep user informed of progress
```

### Step 5: Test the Self-Validating Skill

First, start the orbital-travel-planner app:

```bash
cd /path/to/orbital-travel-planner
python -m flask run
```

Then invoke the skill:

```
/implement-verified
```

When asked, say:
```
Add a /health endpoint that returns {"status": "ok", "service": "orbital-travel"}
```

Watch Claude:
1. Implement the feature
2. Validate with the MCP server
3. If it fails, fix and retry
4. Report success or failure after max attempts

### Step 6: Test with Intentional Error

Try a more complex feature that might fail:

```
/implement-verified

Add a /api/destinations endpoint that returns all destinations from the database sorted by name
```

If validation fails (e.g., wrong schema, missing field), watch Claude fix it automatically.

### Success Criteria ✅

- [ ] MCP server is installed and configured
- [ ] Claude can invoke the validate_endpoint tool
- [ ] `/implement-verified` skill exists
- [ ] Skill demonstrates at least one automatic fix attempt
- [ ] You understand the fix-verify-repeat pattern

### Troubleshooting

**Problem:** MCP server doesn't start
- **Solution:** Check Python path in config
- Test server manually: `python3 server.py`
- Check dependencies are installed

**Problem:** Validation always fails
- **Solution:** Ensure the app is running (flask run)
- Check URL is correct (http://localhost:5000)
- Verify endpoint actually exists

**Problem:** Skill doesn't retry fixes
- **Solution:** Check prompt includes retry logic
- Ensure validation errors are clear
- Make sure attempt counter is tracked

## Stage 2 Complete! 🎉

You now have:
- A multi-agent orchestration skill
- A custom validation MCP server
- A self-correcting implementation loop
- Understanding of agent coordination patterns

### Quick Knowledge Check

1. How do agents pass data to each other?
2. What's the difference between sequential and parallel agent execution?
3. What protocol do MCP servers use?
4. How many times should a self-validating loop retry?
5. Why use structured JSON instead of prose for agent communication?

### Going Deeper (Optional)

1. **Enhanced Validation**: Add schema validation for POST endpoints

2. **Smarter Fixes**: Track what fixes were tried and don't repeat them

3. **Parallel Validation**: Modify `/validate-api` to validate multiple endpoints in parallel

4. **Validation Reports**: Generate HTML reports from validation results

## What's Next?

In [Stage 3: Advanced Agent Orchestration](./stage3-orchestration.md), you'll build complex agent dependency graphs with chaos testing!

---

**Navigation:**
⬅️ [Back: Stage 1](./stage1-foundations.md) | [Overview](./README.md) | ➡️ [Next: Stage 3](./stage3-orchestration.md)
