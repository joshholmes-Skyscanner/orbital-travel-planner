# Advanced Claude Code Workshop

Build reusable skills and agent coordination patterns for daily use.

## Workshop Details

- **Duration:** 5.5 hours (10:30–16:00, lunch 12:00–13:00)
- **Target Audience:** Backend Python engineers familiar with Claude and LLM basics
- **Core Topics:** Custom skills, agent orchestration, MCP tooling, and practical daily workflow automation

## Learning Outcomes

By the end of this workshop, you will:

- Create custom Claude Code skills for workflow automation and agent orchestration
- Understand when skills benefit from using agents internally (for clean context and efficiency)
- Build practical, reusable skills for common engineering tasks
- Apply agent coordination patterns to your daily engineering work

## Prerequisites

Ensure you have the following installed:

- Claude Code CLI (configured and authenticated)
- Python 3.9 or later
- Git and GitHub CLI (`gh`)
- Text editor or IDE
- orbital-travel-planner repository (cloned)

## Workshop Structure

### Morning Session (10:30–13:00)

**[Stage 1: Foundations & Setup](./stage1-foundations.md)** — 30 minutes (10:30–11:00)

Core building blocks: skills, agents, and MCP servers.

**[Stage 2: Chaos Engineering & Agent Orchestration](./stage2-orchestration.md)** — 120 minutes (11:00–13:00)

Build a chaos testing skill with parallel and sequential agent coordination.

### Afternoon Session (13:00–16:00)

**[Stage 3: Daily Workflow Skills](./stage3-workflow-skills.md)** — 120 minutes (13:00–15:00)

Build practical, reusable skills for common engineering tasks (sprint retros, PR analysis, code audits).

**[Showcase: Share What You Built](./showcase.md)** — 60 minutes (15:00–16:00)

Demo your skills and share learnings with the group.

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
3. Start with [Stage 1: Foundations & Setup](./stage1-foundations.md)
4. Progress through stages sequentially
5. Complete success criteria before advancing

## Workshop Philosophy

The orbital-travel-planner serves as a learning vehicle. The real goal is building reusable patterns you'll apply to production codebases.

Focus on understanding the underlying patterns rather than memorizing specific implementations. The workshop emphasizes practical skills you can use immediately in your daily work.

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
- Chaos engineering and resilience testing
- Workflow automation (retros, PR analysis, onboarding, tech debt audits)
- Complex multi-agent orchestration with parallel and sequential execution

### Key Patterns
- Parallel vs. sequential agent coordination
- Using agents for efficiency (clean context, cheaper models)
- Data passing between agents via structured files
- Skills that coordinate multiple specialized agents
- Practical automation for daily engineering workflows

---

**Ready to begin?** [Start with Stage 1: Foundations & Setup](./stage1-foundations.md)
