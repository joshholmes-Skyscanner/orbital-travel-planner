# Stage 6: Integration & Reflection

**Time:** 15:45–16:00 (15 minutes)
**Goal:** Integrate your skills into a cohesive workflow and plan post-workshop usage.

## Learning Objectives

- Compose multiple skills into workflows
- Document skills for team sharing
- Understand when to use skills vs. ad-hoc prompts
- Plan post-workshop adoption

## Step 1: Create a Meta-Skill

Create a comprehensive audit skill that uses all the skills you've built today.

```bash
mkdir ~/.claude/skills/full-audit
cd full-audit
```

Create `skill.json`:

```json
{
  "name": "full-audit",
  "version": "1.0.0",
  "description": "Comprehensive codebase audit using all workshop skills",
  "author": "Your Name",
  "invocation": "/full-audit"
}
```

Create `prompt.txt`:

```txt
You are a comprehensive audit orchestrator. Run a full audit of the codebase using multiple skills.

AUDIT PHASES:

1. API VALIDATION
   - Invoke /validate-api skill
   - Wait for completion

2. API SECURITY & QUALITY
   - Invoke /api-audit skill (uses api-toolkit MCP server)
   - Wait for completion

3. CHAOS RESILIENCE (Optional - only if time permits)
   - Invoke /chaos-test skill
   - Wait for completion

4. AGGREGATE REPORT
   - Read all generated reports:
     - api-validation-report.md
     - api-audit-report.md
     - chaos-test-report.md (if exists)
   - Create master report: FULL-AUDIT-REPORT.md

MASTER REPORT STRUCTURE:
```markdown
# Full Codebase Audit

**Date**: <timestamp>
**Repository**: <repo name>

## Executive Summary
[High-level findings, key metrics, critical issues]

## API Validation Results
[Summary from /validate-api]

## Security & Quality Results
[Summary from /api-audit]

## Resilience Testing Results
[Summary from /chaos-test, if run]

## Critical Issues (P0)
[Issues requiring immediate attention]

## Recommendations (P1)
[Important but not urgent]

## Improvements (P2)
[Nice-to-have enhancements]

## Detailed Reports
- [API Validation Report](./api-validation-report.md)
- [API Audit Report](./api-audit-report.md)
- [Chaos Test Report](./chaos-test-report.md)
```

IMPORTANT:
- Skills run sequentially (each takes time)
- Provide progress updates
- Handle missing reports gracefully
- Prioritize issues by severity
```

Test the meta-skill:

```
/full-audit
```

This will take several minutes as it runs multiple audits.

## Step 2: Review Your Skills Inventory

List all skills you've created today:

```bash
ls -la ~/.claude/skills/
```

You should have:
- `hello-skill` (Stage 1)
- `validate-api` (Stage 2)
- `implement-verified` (Stage 2)
- `chaos-test` (Stage 3)
- Your workflow skill (Stage 4): `/retro-prep`, `/pr-impact`, etc.
- `api-audit` (Stage 5)
- `full-audit` (Stage 6)

That's 6-7 custom skills!

## Step 3: Document Your Skills

Create a skills registry document:

```bash
cd ~/.claude/skills
```

Create `REGISTRY.md`:

```markdown
# Claude Code Skills Registry

## Workshop Skills (2026-01-29)

### Foundation Skills

#### hello-skill
- **Purpose**: Project-aware greeting and status check
- **Usage**: `/hello-skill`
- **Best for**: Quick project orientation

### Validation & Testing Skills

#### validate-api
- **Purpose**: Multi-agent API endpoint discovery and validation planning
- **Usage**: `/validate-api`
- **Output**: api-endpoints.json, validation-plan.json, test-cases.json
- **Best for**: Understanding all API endpoints in a codebase

#### implement-verified
- **Purpose**: Self-correcting feature implementation with validation loop
- **Usage**: `/implement-verified`
- **Requirements**: api-validator MCP server, running application
- **Best for**: Implementing features with automatic testing

#### chaos-test
- **Purpose**: Chaos engineering with 4-agent orchestration
- **Usage**: `/chaos-test`
- **Output**: chaos-test-report.md with failure patterns and fixes
- **Best for**: Finding resilience issues

#### api-audit
- **Purpose**: Security and quality audit using api-toolkit MCP server
- **Usage**: `/api-audit`
- **Requirements**: api-toolkit MCP server
- **Best for**: Security scanning and API quality checks

### Workflow Skills

#### [Your Stage 4 skill]
- **Purpose**: [What it does]
- **Usage**: `/<skill-name>`
- **Best for**: [Use case]

### Meta Skills

#### full-audit
- **Purpose**: Comprehensive audit running multiple skills
- **Usage**: `/full-audit`
- **Time**: 5-10 minutes
- **Best for**: Complete codebase assessment

## MCP Servers

### api-validator
- **Location**: `~/.claude/mcp-servers/api-validator/`
- **Tools**: validate_endpoint
- **Purpose**: HTTP endpoint validation

### api-toolkit
- **Location**: `~/.claude/mcp-servers/api-toolkit/`
- **Tools**: validate_endpoint, generate_test_data, compare_api_versions, check_security
- **Purpose**: Comprehensive API development toolkit

## Usage Guidelines

### When to Use Skills vs. Ad-Hoc Prompts

**Use skills when:**
- Task is repetitive across projects
- Complex multi-step orchestration needed
- You want consistent behavior
- Task requires specific tool coordination

**Use ad-hoc prompts when:**
- One-time task
- Context-specific requirement
- Exploratory work
- Rapid iteration needed

### Skill Composition

Skills can invoke other skills:
```
/full-audit → /validate-api + /api-audit + /chaos-test
```

## Team Distribution

To share these skills:
1. Copy `~/.claude/skills/<skill-name>` to shared repo
2. Document prerequisites (MCP servers, tools)
3. Provide examples
4. Version your skills (update skill.json)

## Maintenance

- Test skills when Claude Code updates
- Update documentation when behavior changes
- Deprecate unused skills
- Version control your skills directory
```

## Step 4: Group Discussion (5 minutes)

Reflect on today's learning:

### Discussion Questions

1. **Most Valuable Skill**: Which skill will save you the most time?

2. **Agent Orchestration**: When did multiple agents help vs. over-complicate?

3. **Real-World Application**: What will you build next week?

4. **Sharing**: How will you distribute skills to your team?

5. **Patterns**: Which patterns (parallel agents, self-validation, MCP tools) are most powerful?

## Step 5: Plan Your Next Skills

Think about what you'll build after the workshop:

### Ideas for Next Skills

**Code Quality:**
- `/review-pr` - Automated code review with suggestions
- `/test-coverage` - Gap analysis and test generation
- `/lint-fix` - Auto-fix linting issues

**DevOps:**
- `/deploy-check` - Pre-deployment validation
- `/env-audit` - Environment variable verification
- `/dependency-scan` - Security and version checks

**Documentation:**
- `/doc-api` - Generate API documentation
- `/readme-gen` - Create README from code
- `/diagram-arch` - Generate architecture diagrams

**Team Workflow:**
- `/standup-prep` - Daily standup summary
- `/release-notes` - Generate from commit history
- `/triage-issues` - Prioritize GitHub issues

## Success Criteria ✅

- [ ] You have 6+ working skills installed
- [ ] Skills are documented in REGISTRY.md
- [ ] You can explain when to use each skill
- [ ] You can invoke skills on different repos
- [ ] You understand skill composition
- [ ] You have a plan for post-workshop usage

## Post-Workshop Checklist

### Today (before you leave)
- [ ] Test each skill on orbital-travel-planner
- [ ] Verify MCP servers are configured
- [ ] Document any issues encountered
- [ ] Back up your skills directory

### This Week
- [ ] Test skills on your work projects
- [ ] Build one new workflow skill
- [ ] Share one skill with your team
- [ ] Gather feedback on usefulness

### This Month
- [ ] Create a team skills repository
- [ ] Run a demo for your team
- [ ] Iterate based on usage patterns
- [ ] Measure time savings

## Key Takeaways

### Meta-Patterns Mastered

**Agent Coordination:**
- Parallel: Independent tasks
- Sequential: Dependent tasks
- Background: Long-running tasks
- Coordinator: Orchestration-only

**Self-Validation:**
- External validation via MCP
- Fix-verify-repeat loops
- Guardrails and max iterations
- Structured feedback parsing

**Skill Design:**
- Composability (skills call skills)
- Reusability (parameterized)
- Observability (clear outputs)
- Graceful degradation

**MCP Patterns:**
- Focused single-purpose tools
- Rich error diagnostics
- Tool composition
- Stateless design

### What Makes Skills Valuable

1. **Time Savings**: >10 minutes per use
2. **Consistency**: Same process every time
3. **Portability**: Works across projects
4. **Composability**: Builds on other skills
5. **Documentation**: Clear usage examples

## Sharing Your Work

### Internal Demo Template

```markdown
# Claude Code Skills Demo

## What Are Skills?
[Brief explanation]

## Skills I Built Today
[Show 2-3 most impressive]

## Live Demo
[Run /full-audit on a project]

## How to Install
[Step-by-step]

## When to Use
[Guidelines]

## Q&A
```

### Team Distribution

1. **Create shared repository**:
```bash
git init claude-skills
cd claude-skills
cp -r ~/.claude/skills/* ./
git add .
git commit -m "Add workshop skills"
```

2. **Document installation**:
```markdown
# Installation

Clone this repo:
```bash
git clone <repo-url>
```

Symlink skills:
```bash
ln -s $(pwd)/skills/* ~/.claude/skills/
```

Install MCP servers:
```bash
cd mcp-servers/api-toolkit
pip install -r requirements.txt
```

Configure Claude Code:
[Add to ~/.claude/config.json]
```

3. **Set contribution guidelines**:
```markdown
# Contributing New Skills

1. Test on 2+ different projects
2. Document in REGISTRY.md
3. Include usage examples
4. Version your skill
5. Submit PR for review
```

## Workshop Complete! 🎉

You've built:
- **6-7 custom skills** for validation, testing, and workflow automation
- **2 MCP servers** extending Claude's capabilities
- **Agent orchestration patterns** (parallel, sequential, background)
- **Self-validating loops** that fix their own errors
- **Real-world workflow automations** saving significant time

### What's Next

You're now equipped to:
- Build skills for any repetitive task
- Orchestrate complex multi-agent workflows
- Extend Claude with custom MCP tools
- Share and maintain team skills
- Reason about when to automate vs. manual

### Resources

- **Skills directory**: `~/.claude/skills/`
- **MCP servers**: `~/.claude/mcp-servers/`
- **Config**: `~/.claude/config.json`
- **Documentation**: [MCP Spec](https://modelcontextprotocol.io/)

### Keep Learning

- Experiment with new skill ideas
- Share patterns with your team
- Contribute to community skills
- Build MCP servers for your domain

## Thank You!

Questions? Ideas? Share them with the group!

---

**Navigation:**
⬅️ [Back: Stage 5](./stage5-mcp-servers.md) | [Back to Overview](./README.md)
