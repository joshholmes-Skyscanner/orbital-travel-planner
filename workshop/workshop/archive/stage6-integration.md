# Stage 6: Integration

**Time:** 15 minutes
**Goal:** Integrate skills into cohesive workflows and prepare for daily use

## Learning Objectives

- Compose multiple skills into workflows
- Document skills for team distribution
- Understand when to use skills vs. ad-hoc prompts
- Plan post-workshop adoption

## Create a Meta-Skill

Build a comprehensive audit skill using all workshop skills.

### 1. Set Up Skill

```bash
mkdir -p ~/.claude/skills/full-audit
cd full-audit
```

Create `skill.json`:

```json
{
  "name": "full-audit",
  "version": "1.0.0",
  "description": "Comprehensive codebase audit using multiple workshop skills",
  "author": "Your Name",
  "invocation": "/full-audit"
}
```

### 2. Create Orchestration Prompt

Create `prompt.txt`:

```text
You are a comprehensive audit orchestrator running multiple skills for full codebase analysis.

AUDIT PHASES:

1. API VALIDATION
   Invoke /validate-api skill
   Wait for completion

2. API SECURITY & QUALITY
   Invoke /api-audit skill (uses api-toolkit MCP server)
   Wait for completion

3. CHAOS RESILIENCE (Optional if time permits)
   Invoke /chaos-test skill
   Wait for completion

4. AGGREGATE REPORT
   Read all generated reports:
   - api-validation-report.md
   - api-audit-report.md
   - chaos-test-report.md (if exists)

   Create master report: FULL-AUDIT-REPORT.md

MASTER REPORT STRUCTURE:
- Executive Summary (high-level findings, key metrics, critical issues)
- API Validation Results
- Security & Quality Results
- Resilience Testing Results (if run)
- Critical Issues (P0 - immediate attention)
- Recommendations (P1 - important but not urgent)
- Improvements (P2 - nice-to-have)
- Links to detailed reports

RULES:
- Skills run sequentially
- Provide progress updates
- Handle missing reports gracefully
- Prioritize issues by severity
```

### 3. Test the Meta-Skill

```
/full-audit
```

This runs multiple audits sequentially (several minutes).

## Review Skills Inventory

List created skills:

```bash
ls -la ~/.claude/skills/
```

Expected skills:
- `hello-skill` (Stage 1)
- `validate-api` (Stage 2)
- `implement-verified` (Stage 2)
- `chaos-test` (Stage 3)
- Your workflow skill (Stage 4)
- `api-audit` (Stage 5)
- `full-audit` (Stage 6)

Total: 6-7 custom skills

## Document Your Skills

Create skills registry:

```bash
cd ~/.claude/skills
```

Create `REGISTRY.md`:

```markdown
# Claude Code Skills Registry

## Workshop Skills

### Foundation
- **hello-skill**: Project-aware greeting and status check

### Validation & Testing
- **validate-api**: Multi-agent API endpoint discovery and validation
- **implement-verified**: Self-correcting feature implementation
- **chaos-test**: Chaos engineering with 4-agent orchestration
- **api-audit**: Security and quality audit using MCP server

### Workflow
- **[your-skill]**: [Description]

### Meta
- **full-audit**: Comprehensive audit running multiple skills

## MCP Servers

### api-validator
- **Location**: `~/.claude/mcp-servers/api-validator/`
- **Tools**: validate_endpoint
- **Purpose**: HTTP endpoint validation

### api-toolkit
- **Location**: `~/.claude/mcp-servers/api-toolkit/`
- **Tools**: validate_endpoint, generate_test_data, compare_api_versions, check_security
- **Purpose**: API development toolkit

## Usage Guidelines

### When to Use Skills

Use skills when:
- Task is repetitive across projects
- Complex multi-step orchestration needed
- Consistent behavior desired
- Specific tool coordination required

### When to Use Ad-Hoc Prompts

Use prompts when:
- One-time task
- Context-specific requirement
- Exploratory work
- Rapid iteration needed

## Team Distribution

To share skills:
1. Copy `~/.claude/skills/<skill-name>` to shared repo
2. Document prerequisites (MCP servers, tools)
3. Provide examples
4. Version skills (update skill.json)
```

## Discussion Points

Reflect on workshop learnings:

### 1. Most Valuable Skill
Which skill will save the most time in your daily work?

### 2. Agent Orchestration
When did multiple agents help vs. over-complicate?

### 3. Real-World Application
What will you build next week?

### 4. Team Sharing
How will you distribute skills to your team?

### 5. Pattern Recognition
Which patterns (parallel agents, self-validation, MCP tools) are most powerful?

## Plan Next Skills

Ideas for future development:

### Code Quality
- `/review-pr`: Automated code review with suggestions
- `/test-coverage`: Gap analysis and test generation
- `/lint-fix`: Auto-fix linting issues

### DevOps
- `/deploy-check`: Pre-deployment validation
- `/env-audit`: Environment variable verification
- `/dependency-scan`: Security and version checks

### Documentation
- `/doc-api`: Generate API documentation
- `/readme-gen`: Create README from code
- `/diagram-arch`: Generate architecture diagrams

### Team Workflow
- `/standup-prep`: Daily standup summary
- `/release-notes`: Generate from commit history
- `/triage-issues`: Prioritize GitHub issues

## Verification

- [ ] 6+ working skills installed
- [ ] Skills documented in REGISTRY.md
- [ ] Can explain when to use each skill
- [ ] Can invoke skills on different repos
- [ ] Understand skill composition
- [ ] Have post-workshop plan

## Post-Workshop Checklist

### Today (Before Leaving)
- [ ] Test each skill on orbital-travel-planner
- [ ] Verify MCP servers configured
- [ ] Document issues encountered
- [ ] Back up skills directory

### This Week
- [ ] Test skills on work projects
- [ ] Build one new workflow skill
- [ ] Share one skill with team
- [ ] Gather feedback on usefulness

### This Month
- [ ] Create team skills repository
- [ ] Run demo for team
- [ ] Iterate based on usage patterns
- [ ] Measure time savings

## Key Takeaways

### Meta-Patterns

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

## Team Distribution

### Create Shared Repository

```bash
git init claude-skills
cd claude-skills
cp -r ~/.claude/skills/* ./
git add .
git commit -m "Add workshop skills"
```

### Document Installation

```markdown
# Installation

Clone repository:
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

Configure Claude Code (add to ~/.claude/config.json):
[Configuration details]
```

### Contribution Guidelines

```markdown
# Contributing Skills

1. Test on 2+ different projects
2. Document in REGISTRY.md
3. Include usage examples
4. Version your skill (semantic versioning)
5. Submit PR for review
```

## Workshop Complete

You have built:
- **6-7 custom skills** for validation, testing, and workflow automation
- **2 MCP servers** extending Claude's capabilities
- **Agent orchestration patterns** (parallel, sequential, background)
- **Self-validating loops** that fix errors automatically
- **Real-world workflow automations** saving significant time

### Next Steps

You can now:
- Build skills for any repetitive task
- Orchestrate complex multi-agent workflows
- Extend Claude with custom MCP tools
- Share and maintain team skills
- Reason about when to automate vs. manual

### Resources

- **Skills**: `~/.claude/skills/`
- **MCP servers**: `~/.claude/mcp-servers/`
- **Config**: `~/.claude/config.json`
- **MCP Spec**: https://modelcontextprotocol.io/

---

**Congratulations on completing the Advanced Claude Code Workshop!**
