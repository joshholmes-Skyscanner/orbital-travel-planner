# Stage 3: Daily Workflow Skills

**Time:** 120 minutes
**Goal:** Build practical skills for common engineering workflows

## Learning Objectives

- Create real-world workflow automation
- Make skills portable across repositories
- Design for team distribution
- Understand skill composition patterns

## Overview

Choose ONE skill to build from the options below. Focus on:
- **Portability**: Works on any repository
- **Usefulness**: Saves >10 minutes vs. manual process
- **Documentation**: Clear usage examples
- **Composability**: Can combine with other skills

## Skill Options

### Option 1: Sprint Retrospective Preparation
### Option 2: Pull Request Impact Analysis
### Option 3: Service Onboarding Guide
### Option 4: Incident Post-Mortem Generator
### Option 5: Technical Debt Assessment

Or propose your own workflow automation.

---

## Option 1: Sprint Retrospective Preparation

### Purpose
Analyzes git history to generate sprint retrospective talking points.

### Implementation

#### Create the Skill

```bash
mkdir -p ~/.claude/skills/retro-prep
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

#### Create the Prompt

Create `prompt.txt`:

```text
You are a sprint retrospective preparation assistant generating insights from git history.

PROCESS:

1. Ask for date range (default: last 2 weeks):
   - Start date (YYYY-MM-DD)
   - End date (YYYY-MM-DD)

2. Analyze git history using Bash:
   - git log --since="<start>" --until="<end>" --pretty=format:"%h|%an|%ad|%s" --date=short
   - git log --since="<start>" --until="<end>" --name-only --pretty=format:""

3. Categorize commits:
   - Features: "feat:", "add", "implement"
   - Bugs: "fix:", "bug", "patch"
   - Refactoring: "refactor", "clean", "improve"
   - Tech debt: "debt", "TODO", "deprecate"

4. Identify patterns:
   - Most changed files (high churn = hotspot)
   - Commit frequency by day
   - Author contributions
   - Common themes

5. Generate report (retro-prep.md) with sections:
   - Overview (duration, commits, contributors)
   - What went well (features, fixes, improvements)
   - What was painful (high churn, blockers inferred from messages)
   - Patterns & insights (metrics, observations)
   - Action items (refactoring needs, test gaps)

METRICS:
- Total commits
- Commits per category
- Top 5 most-changed files
- Commit frequency graph (ASCII art)

Be objective. Base insights on data, not assumptions.
```

#### Test the Skill

```
/retro-prep
```

Enter a date range to analyze.

#### Verify Portability

Test on a different repository:

```bash
cd ~/different-project
```

```
/retro-prep
```

Verify it works on different repo structures.

---

## Option 2: Pull Request Impact Analysis

### Purpose
Analyzes PR to understand blast radius, affected systems, and testing requirements.

### Implementation

#### Create the Skill

```bash
mkdir -p ~/.claude/skills/pr-impact
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

#### Create the Prompt

Create `prompt.txt`:

```text
You are a pull request impact analyzer assessing code change scope and risk.

PROCESS:

1. Ask for PR number or URL

2. Fetch PR data using gh CLI:
   - gh pr view <number> --json title,body,files,additions,deletions
   - gh pr diff <number>

3. Analyze impact:
   - Files changed (categorize: backend, frontend, config, tests, docs)
   - Lines changed (large changes = higher risk)
   - Affected systems (services, endpoints, schemas)
   - Dependencies (imports, API calls, queries)
   - Breaking changes (signature changes, removed endpoints)

4. Determine test requirements:
   - Unit tests (functions/classes modified)
   - Integration tests (multiple services affected)
   - E2E tests (user flows changed)
   - Performance tests (critical path modified)
   - Security review (auth/permissions/data access)

5. Assess risk level:
   - Low: <50 lines, single file, tested area
   - Medium: 50-200 lines, multiple files, partial coverage
   - High: >200 lines, cross-cutting, critical path

6. Generate review checklist with specific requirements

7. Write to pr-impact-<number>.md

ERROR HANDLING:
- If gh not installed: provide manual instructions
- If PR not found: verify number and repo
- If diff too large: analyze file list instead
```

#### Test the Skill

```bash
gh pr list
```

```
/pr-impact

PR #123
```

Verify analysis accuracy against actual PR.

---

## Making Skills Portable

### Parameterization

Avoid hardcoded paths:

```python
# Bad
api_files = "app/api/*.py"

# Good
api_files = find_api_files()  # Searches common locations
```

### Graceful Degradation

Handle missing tools:

```python
if gh_cli_available():
    use_gh_cli()
else:
    provide_manual_instructions()
```

### Repository Type Detection

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
# Skill Name

## Purpose
One sentence: what problem does this solve?

## Usage
```
/skill-name [optional args]
```

## Parameters
- `param1`: Description (optional/required)

## Example Output
[Sample output or screenshot]

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
```

## Verification

- [ ] Skill works on orbital-travel-planner
- [ ] Skill works on at least one other repository
- [ ] Report includes all required sections
- [ ] Output saves >10 minutes vs. manual process
- [ ] Skill is documented with usage examples

## Stage 3 Summary

You have now:
- Built a practical workflow skill
- Understood skill portability patterns
- Created documentation for team sharing
- Learned skill composition principles

### Knowledge Check

1. What makes a skill portable?
2. When should you spawn agents vs. use direct tools?
3. How do you handle missing dependencies gracefully?
4. What makes skill documentation effective?
5. When is a skill worth building vs. one-off prompt?

---

**Next:** [Showcase: Share What You Built](./showcase.md)
