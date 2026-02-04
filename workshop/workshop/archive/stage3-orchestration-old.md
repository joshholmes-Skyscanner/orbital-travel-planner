# Stage 3: Resilience Testing Skills

**Time:** 60 minutes
**Goal:** Build a skill that tests system resilience under failure conditions

## Learning Objectives

- Build a chaos engineering skill that finds resilience issues
- Understand when parallel task execution helps
- Create skills that propose concrete fixes
- Learn patterns for skills with complex workflows

## Overview

You'll build `/chaos-test` - a skill that:
- Injects failures into your application
- Generates load to trigger issues
- Analyzes failure patterns
- Proposes specific fixes

**Why this uses agents:** This skill has four distinct phases that can run independently. Using agents lets us run some in parallel (faster) and keeps each phase focused on one job.

## What You're Building

A comprehensive chaos testing skill that:
1. Finds where your system breaks under stress
2. Identifies patterns in failures
3. Recommends specific code changes
4. Helps you build more resilient systems

From the user's perspective: `/chaos-test` → detailed report with fixes

Internally: Uses multiple agents for efficiency, but that's transparent to the user.

## Create the Chaos Testing Skill

### 1. Set Up the Skill

```bash
mkdir -p ~/.claude/skills/chaos-test
cd chaos-test
```

Create `skill.json`:

```json
{
  "name": "chaos-test",
  "version": "1.0.0",
  "description": "Tests system resilience by injecting failures and analyzing patterns",
  "author": "Your Name",
  "invocation": "/chaos-test"
}
```

### 2. Write the Skill Logic

Create `prompt.txt`:

```text
You are a chaos engineering specialist. Test system resilience by injecting failures, generating load, analyzing patterns, and proposing fixes.

PHASE 1: PARALLEL SETUP (Run simultaneously for speed)

Agent 1 (Chaos Injector) - Background:
"Modify the application to inject random failures:
- Add random delays: time.sleep(random.uniform(0.1, 2))
- Add random exceptions: raise Exception('Chaos!') with 10% probability
- Document injection points in chaos-config.json"

Agent 2 (Load Generator) - Background:
"Generate load against the API:
- 50 requests to /api/destinations
- 50 requests to /api/bookings
- Log all results (response time, status, errors) to load-results.json"

WHY PARALLEL: These tasks are independent. Running them together is faster.
WHY BACKGROUND: They take time. We don't want to wait.

PHASE 2: WAIT FOR DATA
Poll Agent 2's output until load-results.json has sufficient data (100+ entries) or 60 seconds elapsed.

PHASE 3: ANALYSIS (Sequential - needs Phase 2 data)

Agent 3 (Pattern Analyzer):
"Read load-results.json and analyze:
- Which endpoints failed most frequently?
- What are the error rates and latency percentiles (p95, p99)?
- Correlate failures with chaos-config.json to identify root causes
Write analysis to failure-patterns.json"

WHY SEQUENTIAL: Needs data from Agent 2.
WHY AGENT: Fresh context focused purely on data analysis.

PHASE 4: FIXES (Sequential - needs Phase 3 analysis)

Agent 4 (Fix Proposer):
"Read failure-patterns.json and propose specific code fixes:
- For each pattern, suggest concrete changes (file, line, what to change, why)
- Prioritize by impact (highest error rate first)
Write proposals to fix-proposals.json"

WHY SEQUENTIAL: Needs analysis from Agent 3.
WHY AGENT: Fresh context focused on fix generation.

PHASE 5: REPORT
Read all JSON files and create chaos-test-report.md:
- Chaos configuration summary
- Load testing results (requests, success rate, latencies)
- Failure patterns identified
- Prioritized fix proposals
- Top 3 most critical issues

IMPLEMENTATION NOTES:
- Agents 1 & 2 must spawn in ONE message (both Task calls together) to run in parallel
- Use run_in_background: true for long-running tasks
- Poll with TaskOutput to check Agent 2 progress
- Only spawn Agent 3 after sufficient data collected
- Only spawn Agent 4 after Agent 3 completes
- If timeout, proceed with partial data (graceful degradation)

The user just sees: /chaos-test → comprehensive report
The agents are how we make it fast and efficient internally.
```

### 3. Prepare the Environment

Ensure the application is running:

```bash
cd /path/to/orbital-travel-planner
python -m flask run
```

Verify endpoints respond:

```bash
curl http://localhost:5000/api/destinations
curl http://localhost:5000/api/bookings
```

### 4. Run the Chaos Test

```
/chaos-test
```

The skill will:
1. Inject chaos and generate load (in parallel)
2. Wait for sufficient data
3. Analyze failure patterns
4. Propose specific fixes
5. Generate comprehensive report

This takes a few minutes. The skill is doing real chaos testing on your system.

### 5. Review the Report

```bash
cat chaos-test-report.md
```

Expected sections:
- **Chaos Configuration**: What failures were injected
- **Load Test Results**: Total requests, success rate, latencies
- **Failure Patterns**: Which endpoints failed, why, how often
- **Fix Proposals**: Ranked list of code changes with specifics

### 6. Implement a Fix

```
Based on chaos-test-report.md, implement the highest-priority fix
```

The skill should:
1. Read the fix proposal
2. Find the relevant code
3. Apply the fix (add timeout, retry logic, error handling)
4. Show you what changed

### 7. Verify the Fix

Re-run chaos testing:

```
/chaos-test
```

Compare the new report to the previous one:
- Did error rates decrease?
- Are latencies more stable?
- Did the specific failure pattern disappear?

### What Just Happened?

From your perspective: You ran `/chaos-test` and got a detailed report with fixes.

Internally: The skill used four agents with a mix of parallel and sequential execution. But that's an implementation detail that made the skill faster and more efficient.

**Why this design works:**
- Chaos injection and load generation are independent → run in parallel
- Pattern analysis needs load data → wait and run sequentially
- Fix proposals need pattern analysis → wait and run sequentially
- Each phase gets fresh, focused context
- Cheaper models can handle specific tasks

## Verification

- [ ] `/chaos-test` skill works end-to-end
- [ ] Report identifies real failure patterns
- [ ] Fix proposals are specific and actionable
- [ ] Re-running after fixes shows improvement
- [ ] Understand why some work runs in parallel vs. sequential

## Troubleshooting

**Agents run one at a time instead of parallel:**
- Ensure both Task calls are in the SAME message in the prompt
- Both must specify `run_in_background: true`

**Background tasks never finish:**
- Add timeout check (60 seconds max)
- Proceed with partial data if needed

**Not enough data collected:**
- Increase request count in load generator
- Lower the data threshold

**Can't identify failure patterns:**
- Increase chaos injection probability
- Verify chaos-config.json is being used

## Understanding the Design

### Why Parallel Execution Here?

Chaos injection and load generation are completely independent. Running them in parallel:
- Finishes faster (both tasks complete simultaneously)
- Uses resources efficiently
- Doesn't add complexity (no coordination needed)

### Why Sequential After That?

Pattern analysis needs load data. Fix proposals need pattern analysis. This creates natural dependencies that require sequential execution.

### Why Not Just Do Everything Directly in the Skill?

You could, but:
- Context would get huge (chaos code + load results + analysis + fixes)
- Can't use cheaper models for focused tasks
- Can't run anything in parallel
- Harder to maintain and debug

Agents let the skill delegate work efficiently while staying focused on coordination.

## Stage 3 Summary

You built `/chaos-test` - a powerful resilience testing skill that:
- Identifies system weaknesses under failure conditions
- Analyzes patterns in failures
- Proposes concrete, prioritized fixes
- Uses agents internally for speed and efficiency

### Key Insights

**Skills vs. Agents:**
- Users invoke skills (`/chaos-test`)
- Skills may use agents internally (implementation detail)
- Focus on what the skill does, not how it does it

**When parallel execution helps:**
- Tasks are independent
- Both take significant time
- No coordination needed
- Results don't depend on each other

**When sequential execution is needed:**
- Task B needs output from Task A
- Natural dependencies in the workflow
- Order matters for correctness

**Graceful degradation:**
- Set timeouts on long-running tasks
- Proceed with partial data when needed
- Report what worked and what didn't

### Knowledge Check

1. What does `/chaos-test` do for users?
2. Why do chaos injection and load generation run in parallel?
3. Why does pattern analysis wait for load generation?
4. When is it worth using agents in a skill vs. doing work directly?
5. What's "graceful degradation" and why does it matter?

### Advanced Exercises (Optional)

**Enhanced Chaos:**
Add more failure types (database timeouts, memory pressure, network issues).

**Real-Time Monitoring:**
Add a monitoring agent that watches logs in real-time and alerts on anomalies.

**Gradual Ramp:**
Gradually increase failure rates (5% → 10% → 20%) and track when the system breaks.

**Comparative Testing:**
Run chaos testing on two different branches and compare results.

---

**Next:** [Stage 4: Workflow Automation](./stage4-workflow-skills.md)
