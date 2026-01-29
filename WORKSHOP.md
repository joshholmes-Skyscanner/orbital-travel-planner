# Advanced Claude Code Workshop: Meta-Programming & Skill Development

**Duration:** 10:30–16:00 (lunch 12:00–13:00)
**Audience:** Backend Python engineers familiar with Claude and LLM basics
**Focus:** Custom skills, agent orchestration, self-validation loops, MCP tooling, meta-programming

**Philosophy:** The orbital-travel-planner is a vehicle. The goal is to build reusable skills, validation harnesses, and agent coordination patterns you'll use daily after this workshop.

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

### Part A: Create a Simple Skill (10 min)
- Navigate to `~/.claude/skills/` and create a new skill directory: `hello-skill`
- Create a `skill.json` manifest with basic metadata
- Create a `prompt.txt` that defines what the skill does
- Invoke the skill with `/hello-skill` and verify it works
- Examine an existing skill (e.g., keybindings-help) to understand the structure

### Part B: Spawn and Coordinate Agents (10 min)
- Use Claude to spawn an Explore agent that maps the orbital-travel-planner codebase
- Spawn a Bash agent to run tests
- Try spawning multiple agents in parallel (e.g., Explore + Bash simultaneously)
- Use `TaskOutput` to retrieve results from a background agent
- Understand the different agent types: Explore, Plan, Bash, general-purpose

### Part C: Add an MCP Server (10 min)
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

## Stage 2: Meta-Programming & Self-Validation
**Time:** 11:00–12:00 (60 min)

**Goal:** Build a skill that orchestrates multiple agents and validates its own work using external tools.

**Tasks:**

### Part A: Multi-Agent Skill (30 min)
- Create a custom skill `/validate-api` that:
  - Spawns an Explore agent to find all API endpoints in the codebase
  - Spawns a Plan agent to design a validation strategy
  - Spawns a general-purpose agent to generate test cases for each endpoint
  - Writes findings to a structured JSON report
- Make the skill coordinate the agents sequentially: Explore → Plan → Execute
- Test the skill on the orbital-travel-planner codebase

### Part B: Self-Validating Loop (30 min)
- Create a simple MCP server that validates HTTP endpoints:
  - Tool: `validate_endpoint(url, expected_status, expected_schema)`
  - Implementation: Use `curl` or `httpx` to make actual HTTP calls
  - Return: Structured pass/fail with diffs
- Create a skill `/implement-verified` that:
  - Takes a feature description as a parameter
  - Implements the feature
  - Uses the validation MCP server to test it
  - If validation fails, attempts to fix the issue automatically
  - Loops up to 3 times or until validation passes
- Test it on a simple feature: "add a `/health` endpoint that returns `{status: ok}`"

**Success criteria:**
- Your `/validate-api` skill spawns 3 agents sequentially and produces a structured report
- Your validation MCP server can make HTTP calls and return pass/fail
- The `/implement-verified` skill demonstrates at least one autonomous fix attempt
- You understand how to pass data between agents (structured files, not prose)

**Hints:**
- Agents should write to files that subsequent agents read (e.g., `findings.json`)
- The MCP server can be a simple Python script using the `mcp` package
- For the validation loop, the skill needs to parse error messages and form fix hypotheses
- Use `run_in_background: false` for sequential dependencies

---

## Lunch Break
**Time:** 12:00–13:00

---

## Stage 3: Advanced Agent Orchestration
**Time:** 13:00–14:00 (60 min)

**Goal:** Create skills that coordinate multiple specialized agents in parallel with complex dependency graphs.

**Tasks:**
- Create a skill `/chaos-test` that orchestrates four agents:
  - **Agent 1 (Chaos Injector)**: Modifies MCP servers to inject random failures (runs in background)
  - **Agent 2 (Load Generator)**: Repeatedly calls the booking API and logs results (runs in background)
  - **Agent 3 (Pattern Analyzer)**: Monitors logs, identifies failure patterns (waits for Agent 2 data)
  - **Agent 4 (Fix Proposer)**: Analyzes patterns and proposes code fixes (waits for Agent 3 analysis)
- The skill should:
  - Launch Agents 1 & 2 in parallel using `run_in_background: true`
  - Poll Agent 2's output with `TaskOutput` until sufficient data collected
  - Launch Agent 3 once data is available
  - Launch Agent 4 once patterns are identified
  - Generate a final report with: failure patterns, root cause, proposed fixes
- Implement at least one fix from the chaos testing and verify it resolves the issue

**Success criteria:**
- Four agents run with correct dependencies (parallel + sequential)
- Agents communicate via structured JSON files
- You identified a real bug (concurrency issue, missing error handling, timeout problem)
- You can diagram the agent flow and explain the coordination logic

**Hints:**
- Use `TaskOutput` with polling to check if background agents are done
- Each agent should write to a specific file: `chaos-failures.json`, `load-results.json`, etc.
- Consider adding a "coordinator" skill that just orchestrates, doesn't do work
- Think about timeouts: what if an agent runs too long?

---

## Stage 4: Daily Workflow Skills
**Time:** 14:00–15:00 (60 min)

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

## Stage 5: MCP Server Development
**Time:** 15:00–15:45 (45 min)

**Goal:** Build a custom MCP server that extends Claude's capabilities for your domain.

**Tasks:**
- Create an MCP server for API development workflows with these tools:

  **`validate_endpoint`**:
  - Parameters: `url`, `method`, `expected_status`, `expected_schema` (JSON Schema)
  - Implementation: Makes HTTP request, validates response
  - Returns: Pass/fail with detailed diffs if validation fails

  **`generate_test_data`**:
  - Parameters: `schema` (JSON Schema or Pydantic model)
  - Implementation: Generates realistic test data matching schema
  - Returns: JSON test data (valid and edge cases)

  **`compare_api_versions`**:
  - Parameters: `openapi_spec_v1`, `openapi_spec_v2`
  - Implementation: Diffs two OpenAPI specs
  - Returns: Breaking changes, new endpoints, deprecated fields

  **`check_security`**:
  - Parameters: `endpoint_url`
  - Implementation: Scans for common issues (missing auth headers, CORS misconfig, verbose errors)
  - Returns: Security findings with severity levels

- Integrate the MCP server into Claude Code config
- Create a skill `/api-audit` that uses your MCP server to audit the orbital-travel-planner
- Write documentation for your MCP server: tool descriptions, parameters, examples

**Success criteria:**
- Your MCP server implements at least 3 tools correctly
- It responds to MCP protocol messages (initialize, tool discovery, tool invocation)
- Claude Code can discover and invoke your MCP server
- The `/api-audit` skill successfully uses your MCP server
- You can explain MCP protocol: JSON-RPC transport, tool schemas, error handling

**Hints:**
- Use Python `mcp` package or study the protocol and build from scratch
- MCP servers communicate over stdio (standard input/output)
- Tools return structured JSON—define clear schemas
- Test your MCP server standalone before integrating with Claude
- Consider: should tools be sync or async? What about long operations?
- Error handling: return rich diagnostics, not just "failed"

---

## Stage 6: Integration & Reflection
**Time:** 15:45–16:00 (15 min)

**Goal:** Integrate your skills into a cohesive workflow and plan post-workshop usage.

**Tasks:**
- Create a meta-skill `/full-audit` that composes your built skills:
  - Runs `/validate-api`
  - Executes `/chaos-test`
  - Performs `/api-audit` using your MCP server
  - Aggregates findings into single comprehensive report
- Install your custom skills in local Claude Code setup
- Document each skill: purpose, parameters, usage examples, limitations
- Group discussion (5 min):
  - What skill saved the most time?
  - When did agent orchestration help vs. over-complicate?
  - Which patterns will you use at work?
  - What would you build next?

**Success criteria:**
- You have 2-3 working skills installed locally
- You can invoke them on different repos
- You understand how to share skills with your team
- You can articulate when to build a skill vs. use an ad-hoc prompt

**Hints:**
- Skills live in `~/.claude/skills/` (or team shared repo)
- Use `git log --oneline` to review what you built today
- Consider which skills need MCP servers vs. work with existing tools
- Think about team distribution: shared skills repo vs. individual installation

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
