# Stage 5: MCP Server Development

**Time:** 45 minutes
**Goal:** Build custom MCP servers extending Claude's capabilities

## Learning Objectives

- Understand MCP protocol (JSON-RPC over stdio)
- Implement MCP tools with proper schemas
- Handle tool discovery and invocation lifecycle
- Provide rich error diagnostics
- Integrate servers with Claude Code

## Overview

Build an **API Development Toolkit** MCP server with four tools:
1. `validate_endpoint` — HTTP endpoint validation
2. `generate_test_data` — Schema-based test data generation
3. `compare_api_versions` — OpenAPI spec diffing
4. `check_security` — Security vulnerability scanning

## MCP Protocol Fundamentals

### Communication Model

```
Claude Code ↔ MCP Server
   (JSON-RPC over stdio)
```

### Message Flow

1. **Initialize**: Claude asks server capabilities
2. **Tool Discovery**: Server lists available tools
3. **Tool Invocation**: Claude calls specific tool
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

## Implementation

### 1. Set Up Project

```bash
mkdir -p ~/.claude/mcp-servers/api-toolkit
cd ~/.claude/mcp-servers/api-toolkit
```

Create `requirements.txt`:

```text
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

### 2. Implement Core Server

Due to length, the complete server implementation (400+ lines) includes:

- Tool implementations for all four functions
- MCP protocol handlers (initialize, tools/list, tools/call)
- Error handling and rich diagnostics
- Main server loop reading from stdin

Key structure:

```python
#!/usr/bin/env python3
import json
import sys
import httpx
from jsonschema import validate, ValidationError
from faker import Faker

# Tool implementations
def validate_endpoint(url, expected_status=200, expected_schema=None):
    # HTTP validation logic
    pass

def generate_test_data(schema, count=1, include_edge_cases=True):
    # Test data generation logic
    pass

def compare_api_versions(spec_v1, spec_v2):
    # API diff logic
    pass

def check_security(endpoint_url):
    # Security scanning logic
    pass

# MCP Protocol handlers
def handle_initialize(params):
    return {"protocolVersion": "0.1.0", ...}

def handle_tools_list():
    return {"tools": [...]}

def handle_tools_call(tool_name, arguments):
    # Route to appropriate tool
    pass

# Main loop
def main():
    for line in sys.stdin:
        request = json.loads(line)
        # Process request, send response
        pass
```

Refer to Stage 2 for the complete `api-validator` server implementation as a template.

### 3. Configure Claude Code

Edit `~/.claude/config.json` (replace `YOUR_USERNAME`):

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

Restart Claude Code.

### 4. Test the MCP Server

Test each tool:

```
Use api-toolkit to validate http://localhost:5000/api/destinations
```

```
Use api-toolkit to generate test data for this schema:
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
Use api-toolkit to check security of http://localhost:5000/api/bookings
```

### 5. Create Integration Skill

```bash
mkdir -p ~/.claude/skills/api-audit
cd api-audit
```

Create `skill.json`:

```json
{
  "name": "api-audit",
  "version": "1.0.0",
  "description": "Comprehensive API audit using api-toolkit MCP server",
  "author": "Your Name",
  "invocation": "/api-audit"
}
```

Create `prompt.txt`:

```text
You are an API auditor using the api-toolkit MCP server for comprehensive analysis.

PROCESS:

1. Find all API endpoints (Explore or Grep)
2. For each endpoint:
   - Validate accessibility (validate_endpoint)
   - Check security (check_security)
3. Generate test data for POST endpoints
4. Create report: api-audit-report.md

REPORT FORMAT:
- Executive summary
- Per-endpoint findings
- Security issues (ranked by severity)
- Performance metrics
- Recommendations

Use api-toolkit MCP server tools extensively.
```

Test:

```
/api-audit
```

## Verification

- [ ] MCP server implements all 4 tools
- [ ] Server responds to MCP protocol messages
- [ ] Claude Code discovers tools
- [ ] All tools return structured results
- [ ] `/api-audit` skill uses MCP server
- [ ] Understand JSON-RPC basics

## Troubleshooting

**Server doesn't start:**
- Check Python path in config
- Test manually: `python3 server.py`
- Verify dependencies installed

**Tools not discovered:**
- Verify `tools/list` returns correct schema
- Check JSON format validity
- Restart Claude Code

**Tool execution fails:**
- Check argument types match schema
- Add logging to server.py
- Return rich error messages

## Stage 5 Summary

You have now:
- Built a functional MCP server
- Implemented domain-specific tools
- Understood MCP protocol
- Created skills leveraging MCP servers

### Knowledge Check

1. What protocol do MCP servers use?
2. What are the three main MCP message types?
3. How does Claude discover available tools?
4. What should tool error messages include?
5. When should you build an MCP server vs. a skill?

---

**Next:** [Stage 6: Integration](./stage6-integration.md)
