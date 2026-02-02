# Stage 1: Foundations

**Time:** 30 minutes
**Goal:** Understand core building blocks—skills, agents, and MCP servers

## Learning Objectives

- Create and structure custom Claude Code skills
- Spawn and coordinate different agent types
- Configure MCP servers
- Understand where configuration and skills are stored

## Part A: Create a Custom Skill

**Time:** 10 minutes

### Background: Skills Overview

Skills extend Claude Code with reusable commands. They inject specialized instructions into Claude's context when invoked.

**Skill structure:**
```
~/.claude/skills/skill-name/
├── skill.json    # Metadata and configuration
└── prompt.txt    # Instructions for Claude
```

### 1. Examine an Existing Skill

```bash
cd ~/.claude/skills
ls
cat keybindings-help/skill.json
cat keybindings-help/prompt.txt
```

Note the structure: a JSON manifest and a prompt file.

### 2. Create a New Skill Directory

```bash
mkdir -p ~/.claude/skills/hello-skill
cd ~/.claude/skills/hello-skill
```

### 3. Create the Manifest

Create `skill.json`:

```json
{
  "name": "hello-skill",
  "version": "1.0.0",
  "description": "Project-aware greeting and status check",
  "author": "Your Name",
  "invocation": "/hello-skill"
}
```

**Field definitions:**
- `name`: Internal identifier (must match directory name)
- `version`: Semantic version for tracking changes
- `description`: Displayed in skill listings
- `author`: Your name or team identifier
- `invocation`: Command users type (must start with `/`)

### 4. Create the Prompt

Create `prompt.txt`:

```text
You are a project-aware greeting assistant.

When invoked:
1. Read README.md in the current directory (if present)
2. Greet the user and mention the project name
3. Check git status for uncommitted changes
4. Provide a relevant tip based on project type:
   - Python: pytest, linting, or virtual environment tips
   - JavaScript: npm scripts or dependency tips
   - General: useful git commands
5. Ask what the user would like to work on

Use Read and Bash tools as needed. Keep responses under 100 words.
```

### 5. Test the Skill

In your Claude Code session:

```
/hello-skill
```

The skill should activate and provide project context.

### Verification

- [ ] Created `~/.claude/skills/hello-skill/` directory
- [ ] Both `skill.json` and `prompt.txt` exist
- [ ] Skill invokes with `/hello-skill` command
- [ ] Skill provides project-specific information

### Troubleshooting

**Skill doesn't appear:**
- Restart Claude Code
- Verify directory name matches `name` field in skill.json
- Check file permissions

**Skill errors on invocation:**
- Validate JSON syntax in skill.json
- Ensure prompt.txt provides clear instructions
- Verify current directory has expected files

## Part B: Agent Orchestration

**Time:** 10 minutes

### Background: Agent Types

Agents are specialized Claude instances for specific tasks:

- **Explore**: Codebase exploration and analysis
- **Plan**: Architecture and implementation planning
- **Bash**: Command execution specialist
- **general-purpose**: Multi-step research and complex tasks

### 1. Spawn an Explore Agent

```
Spawn an Explore agent to analyze the orbital-travel-planner codebase structure. Map:
- Main application files
- API endpoint locations
- Database models
- Frontend components
```

Observe Claude using the Task tool to spawn the agent.

### 2. Spawn a Bash Agent

While the Explore agent runs:

```
Spawn a Bash agent to check for tests in this project and run them
```

Both agents can run concurrently.

### 3. Parallel Agent Execution

```
Spawn two agents in parallel:
1. Explore agent to find all API endpoints
2. Bash agent to check Python dependencies
```

Claude should send both Task calls in a single message.

### 4. Background Execution

```
Spawn a Bash agent in the background to run the full test suite with coverage reporting
```

Check progress:

```
Check the output of the background task
```

### 5. Agent Communication via Files

```
1. Spawn an Explore agent to find all API endpoints and write results to api-endpoints.json
2. After completion, spawn a general-purpose agent to read api-endpoints.json and generate test cases for each endpoint
```

Agents communicate through structured files, not conversation.

### Verification

- [ ] Successfully spawned an Explore agent
- [ ] Successfully spawned a Bash agent
- [ ] Executed multiple agents in parallel
- [ ] Used TaskOutput to retrieve background task results
- [ ] Understand when to use each agent type

### Troubleshooting

**Agent times out:**
- Break tasks into smaller chunks
- Use background mode for long-running operations

**Agents don't run in parallel:**
- Ensure tasks are independent
- Verify Claude sent both Task calls in one message

**Cannot find agent output:**
- Check for files agents created
- Use correct task ID with TaskOutput

## Part C: MCP Server Configuration

**Time:** 10 minutes

### Background: MCP Servers

MCP (Model Context Protocol) servers extend Claude's capabilities with custom tools. They function as plugins providing new functions Claude can invoke.

### 1. Review Existing Configuration

```bash
cat pyproject.toml
```

Look for the `[tool.claude.mcp]` section showing configured MCP servers.

### 2. Understand MCP Structure

An MCP server provides:
- **Tools**: Functions Claude can invoke
- **Parameters**: JSON Schema defining inputs
- **Responses**: Structured return values

### 3. Test the Existing MCP Server

```
Use the MCP server to validate the /api/destinations endpoint for a 200 status code
```

Claude should discover and invoke the configured MCP server tool.

### 4. Add a New MCP Server

Add the time MCP server as an example.

Create or edit `~/.claude/config.json`:

```json
{
  "mcpServers": {
    "time": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-time"]
    }
  }
}
```

Restart Claude Code to load the configuration.

### 5. Test the New Server

```
Query the current time from the MCP time server
```

### 6. Review MCP Protocol

```
Explain how MCP servers communicate using the JSON-RPC protocol over stdio
```

Or fetch documentation:

```
Use WebFetch to retrieve and summarize the MCP protocol documentation from https://modelcontextprotocol.io
```

### Verification

- [ ] Reviewed existing MCP server configuration
- [ ] Tested orbital-travel-planner MCP server
- [ ] Added new MCP server to configuration
- [ ] Claude successfully invoked the new server
- [ ] Understand MCP basics (tools, parameters, JSON-RPC)

### Troubleshooting

**MCP server not found:**
- Verify config file syntax is valid JSON
- Restart Claude Code after config changes
- Check server command path is correct

**Tool invocation fails:**
- Verify parameter types match schema
- Check server logs for errors
- Ensure server process is running

**Cannot locate config file:**
- Check `~/.claude/config.json`
- Ask Claude for config file location
- Refer to Claude Code documentation

## Stage 1 Summary

You have now:
- Created a working custom skill
- Spawned and coordinated different agent types
- Added an MCP server to your configuration
- Understood core Claude Code building blocks

### Knowledge Check

Before proceeding, ensure you can answer:

1. Where do custom skills reside?
2. What files are required to create a skill?
3. What are the four main agent types?
4. How do agents share data with each other?
5. What protocol do MCP servers use?

### Advanced Exercises (Optional)

**Skill Enhancement:**
Modify hello-skill to detect programming language and provide language-specific tips.

**Agent Chain:**
Create a three-agent workflow:
1. Find all Python files
2. Identify files without tests
3. Generate test stubs for uncovered files

**MCP Exploration:**
Browse https://github.com/modelcontextprotocol/servers and add another server of interest.

---

**Next:** [Stage 2: Meta-Programming & Self-Validation](./stage2-meta-programming.md)
