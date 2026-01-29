# Stage 4: Daily Workflow Skills

**Time:** 14:00–15:00 (60 minutes)
**Goal:** Create practical, reusable skills for common engineering tasks beyond just coding.

## Learning Objectives

By the end of this stage, you'll have:
- Built a real-world workflow skill you'll actually use
- Understood how to make skills portable across repos
- Learned skill composition patterns
- Created documentation for team distribution

## Overview

In this stage, you'll pick ONE skill to build from the options below (or propose your own). Focus on making it:
- **Portable**: Works on any repo, not just orbital-travel-planner
- **Useful**: Saves >10 minutes compared to manual process
- **Well-documented**: Others can use it without asking you
- **Composable**: Can be combined with other skills

## Skill Options

Choose one to build:

### Option 1: `/retro-prep` - Sprint Retrospective Preparation
### Option 2: `/pr-impact` - Pull Request Impact Analysis
### Option 3: `/onboard-service` - Service Onboarding Guide
### Option 4: `/incident-debrief` - Incident Post-Mortem Generator
### Option 5: `/debt-audit` - Technical Debt Assessment

Or propose your own workflow automation!

---

## Option 1: `/retro-prep` - Sprint Retrospective Preparation

### What It Does
Analyzes git history to prepare talking points for sprint retrospectives.

### Step-by-Step Implementation

#### Step 1: Create the Skill

```bash
mkdir ~/.claude/skills/retro-prep
cd retro-prep
```

Create `skill.json`:

```json
{
  "name": "retro-prep",
  "version": "1.0.0",
  "description": "Analyzes sprint commits to generate retrospective talking points",
  "author": "Your Name",
  "invocation": "/retro-prep"
}
```

#### Step 2: Write the Skill Prompt

Create `prompt.txt`:

```txt
You are a sprint retrospective preparation assistant. Generate insights from git history to facilitate retrospective discussions.

PROCESS:

1. ASK for date range (or default to last 2 weeks):
   - Start date (YYYY-MM-DD)
   - End date (YYYY-MM-DD)

2. ANALYZE git history:
   - Get all commits in date range: git log --since="<start>" --until="<end>" --pretty=format:"%h|%an|%ad|%s" --date=short
   - Get changed files: git log --since="<start>" --until="<end>" --name-only --pretty=format:""

3. CATEGORIZE commits:
   - Features: commits with "feat:", "add", "implement"
   - Bugs: commits with "fix:", "bug", "patch"
   - Refactoring: commits with "refactor", "clean", "improve"
   - Tech debt: commits with "debt", "TODO", "deprecate"
   - Other: everything else

4. IDENTIFY patterns:
   - Most active files (high churn = potential hotspot)
   - Commit frequency by day (busy days vs. slow days)
   - Author contributions
   - Common commit message themes

5. GENERATE retrospective sections:
   - **What went well**: Feature completions, bug fixes, improvements
   - **What was painful**: High-churn files, long-running branches, blockers (infer from commit messages)
   - **Action items**: Files needing refactoring, areas needing tests, documentation gaps

6. INCLUDE metrics:
   - Total commits
   - Commits per category
   - Top 5 most-changed files
   - Commit frequency graph (ASCII art)

7. WRITE to retro-prep.md

FORMAT:
```markdown
# Sprint Retrospective: <start> to <end>

## Overview
- **Duration**: X days
- **Commits**: X total
- **Contributors**: X people
- **Files changed**: X files

## What Went Well ✅
[List accomplishments based on feature commits]

## What Was Painful ⚠️
[List challenges inferred from patterns]

## Patterns & Insights 📊
[Metrics and observations]

## Action Items 🎯
[Concrete next steps]

## Detailed Commit Breakdown
[Table of commits by category]
```

IMPORTANT:
- Be objective—base insights on data, not assumptions
- Highlight both positives and concerns
- Make action items specific and actionable
- Use git commands via Bash tool
```

#### Step 3: Test on orbital-travel-planner

```
/retro-prep
```

Enter a date range (e.g., last 2 weeks).

#### Step 4: Test on a Different Repo

```bash
cd ~/different-project
```

```
/retro-prep
```

Verify it works on different repo structures.

#### Step 5: Enhance with Git Stats

Add more sophisticated analysis:

```bash
# Get churn stats
git log --since="<start>" --until="<end>" --pretty=tformat: --numstat | awk '{add+=$1; del+=$2} END {print add, del}'

# Get author stats
git shortlog --since="<start>" --until="<end>" -sn
```

### Success Criteria ✅

- [ ] Skill works on orbital-travel-planner
- [ ] Skill works on at least one other repo
- [ ] Report includes all required sections
- [ ] Metrics are accurate
- [ ] Output saves >10 min vs. manual analysis

---

## Option 2: `/pr-impact` - Pull Request Impact Analysis

### What It Does
Analyzes a PR to understand blast radius, affected systems, and testing requirements.

### Step-by-Step Implementation

#### Step 1: Create the Skill

```bash
mkdir ~/.claude/skills/pr-impact
cd pr-impact
```

Create `skill.json`:

```json
{
  "name": "pr-impact",
  "version": "1.0.0",
  "description": "Analyzes pull request blast radius and generates review checklist",
  "author": "Your Name",
  "invocation": "/pr-impact"
}
```

#### Step 2: Write the Skill Prompt

Create `prompt.txt`:

```txt
You are a pull request impact analyzer. You assess the scope and risk of code changes.

PROCESS:

1. ASK for PR number or URL

2. FETCH PR data using gh CLI:
   - gh pr view <number> --json title,body,files,additions,deletions
   - gh pr diff <number>

3. ANALYZE impact:
   - **Files changed**: Count and categorize (backend, frontend, config, tests, docs)
   - **Lines changed**: Additions vs. deletions (large changes = higher risk)
   - **Affected systems**: Identify services, endpoints, database schemas
   - **Dependencies**: Find imports, API calls, database queries
   - **Breaking changes**: Look for signature changes, removed endpoints, schema migrations

4. DETERMINE test requirements:
   - **Unit tests**: Functions/classes modified
   - **Integration tests**: If multiple services affected
   - **E2E tests**: If user-facing flows changed
   - **Performance tests**: If critical path modified
   - **Security review**: If auth, permissions, or data access changed

5. ASSESS risk level:
   - **Low**: <50 lines, single file, well-tested area
   - **Medium**: 50-200 lines, multiple files, some test coverage
   - **High**: >200 lines, cross-cutting, lacks tests, touches critical path

6. GENERATE review checklist:
   - Code quality checks
   - Security considerations
   - Performance implications
   - Breaking change verification
   - Test coverage requirements
   - Deployment considerations

7. WRITE to pr-impact-<number>.md

FORMAT:
```markdown
# PR Impact Analysis: #<number>

## Summary
- **Title**: <title>
- **Risk Level**: Low/Medium/High
- **Files Changed**: X files (breakdown)
- **Lines Changed**: +X / -X

## Affected Systems
[List services, endpoints, schemas]

## Breaking Changes
[List potential breaking changes, or "None identified"]

## Test Requirements
- [ ] Unit tests for <specific components>
- [ ] Integration tests for <interactions>
- [ ] E2E tests for <user flows>
- [ ] Performance tests for <critical paths>

## Review Checklist
- [ ] Code follows project style guide
- [ ] Error handling is comprehensive
- [ ] Security: auth/validation checks present
- [ ] Performance: no obvious bottlenecks
- [ ] Documentation updated
- [ ] Database migrations are safe (if applicable)

## Deployment Considerations
[Feature flags, rollout plan, rollback strategy]

## Files Changed
<table of files with impact assessment>
```

TOOLS REQUIRED:
- gh CLI (GitHub CLI)
- Access to current repository

ERROR HANDLING:
- If gh not installed: provide manual instructions
- If PR not found: verify number and repo
- If diff too large: analyze files list instead
```

#### Step 3: Test on a Real PR

Find a recent PR in orbital-travel-planner (or create one):

```bash
gh pr list
```

```
/pr-impact

PR #123
```

#### Step 4: Verify Accuracy

Manually review the PR and check if the analysis:
- Correctly identified affected files
- Found breaking changes (if any)
- Suggested appropriate tests
- Assessed risk accurately

### Success Criteria ✅

- [ ] Skill works with gh CLI
- [ ] Correctly identifies affected systems
- [ ] Risk assessment is reasonable
- [ ] Test checklist is specific
- [ ] Review checklist is actionable

---

## Option 3: `/onboard-service` - Service Onboarding Guide

### What It Does
Generates comprehensive onboarding documentation for a service repository.

### Implementation Outline

**Key features:**
- Analyzes repo structure
- Identifies entry points (main.py, routes, handlers)
- Maps dependencies (requirements.txt, package.json, etc.)
- Finds configuration (env vars, config files)
- Generates ASCII or mermaid architecture diagram
- Creates setup checklist

**Output:** `ONBOARDING.md` with everything a new engineer needs

### Success Criteria ✅
- Works on any Python/JS service
- Identifies all external dependencies
- Setup instructions are accurate
- Architecture diagram is helpful

---

## Option 4: `/incident-debrief` - Incident Post-Mortem Generator

### What It Does
Analyzes incident logs, errors, and timeline to generate post-mortem documentation.

### Implementation Outline

**Inputs:**
- Log files
- Error messages
- Incident timeline (from Slack, PagerDuty, etc.)

**Analysis:**
- Construct event timeline
- Identify root cause(s)
- Find contributing factors
- Assess impact

**Output:**
- Structured post-mortem document
- Action items to prevent recurrence
- Links to relevant code/config

### Success Criteria ✅
- Timeline is accurate
- Root cause is identified
- Prevention steps are actionable
- Document follows post-mortem template

---

## Option 5: `/debt-audit` - Technical Debt Assessment

### What It Does
Scans codebase for technical debt and prioritizes by risk.

### Implementation Outline

**Scans for:**
- TODO/FIXME/XXX/HACK comments
- Missing tests (functions without coverage)
- Deprecated API usage
- Code duplication
- Hardcoded values

**Prioritization:**
- Critical path files (high traffic)
- Frequently changed files (high churn)
- Security-sensitive code

**Output:**
- Ranked list of debt items
- Estimated effort to fix
- Suggested remediation steps

### Success Criteria ✅
- Finds all debt markers
- Prioritization is sensible
- Remediation steps are specific
- Report is actionable

---

## General Implementation Guide (All Skills)

### Phase 1: Skeleton (10 min)

1. Create skill directory and files
2. Write basic prompt
3. Test invocation

### Phase 2: Core Logic (25 min)

1. Implement main analysis logic
2. Use appropriate tools (Bash, Glob, Grep, Read)
3. Spawn agents if needed

### Phase 3: Output Generation (15 min)

1. Format results as markdown
2. Include metrics and insights
3. Make it scannable (headings, tables, lists)

### Phase 4: Testing & Polish (10 min)

1. Test on orbital-travel-planner
2. Test on a different repo
3. Fix edge cases
4. Add error handling

## Making Skills Portable

### Parameterization
Don't hardcode paths or repo-specific values:
```python
# Bad
api_files = "app/api/*.py"

# Good
api_files = find_api_files()  # Searches common locations
```

### Graceful Degradation
Handle missing tools or files:
```python
if gh_cli_available():
    use_gh_cli()
else:
    provide_manual_instructions()
```

### Repo Type Detection
Adapt to different project structures:
```python
if exists("pyproject.toml"):
    # Python project
elif exists("package.json"):
    # JavaScript project
elif exists("Cargo.toml"):
    # Rust project
```

## Documentation Template

Create a README for your skill:

```markdown
# <Skill Name>

## Purpose
[One sentence: what problem does this solve?]

## Usage
```
/skill-name [optional args]
```

## Parameters
- `param1`: Description (optional/required)
- `param2`: Description (optional/required)

## Example Output
[Screenshot or sample output]

## Requirements
- Git repository
- Python 3.9+ (if applicable)
- GitHub CLI (if applicable)

## How It Works
1. Step 1
2. Step 2
3. Step 3

## Limitations
- Limitation 1
- Limitation 2

## Tips
- Tip 1
- Tip 2
```

## Stage 4 Complete! 🎉

You now have:
- A practical workflow skill
- Understanding of skill portability
- Documentation for team sharing
- Experience with real-world automation

### Quick Knowledge Check

1. What makes a skill portable?
2. When should you spawn agents vs. use direct tools?
3. How do you handle missing dependencies gracefully?
4. What makes skill documentation good?
5. When is a skill worth building vs. one-off prompt?

## What's Next?

In [Stage 5: MCP Server Development](./stage5-mcp-servers.md), you'll build a custom MCP server that extends Claude's capabilities with domain-specific tools!

---

**Navigation:**
⬅️ [Back: Stage 3](./stage3-orchestration.md) | [Overview](./README.md) | ➡️ [Next: Stage 5](./stage5-mcp-servers.md)
