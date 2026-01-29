# Stage 1: Foundations & Setup

**Time:** 10:30–11:00 (30 minutes)
**Goal:** Get hands-on experience with the core building blocks: skills, agents, and MCP servers.

## Learning Objectives

By the end of this stage, you'll understand:
- How to create and structure custom skills
- How to spawn and coordinate different agent types
- How to add and configure MCP servers
- Where Claude Code stores configuration and skills

## Part A: Create a Simple Skill (10 minutes)

### What Are Skills?

Skills are reusable Claude Code extensions that add custom commands. They're like slash commands that inject specialized instructions into Claude's context.

### Step 1: Navigate to the Skills Directory

```bash
cd ~/.claude/skills
ls
```

You should see existing skills like `keybindings-help`. Let's examine one:

```bash
cat keybindings-help/skill.json
cat keybindings-help/prompt.txt
```

### Step 2: Create Your First Skill

Create a new skill directory:

```bash
mkdir hello-skill
cd hello-skill
```

### Step 3: Create the Manifest File

Create `skill.json`:

```json
{
  "name": "hello-skill",
  "version": "1.0.0",
  "description": "A simple greeting skill that demonstrates basic skill structure",
  "author": "Your Name",
  "invocation": "/hello-skill"
}
```

**What each field means:**
- `name`: Internal identifier (must match directory name)
- `version`: Semantic version for tracking changes
- `description`: What the skill does (shown in skill list)
- `author`: Your name or team name
- `invocation`: The command users type (must start with `/`)

### Step 4: Create the Prompt File

Create `prompt.txt`:

```txt
You are a friendly greeting assistant. When invoked:

1. Greet the user warmly
2. Check the current directory and mention what project they're working on
3. Offer a brief tip about Claude Code usage
4. Ask if they need help with anything specific

Keep your response concise and helpful. Use the Read tool if you need to check files.
```

**Prompt design tips:**
- Be specific about what the skill should do
- Use numbered steps for clarity
- Mention which tools to use
- Keep it focused on one task

### Step 5: Test Your Skill

In your Claude Code session:

```
/hello-skill
```

The skill should activate and greet you!

### Step 6: Make It More Useful

Let's enhance the skill to be project-aware. Edit `prompt.txt`:

```txt
You are a project-aware greeting assistant. When invoked:

1. Read the README.md file in the current directory (if it exists)
2. Greet the user and mention the project name from the README
3. Check git status to see if there are uncommitted changes
4. Provide a relevant tip based on the project type:
   - Python projects: mention pytest or linting
   - JavaScript projects: mention npm scripts
   - Any project: mention useful git commands
5. Ask what they'd like to work on

Use the Read and Bash tools as needed. Keep your response under 100 words.
```

Test it again:

```
/hello-skill
```

### Success Criteria ✅

- [ ] You created `~/.claude/skills/hello-skill/` directory
- [ ] `skill.json` and `prompt.txt` files exist
- [ ] You can invoke the skill with `/hello-skill`
- [ ] The skill responds appropriately
- [ ] You understand the basic skill structure

### Troubleshooting

**Problem:** Skill doesn't appear when typed
- **Solution:** Restart Claude Code or reload config
- Check that directory name matches `name` in `skill.json`

**Problem:** Skill errors when invoked
- **Solution:** Check `prompt.txt` for syntax errors
- Ensure the prompt gives clear instructions

**Problem:** Skill doesn't find files
- **Solution:** Make sure you're in the right directory
- Check file permissions

## Part B: Spawn and Coordinate Agents (10 minutes)

### What Are Agents?

Agents are specialized Claude instances that handle specific tasks. They run independently and can work in parallel or sequence.

### Available Agent Types

- **Explore**: Fast codebase exploration, searches, and questions
- **Plan**: Software architecture and implementation planning
- **Bash**: Command execution specialist
- **general-purpose**: Multi-step research and complex tasks

### Step 1: Spawn an Explore Agent

Ask Claude Code to spawn an Explore agent:

```
Please spawn an Explore agent to map the orbital-travel-planner codebase structure. I want to understand:
- Main application files
- API endpoint locations
- Database models
- Frontend files
```

Watch how Claude spawns the agent using the Task tool.

### Step 2: Spawn a Bash Agent

While the Explore agent is running, spawn a Bash agent:

```
Please spawn a Bash agent to check if there are any tests in this project and run them.
```

Notice both agents can run in parallel!

### Step 3: Multiple Agents in Parallel

Try spawning multiple agents at once:

```
Spawn two agents in parallel:
1. An Explore agent to find all API endpoints
2. A Bash agent to check Python dependencies
```

Claude should send both Task tool calls in a single message.

### Step 4: Background Agents

Try running an agent in the background:

```
Spawn a Bash agent in the background to run a comprehensive test suite with coverage reporting.
```

Then use `TaskOutput` to check progress:

```
Check the output of the background task.
```

### Step 5: Understanding Agent Communication

Agents work best when they communicate through structured data. Try this:

```
1. Spawn an Explore agent to find all API endpoints and write them to api-endpoints.json
2. Then spawn a general-purpose agent to read api-endpoints.json and generate test cases for each endpoint
```

Notice how agents pass data via files, not through conversation.

### Success Criteria ✅

- [ ] You successfully spawned an Explore agent
- [ ] You spawned a Bash agent
- [ ] You spawned multiple agents in parallel
- [ ] You used TaskOutput to retrieve background task results
- [ ] You understand different agent types and when to use each

### Troubleshooting

**Problem:** Agent times out
- **Solution:** Break the task into smaller chunks
- Use background mode for long tasks

**Problem:** Agents don't run in parallel
- **Solution:** Make sure tasks are truly independent
- Check that Claude sent both Task calls in one message

**Problem:** Can't find agent output
- **Solution:** Check for files agents created
- Use TaskOutput with the correct task ID

## Part C: Add an MCP Server (10 minutes)

### What Are MCP Servers?

MCP (Model Context Protocol) servers extend Claude's capabilities with custom tools. They're like plugins that add new functions Claude can call.

### Step 1: Check Existing MCP Configuration

First, let's see what MCP servers are already configured:

```bash
cat pyproject.toml
```

Look for the `[tool.claude.mcp]` section. You should see the existing MCP server configuration.

### Step 2: Understand MCP Server Structure

An MCP server has:
- **Tools**: Functions Claude can call (like `validate_endpoint`)
- **Parameters**: JSON schema defining inputs
- **Responses**: Structured return values

### Step 3: Test the Existing MCP Server

Try asking Claude to use an MCP tool:

```
Use the MCP server to validate the /api/destinations endpoint. Check if it returns a 200 status.
```

Claude should discover and invoke the MCP server tool.

### Step 4: Add a Simple MCP Server

Let's add the built-in `time` MCP server as an example. Create or edit `~/.claude/config.json`:

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

Restart Claude Code to load the new server.

### Step 5: Test the New MCP Server

```
What's the current time according to the MCP time server?
```

Claude should invoke the time MCP server.

### Step 6: Explore MCP Protocol Basics

Ask Claude to explain:

```
Can you explain how MCP servers communicate with you? What's the protocol?
```

Or fetch the docs:

```
Use WebFetch to fetch the MCP protocol documentation from https://modelcontextprotocol.io and summarize the key concepts.
```

### Success Criteria ✅

- [ ] You reviewed the existing MCP server configuration
- [ ] You tested the orbital-travel-planner MCP server
- [ ] You added a new MCP server to your config
- [ ] Claude successfully invoked your new MCP server
- [ ] You understand MCP basics (tools, parameters, JSON-RPC)

### Troubleshooting

**Problem:** MCP server not found
- **Solution:** Check config file syntax
- Restart Claude Code after config changes
- Verify the server command is correct

**Problem:** MCP tool invocation fails
- **Solution:** Check parameter types match schema
- Ensure the server is running (check logs)

**Problem:** Can't find config file
- **Solution:** Try `~/.claude/config.json` or check Claude Code docs
- Ask Claude: "Where is your config file located?"

## Stage 1 Complete! 🎉

You now have:
- A working custom skill
- Experience spawning different agent types
- An MCP server added to your config
- Understanding of the core Claude Code building blocks

### Quick Knowledge Check

Before moving on, make sure you can answer:
1. Where do custom skills live?
2. What file do you edit to create a skill?
3. What are the 4 main agent types?
4. How do agents communicate data to each other?
5. What protocol do MCP servers use?

### Going Deeper (Optional)

If you finish early, try:

1. **Skill Enhancement**: Modify your hello-skill to detect the programming language and give language-specific tips

2. **Agent Chain**: Create a 3-agent chain:
   - Agent 1: Find all Python files
   - Agent 2: Check which ones have tests
   - Agent 3: Generate missing test stubs

3. **MCP Exploration**: Browse MCP example servers at https://github.com/modelcontextprotocol/servers and add another interesting one

## What's Next?

In [Stage 2: Meta-Programming & Self-Validation](./stage2-meta-programming.md), you'll learn to:
- Create skills that orchestrate multiple agents
- Build self-validating loops
- Create your own MCP server for testing

---

**Navigation:**
⬅️ [Back to Overview](./README.md) | ➡️ [Next: Stage 2 - Meta-Programming](./stage2-meta-programming.md)
