# Advanced Claude Code Workshop

Build reusable skills, validation harnesses, and agent coordination patterns for daily use.

## Workshop Details

- **Duration:** 5.5 hours (10:30–16:00, lunch 12:00–13:00)
- **Target Audience:** Backend Python engineers familiar with Claude and LLM basics
- **Core Topics:** Custom skills, agent orchestration, self-validation loops, MCP servers

## Learning Outcomes

By the end of this workshop, you will:

- Create 6+ custom Claude Code skills for validation, testing, and workflow automation
- Build self-validating skills that automatically fix their own errors
- Develop custom MCP servers extending Claude's capabilities
- Understand when skills benefit from using agents internally (for clean context and efficiency)
- Apply these patterns to your daily engineering work

## Prerequisites

Ensure you have the following installed:

- Claude Code CLI (configured and authenticated)
- Python 3.9 or later
- Git and GitHub CLI (`gh`)
- Text editor or IDE
- orbital-travel-planner repository (cloned)

## Workshop Structure

### Morning Session (10:30–12:00)

**[Stage 1: Foundations](./stage1-foundations.md)** — 30 minutes

Core building blocks: skills, agents, and MCP servers.

**[Stage 2: Self-Validating Skills](./stage2-meta-programming.md)** — 60 minutes

Build skills that validate their work and fix errors automatically.

### Afternoon Session (13:00–16:00)

**[Stage 3: Resilience Testing Skills](./stage3-orchestration.md)** — 60 minutes

Build a chaos engineering skill that finds and fixes system weaknesses.

**[Stage 4: Workflow Automation](./stage4-workflow-skills.md)** — 60 minutes

Practical skills for sprint retros, PR analysis, and code audits.

**[Stage 5: MCP Server Development](./stage5-mcp-servers.md)** — 45 minutes

Custom MCP servers with domain-specific tools.

**[Stage 6: Integration](./stage6-integration.md)** — 15 minutes

Skill composition and team distribution planning.

## Self-Paced Learning

Each stage guide includes:

- Clear learning objectives
- Step-by-step instructions with code examples
- Success criteria and verification steps
- Troubleshooting common issues
- Advanced challenges for early finishers

These guides are designed for independent completion if you cannot attend the live workshop.

## Getting Started

1. Review the prerequisites above
2. Clone the orbital-travel-planner repository
3. Start with [Stage 1: Foundations](./stage1-foundations.md)
4. Progress through stages sequentially
5. Complete success criteria before advancing

## Workshop Philosophy

The orbital-travel-planner serves as a learning vehicle. The real goal is building reusable patterns you'll apply to production codebases.

Focus on understanding the underlying patterns rather than memorizing specific implementations.

## Support

During the workshop:
- Ask questions at any time
- Collaborate with other participants
- Reference troubleshooting sections in each guide

After the workshop:
- Return to these guides as reference material
- Check the troubleshooting sections
- Share your implementations with the team

## What You'll Build

### Custom Skills
- API validation and testing automation
- Chaos engineering and resilience testing
- Workflow automation (retros, PR analysis, onboarding)
- Comprehensive audit orchestration

### MCP Servers
- HTTP endpoint validation
- Test data generation
- API version comparison
- Security scanning

### Key Patterns
- Self-validating skills
- Using agents for efficiency (clean context, cheaper models)
- Parallel vs. sequential task execution
- MCP servers for external capabilities

---

**Ready to begin?** [Start with Stage 1: Foundations](./stage1-foundations.md)
