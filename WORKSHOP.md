# Advanced Claude Code Workshop: Meta-Programming & Skill Development

**Duration:** 10:30–16:00 (lunch 12:00–13:00)
**Audience:** Backend Python engineers familiar with Claude and LLM basics
**Focus:** Custom skills, agent orchestration, MCP tooling, and practical daily workflow automation

**Philosophy:** The orbital-travel-planner is a vehicle. The goal is to build reusable skills and agent coordination patterns you'll use daily after this workshop.

**Workshop Flow:**
- **Morning (10:30-13:00):** Stage 1 (Foundations 30min) + Stage 2 (Chaos Engineering 120min)
- **Afternoon (13:00-16:00):** Stage 3 (Build Your Own Skill 120min) + Showcase (60min)

---

## 📚 New Modular Workshop Format!

This workshop has been split into detailed, self-sufficient guides for each stage. Each guide includes:
- Step-by-step instructions
- Code examples
- Success criteria
- Troubleshooting
- Extra challenges

**Start here:** [Workshop Overview & Stage Guides](./workshop/README.md)

The sections below provide the original overview for reference.

---

---

## Stage 1: Foundations & Setup
**Time:** 10:30–11:00 (30 min)

**Goal:** Get hands-on experience with the core building blocks: skills, agents, and MCP servers.

**Tasks:**

### Part A: Create a Simple Skill (20 min)
- Navigate to `~/.claude/skills/` and create a new skill directory: `hello-skill`
- Create a `skill.json` manifest with basic metadata
- Create a `prompt.txt` that defines what the skill does
- Invoke the skill with `/hello-skill` and verify it works
- Examine an existing skill (e.g., keybindings-help) to understand the structure

### Part B: Spawn and Coordinate Agents (20 min)
- Use Claude to spawn an Explore agent that maps the orbital-travel-planner codebase
- Spawn a Bash agent to run tests
- Try spawning multiple agents in parallel (e.g., Explore + Bash simultaneously)
- Use `TaskOutput` to retrieve results from a background agent
- Understand the different agent types: Explore, Plan, Bash, general-purpose

### Part C: Add an MCP Server (20 min)
- Review `pyproject.toml` to see existing MCP server configuration
- Add a new MCP server to the config (use the example `filesystem` or `time` server from MCP docs)
- Restart Claude Code or reload config
- Test that Claude can discover and invoke the MCP server's tools
- Use `WebFetch` or docs to understand the MCP protocol basics

**Success criteria:**
- You have a working custom skill that you can invoke
- You've spawned at least two different agent types and retrieved their results
- You've added an MCP server and verified Claude can use its tools
- You understand where skills live, how agents communicate, and how MCP extends Claude's capabilities

**Hints:**
- Skills are in `~/.claude/skills/<skill-name>/` with `skill.json` + `prompt.txt`
- Agent results can be retrieved immediately (blocking) or later (background with `TaskOutput`)
- MCP servers are configured in your Claude settings (check existing examples in the repo)
- Don't overthink this stage—it's hands-on practice, not production code

---

## Stage 2: Chaos Engineering & Agent Orchestration
**Time:** 11:00–13:00 (120 min)

**Goal:** Build a chaos testing skill that demonstrates parallel and sequential agent coordination.

**Tasks:**
- Create a skill `/chaos-test` that orchestrates four agents:
  - **Agent 1 (Chaos Injector)**: Injects random failures into the code (runs in parallel with Agent 2)
  - **Agent 2 (Load Generator)**: Makes 100+ API requests and logs results (runs in parallel with Agent 1)
  - **Agent 3 (Pattern Analyzer)**: Analyzes failure patterns from load test results (sequential - waits for Agent 2)
  - **Agent 4 (Fix Proposer)**: Proposes specific code fixes based on patterns (sequential - waits for Agent 3)
- The skill should:
  - Launch Agents 1 & 2 **in parallel** using `run_in_background: true`
  - Wait for sufficient data collection
  - Launch Agent 3 once data is ready
  - Launch Agent 4 once analysis is complete
  - Generate a comprehensive report with failure patterns and prioritized fixes

**Success criteria:**
- Agents 1 & 2 run in parallel (understand why)
- Agents 3 & 4 run sequentially (understand why)
- Agents communicate via structured JSON files
- Report identifies real failure patterns
- Fix proposals are specific and actionable
- You understand parallel vs. sequential agent coordination

**Hints:**
- **Critical**: Both Agent 1 & 2 must be spawned in ONE message to run in parallel
- Use `TaskOutput` to poll background agent progress
- Each agent writes to a specific file: `chaos-config.json`, `load-results.json`, `failure-patterns.json`, `fix-proposals.json`
- Implement graceful degradation (proceed with partial data if timeout)
- This demonstrates the most advanced agent orchestration patterns

---

## Stage 3: Daily Workflow Skills
**Time:** 13:00–15:00 (120 min)

**Goal:** Create practical, reusable skills for common engineering tasks beyond just coding.

**Tasks:**
- Each participant picks one skill to build (or propose your own):

  **`/retro-prep`**: Sprint retrospective preparation
  - Analyzes git commits since last sprint (or custom date range)
  - Categorizes commits: features, bugs, refactoring, tech debt
  - Identifies patterns: what went well, what was painful
  - Generates markdown with talking points for retro meeting
  - Includes metrics: commit frequency, file churn, test coverage changes

  **`/pr-impact`**: Pull request blast radius analysis
  - Takes a PR number as parameter
  - Uses `gh` CLI to fetch PR diff
  - Identifies affected services, endpoints, database schemas
  - Determines what tests should run (unit, integration, E2E)
  - Lists potential breaking changes
  - Generates a checklist for PR review

  **`/onboard-service`**: New service onboarding
  - Analyzes a service repository structure
  - Generates architecture diagram (ASCII or mermaid)
  - Identifies dependencies (internal services, external APIs, databases)
  - Finds "entry points" (main functions, API routes, event handlers)
  - Creates setup checklist (env vars, credentials, local dev steps)
  - Produces markdown guide for new team members

  **`/incident-debrief`**: Incident post-mortem generation
  - Takes logs, error messages, or incident timeline as input
  - Constructs timeline of events
  - Identifies root cause(s)
  - Proposes prevention steps (code changes, monitoring, runbooks)
  - Generates structured markdown report
  - Links to relevant code/config that needs changes

  **`/debt-audit`**: Technical debt assessment
  - Scans codebase for debt markers: TODO, FIXME, XXX, HACK, hardcoded values
  - Identifies missing tests (functions without coverage)
  - Finds deprecated API usage
  - Detects code duplication (similar functions/classes)
  - Prioritizes by risk: critical paths, frequently changed files
  - Generates ranked list with remediation suggestions

- Your skill must:
  - Work on any repo (parameterizable, not hardcoded)
  - Coordinate multiple agents or tools
  - Produce structured output (markdown report, JSON, diagram)
  - Be documented with usage examples
  - Save >10 minutes compared to manual process

**Success criteria:**
- Your skill is fully functional and tested on the orbital-travel-planner repo
- You've tested it on at least one other repo (different structure to prove portability)
- The output is useful enough that you'd actually use it at work
- You can explain how to install it for daily use

**Hints:**
- Use Explore agent for broad codebase analysis, Grep/Glob for targeted searches
- Git data is gold: `git log`, `git diff`, `git blame` provide rich context
- Skills can call other skills—compose primitives
- Consider making skills interactive with `AskUserQuestion` for parameters
- Think about output format: can other tools/scripts consume it?

---

## Showcase: Share What You Built
**Time:** 15:00–16:00 (60 min)

**Goal:** Demonstrate your daily workflow skill and share learnings with the group.

**Tasks:**
- Prepare a 5-minute demo of the skill you built in Stage 4:
  - Show it running on the orbital-travel-planner repo
  - Walk through how it orchestrates agents/tools
  - Explain the output and how you'd use it at work
  - Share any challenges you encountered
- Each participant presents their skill (5-7 min per person)
- Group discussion (remaining time):
  - What skill saved the most time?
  - When did agent orchestration help vs. over-complicate?
  - Which patterns will you use at work?
  - What would you build next?

**Success criteria:**
- You have at least 1 working skill that you can demo
- Your skill runs successfully on the orbital-travel-planner repo
- You can explain the architecture and agent coordination
- You can articulate when to build a skill vs. use an ad-hoc prompt
- The group has shared insights about practical applications

**Presentation Tips:**
- Focus on the problem you're solving, not just the code
- Show real output from your skill running
- Discuss what you learned about agent coordination
- Share what you'd change if you had more time

---

## Meta-Patterns to Internalize

### Agent Coordination
- **Parallel agents**: Independent tasks (multiple searches, concurrent tests)
- **Sequential agents**: Output of one feeds another (Explore → Plan → Implement)
- **Background agents**: Long-running tasks that don't block (monitoring, load testing)
- **Coordinator agents**: Orchestration only, delegates all work

### Self-Validation Loops
- **External validation**: MCP servers that run real tests (HTTP calls, type checks, security scans)
- **Fix-verify cycles**: Implement → validate → fix → repeat
- **Guardrails**: Max iterations, confidence thresholds, escalation to human
- **Structured feedback**: Parse failures into actionable hypotheses

### Skill Design Principles
- **Composability**: Skills call other skills, tools, and agents
- **Reusability**: Parameterized for different repos, contexts, use cases
- **Observability**: Log agent handoffs, decision points, failures
- **Graceful degradation**: Partial success better than all-or-nothing
- **Clear contracts**: Well-defined inputs/outputs, structured data

### MCP Server Patterns
- **Tool granularity**: Focused single-purpose tools vs. Swiss army knife
- **Stateless preferred**: Each invocation is independent
- **Rich errors**: Return structured diagnostics with actionable info
- **Composable tools**: Tools that can be chained in sequences
- **Sync vs. async**: Choose based on operation duration

---

## Post-Workshop: Taking Skills Home

### Installation
1. Copy skills to `~/.claude/skills/` (or your team's shared skills repo)
2. Update Claude Code config with your MCP servers
3. Test each skill on a different project to verify portability
4. Document usage: when to use, parameters, example invocations

### Sharing with Team
- Create a team "skills registry" repository
- Document each skill: purpose, prerequisites, examples
- Set up contribution guidelines (skill naming, structure, testing)
- Run internal demos showing patterns, not just "here's a tool"
- Consider pairing: junior engineers learn by building skills with seniors

### Evolution
- Start with narrow, high-value skills (e.g., `/retro-prep`, `/debt-audit`)
- Measure impact: What actually saves time? What gets used?
- Iterate based on feedback: What parameters are missing? What breaks?
- Build MCP servers when skills need capabilities Claude lacks natively
- Share learnings: When did orchestration help? When did it add complexity?

### Maintenance
- Skills break when repos change—version your skills
- Test skills on multiple repos to ensure portability
- Keep documentation updated as skills evolve
- Deprecate skills that aren't used—avoid skill sprawl

---

## Resources

### Claude Code Internals
- Skill structure: `~/.claude/skills/<name>/skill.json` + `prompt.txt`
- Agent types: Plan, Explore, Bash, general-purpose
- Task tool: `subagent_type`, `run_in_background`, `resume`, `TaskOutput`
- Config location: `~/.claude/config.json` (or similar)

### MCP Development
- Specification: <https://modelcontextprotocol.io/>
- Python SDK: `pip install mcp`
- Example servers: <https://github.com/modelcontextprotocol/servers>
- Protocol: JSON-RPC over stdio, tool discovery, invocation, errors

### Validation & Testing
- OpenAPI validation: `openapi-spec-validator`, `schemathesis`
- Contract testing: Pact, Dredd
- API testing: Postman/Newman, `httpx`, `requests`, `curl`
- Schema generation: `pydantic`, `jsonschema`

### Git & Codebase Analysis
- Git commands: `git log`, `git diff`, `git blame`, `git show`
- GitHub CLI: `gh pr view`, `gh issue list`, `gh api`
- Code search: `ripgrep`, `ast-grep`, language-specific parsers

### Agent Patterns
- Background tasks: `run_in_background=true`, poll with `TaskOutput`
- Structured output: Write JSON to files, next agent reads and processes
- Error recovery: Parse failures, hypothesize root cause, attempt fix
- Timeouts: Set reasonable limits, handle gracefully
