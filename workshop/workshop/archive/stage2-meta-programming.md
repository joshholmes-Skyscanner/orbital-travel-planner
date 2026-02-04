# Stage 2: Self-Validating Skills

**Time:** 60 minutes
**Goal:** Build skills that validate their own work and automatically fix errors

## Learning Objectives

- Build a skill that discovers and validates API endpoints
- Create an MCP server for external validation
- Implement self-correcting code loops
- Understand when skills benefit from spawning agents

## Overview

You'll build two powerful skills:
1. **`/validate-api`** - Discovers all API endpoints and generates validation strategies
2. **`/implement-verified`** - Implements features with automatic validation and fixes

These skills use agents internally for clean context and efficiency, but that's an implementation detail.

## Part A: API Validation Skill

**Time:** 30 minutes

### What You're Building

A skill that comprehensively analyzes your API:
- Discovers all endpoints automatically
- Designs a validation strategy
- Generates concrete test cases
- Produces actionable reports

**Why agents help here:** Each phase (discover, plan, execute) needs fresh context. Spawning agents keeps each step focused and uses cheaper models for discrete tasks.

### 1. Create the Skill

```bash
mkdir -p ~/.claude/skills/validate-api
cd ~/.claude/skills/validate-api
```

Create `skill.json`:

```json
{
  "name": "validate-api",
  "version": "1.0.0",
  "description": "Discovers API endpoints and generates comprehensive validation strategy",
  "author": "Your Name",
  "invocation": "/validate-api"
}
```

### 2. Write the Skill Logic

Create `prompt.txt`:

```text
You are an API validation specialist. Discover all API endpoints and create a comprehensive validation strategy.

Your job is to coordinate the analysis, but use agents for discrete tasks to keep context clean and costs low.

PHASE 1: DISCOVERY
Spawn an Explore agent to find all API endpoints:
"Find all API endpoints in the codebase. Look for:
- Flask/FastAPI route decorators (@app.route, @router.get, etc.)
- Endpoint paths and HTTP methods
- Request/response models
Write findings to api-endpoints.json as a structured list."

Wait for completion, then read api-endpoints.json.

PHASE 2: STRATEGY
Spawn a Plan agent to design validation approach:
"Given the API endpoints in api-endpoints.json, design a validation strategy:
- What should be tested for each endpoint?
- What are potential security issues?
- What edge cases should be checked?
Write the strategy to validation-plan.json."

Wait for completion, then read validation-plan.json.

PHASE 3: TEST GENERATION
Spawn a general-purpose agent to create test cases:
"Using the validation plan in validation-plan.json, generate concrete test cases:
- Create sample requests for each endpoint
- Include valid, invalid, and edge cases
- Specify expected responses
Write test cases to test-cases.json."

Wait for completion, then read test-cases.json.

PHASE 4: REPORT
Read all JSON files and create api-validation-report.md with:
- Endpoints discovered
- Validation strategy summary
- Test cases overview
- Key recommendations

WHY AGENTS:
- Each phase needs clean context focused on one task
- Explore agent is optimized for codebase searches
- Plan agent uses cheaper model for strategy work
- Agents prevent context bloat in the main skill

RULES:
- Agents run sequentially (each needs previous output)
- All communication via JSON files
- Verify each file exists before proceeding
```

### 3. Test the Skill

```
/validate-api
```

The skill will:
1. Discover all API endpoints in your codebase
2. Design a validation strategy
3. Generate specific test cases
4. Produce a comprehensive report

### 4. Review the Output

```bash
cat api-endpoints.json        # Discovered endpoints
cat validation-plan.json      # Validation strategy
cat test-cases.json           # Generated test cases
cat api-validation-report.md  # Final report
```

### What Just Happened?

The skill used three agents internally, but from your perspective you just ran `/validate-api` and got a comprehensive analysis. The agents were an implementation detail that:
- Kept each analysis phase focused
- Used cheaper models for discovery and planning
- Prevented context bloat
- Made the skill faster and more cost-effective

### Verification

- [ ] `/validate-api` skill works end-to-end
- [ ] Report includes all discovered endpoints
- [ ] Validation strategy is actionable
- [ ] Test cases are specific and useful
- [ ] Understand why agents help here (not for orchestration, but for efficiency)

### Troubleshooting

**Skill times out:**
- Simplify each agent's task
- Ensure JSON files are being written correctly

**Missing endpoints:**
- Check that Explore agent searched all common route locations
- Verify framework decorators are recognized

**Agents don't wait for previous output:**
- Ensure prompt explicitly reads previous JSON file before spawning next agent

## Part B: Self-Correcting Implementation Skill

**Time:** 30 minutes

### What You're Building

A skill that implements features and automatically validates them:
- Takes a feature description
- Implements the code
- Validates it actually works
- Fixes errors automatically (up to 3 attempts)
- Reports success or detailed diagnostics

**Why MCP server:** We need external validation (real HTTP calls) that Claude can't do natively.

### 1. Create the Validation MCP Server

This provides the external validation capability your skill needs.

```bash
mkdir -p ~/.claude/mcp-servers/api-validator
cd ~/.claude/mcp-servers/api-validator
```

Create `server.py`:

```python
#!/usr/bin/env python3
"""
API Validation MCP Server
Provides external HTTP validation for skills
"""

import json
import sys
from typing import Any, Dict
import httpx
from jsonschema import validate, ValidationError


def validate_endpoint(url: str, expected_status: int = 200,
                     expected_schema: Dict = None) -> Dict[str, Any]:
    """Validates an HTTP endpoint against expected behavior"""
    try:
        response = httpx.get(url, timeout=5.0)

        result = {
            "url": url,
            "status_code": response.status_code,
            "status_match": response.status_code == expected_status,
            "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2),
            "success": True
        }

        if response.status_code != expected_status:
            result["success"] = False
            result["error"] = f"Expected {expected_status}, got {response.status_code}"
            return result

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
                result["response_body"] = response.text[:500]
        else:
            result["response_body"] = response.text[:500]

        return result

    except Exception as e:
        return {"url": url, "success": False, "error": str(e)}


# MCP Protocol handlers
def handle_initialize(params: Dict) -> Dict:
    return {
        "protocolVersion": "0.1.0",
        "serverInfo": {"name": "api-validator", "version": "1.0.0"},
        "capabilities": {"tools": {}}
    }


def handle_tools_list() -> Dict:
    return {
        "tools": [{
            "name": "validate_endpoint",
            "description": "Validates HTTP endpoint against expected status and schema",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Endpoint URL to validate"},
                    "expected_status": {"type": "integer", "default": 200},
                    "expected_schema": {"type": "object", "description": "JSON Schema"}
                },
                "required": ["url"]
            }
        }]
    }


def handle_tools_call(tool_name: str, arguments: Dict) -> Dict:
    if tool_name == "validate_endpoint":
        result = validate_endpoint(**arguments)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
    return {"error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}}


def main():
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
                response = handle_tools_call(params.get("name"), params.get("arguments", {}))
            else:
                response = {"error": {"code": -32601, "message": f"Unknown method: {method}"}}

            print(json.dumps({"jsonrpc": "2.0", "id": request_id, "result": response}), flush=True)

        except Exception as e:
            error = {"jsonrpc": "2.0", "id": request.get("id"), "error": {"code": -32603, "message": str(e)}}
            print(json.dumps(error), flush=True)


if __name__ == "__main__":
    main()
```

Create `requirements.txt`:

```text
httpx>=0.27.0
jsonschema>=4.21.0
```

Install and configure:

```bash
pip install -r requirements.txt
chmod +x server.py
```

Edit `~/.claude/config.json` (replace `YOUR_USERNAME`):

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

Restart Claude Code.

### 2. Test the MCP Server

```
Use the api-validator MCP server to validate http://localhost:5000/health
```

### 3. Create the Self-Correcting Skill

```bash
mkdir -p ~/.claude/skills/implement-verified
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

```text
You are a self-validating implementation assistant. You implement features and automatically verify they work.

PROCESS:
1. Ask user for feature description
2. Implement the feature
3. Validate using api-validator MCP server
4. If validation fails, analyze error and fix
5. Repeat validation up to 3 times or until success

VALIDATION LOOP:
After implementation, IMMEDIATELY validate with api-validator.
If it fails:
- Parse the error carefully
- Form a specific hypothesis about what's wrong
- Make a targeted fix (not a full rewrite)
- Track attempts (stop after 3 failures)

EXAMPLE:
User: "Add a /health endpoint that returns {status: ok}"

You:
1. Implement the endpoint
2. Validate: http://localhost:5000/health
3. If 404: endpoint not registered correctly → fix routing
4. If 500: code error → fix implementation
5. If wrong response: schema mismatch → fix response
6. Report success or final diagnostics

KEY POINTS:
- Use api-validator MCP server (not agents - you need real HTTP validation)
- Don't give up after first failure
- Learn from each validation error
- Keep user informed of progress

This skill doesn't need agents - you do the implementation directly because you need continuous context about what you've tried.
```

### 4. Test Self-Correction

Start the application:

```bash
cd /path/to/orbital-travel-planner
python -m flask run
```

Invoke the skill:

```
/implement-verified
```

When prompted:
```
Add a /health endpoint returning {"status": "ok", "service": "orbital-travel"}
```

Watch the skill:
1. Implement the feature
2. Validate with MCP server
3. If it fails, fix and retry automatically
4. Report success after validation passes

### What Just Happened?

The skill implemented code AND validated it worked. When validation failed, it analyzed the error and fixed it automatically. The MCP server provided real HTTP validation that Claude can't do natively.

Notice this skill didn't spawn agents - it needs continuous context about implementation attempts and fixes. Agents aren't always the answer.

### Verification

- [ ] MCP server is working
- [ ] `/implement-verified` skill exists
- [ ] Skill demonstrates automatic fixes after validation failures
- [ ] Understand when skills need MCP servers vs. agents

### Troubleshooting

**MCP server doesn't start:**
- Check Python path in config
- Test manually: `python3 server.py`
- Verify dependencies installed

**Validation always fails:**
- Ensure application is running
- Check URL is correct
- Verify endpoint exists

**Skill doesn't retry fixes:**
- Check validation errors are clear
- Ensure skill tracks attempt counter

## Stage 2 Summary

You built two powerful skills:
- **`/validate-api`** - Comprehensive API analysis (uses agents for efficiency)
- **`/implement-verified`** - Self-correcting implementation (uses MCP for validation)

### Key Insights

**When to use agents in skills:**
- Discrete tasks with clean boundaries
- When fresh context improves focus
- When cheaper models can handle subtasks
- When parallel or sequential work makes sense

**When NOT to use agents:**
- When you need continuous context (like iterative fixes)
- When the task is already focused
- When coordinating agents adds complexity without benefit

**MCP servers provide:**
- Capabilities Claude doesn't have natively (HTTP calls, file system, external APIs)
- Reusable tools across multiple skills
- Standardized interfaces

### Knowledge Check

1. What does `/validate-api` do for users?
2. Why does that skill use agents internally?
3. What does `/implement-verified` do for users?
4. Why doesn't that skill use agents?
5. When should you build an MCP server vs. use agents?

---

**Next:** [Stage 3: Resilience Testing Skills](./stage3-orchestration.md)
