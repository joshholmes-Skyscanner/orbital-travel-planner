# Showcase: Share What You Built

**Time:** 60 minutes
**Goal:** Demonstrate your daily workflow skill and share learnings with the group

## Format

### Individual Presentations (5-7 minutes each)

Each participant presents the skill they built in Stage 3:

1. **Problem Statement** (1 min)
   - What engineering task does this automate?
   - Why is this painful to do manually?
   - Who would use this skill?

2. **Live Demo** (2-3 min)
   - Run the skill on orbital-travel-planner
   - Show the output/report generated
   - Highlight key features

3. **Technical Deep-Dive** (2 min)
   - How does it work internally?
   - Did you use agents? Why or why not?
   - What was the hardest part to implement?

4. **Real-World Application** (1 min)
   - How would you use this at work?
   - What would you change with more time?
   - Could this be shared with the team?

### Group Discussion (Remaining Time)

After all presentations, discuss as a group:

1. **Impact Assessment**
   - Which skill would save the most time?
   - Which skill was the most creative?
   - Which skill would you want to use?

2. **Agent Orchestration Insights**
   - When did using agents help vs. complicate?
   - What patterns emerged across different skills?
   - When is direct tool use better than spawning agents?

3. **Taking Skills Home**
   - Which patterns will you use at work?
   - What would you build next?
   - How would you share skills with your team?

## Presentation Tips

### Before Your Demo

**Prepare your environment:**
```bash
# Ensure you're in the workshop repo
cd /path/to/orbital-travel-planner

# Test your skill one more time
/your-skill-name

# Have the output ready to show
```

**Prepare talking points:**
- Opening hook: "Ever spent 30 minutes preparing for a retro?"
- Key insight: "The skill uses 2 agents to..."
- Closing: "This would save me X hours per sprint"

### During Your Demo

**Show, don't tell:**
- Run the skill live (prepare fallback if it fails)
- Open the generated report
- Highlight 2-3 most interesting insights

**Be honest about challenges:**
- "I struggled with X, here's how I solved it..."
- "With more time, I would improve Y..."
- "I learned that Z pattern works better than..."

**Invite questions:**
- Pause for questions after technical deep-dive
- Offer to share implementation details after

### Common Demo Pitfalls

❌ Reading code line by line
✅ Show the outcome, explain the approach

❌ Apologizing for what doesn't work
✅ Frame challenges as learning opportunities

❌ Going over time
✅ Practice once, stick to 5-7 minutes

❌ Assuming everyone knows the context
✅ Briefly explain what the skill does

## Example Showcase Flow

**Participant 1: /retro-prep**
- Problem: "Sprint retros take 30 min of prep reviewing commits"
- Demo: Runs skill, shows categorized commits and patterns
- Technical: "Used git log parsing, categorization logic, no agents needed"
- Impact: "Would use this every 2 weeks, save ~20 hours/year"

**Participant 2: /pr-impact**
- Problem: "Hard to assess PR risk and test requirements"
- Demo: Analyzes a real PR, shows blast radius report
- Technical: "Used gh CLI + file analysis, spawned Explore agent for dependencies"
- Impact: "Would help with PR reviews, especially large changes"

**Participant 3: /debt-audit**
- Problem: "Tech debt is invisible until it's a crisis"
- Demo: Scans codebase, generates prioritized debt list
- Technical: "Coordinated 3 agents: search, analyze, prioritize"
- Impact: "Would run monthly, track debt over time"

**Group Discussion:**
- "/retro-prep most practical for immediate use"
- "Agent orchestration helped /debt-audit but /retro-prep didn't need it"
- "All skills could be shared with team via shared skills repo"

## Success Criteria

- [ ] You presented your skill to the group
- [ ] Your demo showed real output on orbital-travel-planner
- [ ] You explained your technical approach
- [ ] You articulated real-world value
- [ ] You participated in group discussion
- [ ] You identified patterns to apply at work

## Post-Workshop Actions

### Share Your Skill

**1. Document it**
Create a README in your skill directory:
```bash
cd ~/.claude/skills/your-skill
nano README.md
```

Include:
- Purpose
- Usage
- Example output
- Requirements
- Limitations

**2. Test portability**
Try your skill on 2-3 different repositories:
```bash
cd ~/different-project
/your-skill
```

Fix any hardcoded assumptions.

**3. Share with team**
Options for distribution:
- Team skills repository (git clone to ~/.claude/skills/)
- Internal documentation wiki
- Demo during team meeting
- Pair with teammate to customize

### Build Your Next Skill

Ideas based on workshop patterns:

**From /api-explorer pattern (sequential agents):**
- Database schema documenter
- Architecture diagram generator
- Dependency analyzer

**From /retro-prep pattern (git analysis):**
- Hotspot identifier (high-churn files)
- Contributor onboarding (who to ask about what)
- Release notes generator

**From /pr-impact pattern (blast radius):**
- Test coverage gap finder
- Breaking change detector
- Deployment risk assessor

### Continue Learning

**Deepen agent orchestration:**
- Parallel agents for independent tasks
- Error recovery and retry logic
- Agent result validation

**Explore MCP servers:**
- Build custom tools for your domain
- Integrate external APIs
- Create team-specific capabilities

**Advanced skill patterns:**
- Skills that call other skills
- Interactive skills with user input
- Background skills that monitor continuously

## Workshop Wrap-Up

You have now:
- ✅ Created custom skills from scratch
- ✅ Understood agent coordination patterns
- ✅ Built practical automation for daily workflows
- ✅ Shared learnings with peers
- ✅ Identified patterns to apply at work

### Final Reflection

Take 2 minutes to write down:
1. One skill pattern you'll use this week
2. One automation you'll build next month
3. One insight to share with your team

---

**Thank you for participating!**

Continue building skills, share them with your team, and apply these patterns to make your engineering work more efficient and enjoyable.
