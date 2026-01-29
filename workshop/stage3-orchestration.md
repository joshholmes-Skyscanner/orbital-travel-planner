# Stage 3: Advanced Agent Orchestration

**Time:** 13:00–14:00 (60 minutes)
**Goal:** Create skills that coordinate multiple specialized agents in parallel with complex dependency graphs.

## Learning Objectives

By the end of this stage, you'll master:
- Running agents in parallel with dependencies
- Using background tasks effectively
- Polling agent outputs with TaskOutput
- Building complex coordination patterns
- Chaos testing and failure injection

## What You're Building

A `/chaos-test` skill that orchestrates four agents with mixed parallel/sequential execution:
- **Agents 1 & 2**: Run in parallel (chaos injection + load generation)
- **Agent 3**: Waits for Agent 2, analyzes patterns
- **Agent 4**: Waits for Agent 3, proposes fixes

This creates a dependency graph:
```
Agent 1 (Chaos) ──┐
                  ├──> (both run in parallel)
Agent 2 (Load) ───┴──> Agent 3 (Analyze) ──> Agent 4 (Fix)
```

## Step 1: Understand the Architecture

### Parallel Execution
Agents 1 and 2 are independent—they don't need each other's outputs. Run them simultaneously.

### Sequential Execution
Agent 3 needs Agent 2's data. Agent 4 needs Agent 3's analysis. They must wait.

### Background Tasks
Long-running agents (chaos injection, load testing) should use `run_in_background: true`.

## Step 2: Create the Chaos Test Skill

```bash
mkdir ~/.claude/skills/chaos-test
cd chaos-test
```

Create `skill.json`:

```json
{
  "name": "chaos-test",
  "version": "1.0.0",
  "description": "Orchestrates chaos testing with parallel and sequential agents",
  "author": "Your Name",
  "invocation": "/chaos-test"
}
```

Create `prompt.txt`:

```txt
You are a chaos engineering orchestrator. You coordinate four agents to inject failures, generate load, analyze patterns, and propose fixes.

ARCHITECTURE:

Phase 1: PARALLEL CHAOS & LOAD (Background)
- Agent 1 (Chaos Injector): Modify the app to inject random failures
  - Add random delays (time.sleep(random.uniform(0.1, 2)))
  - Add random exceptions (raise Exception("Chaos!") with 10% probability)
  - Write chaos points to chaos-config.json
  - Run in BACKGROUND

- Agent 2 (Load Generator): Repeatedly call API endpoints
  - Make 50 requests to /api/destinations
  - Make 50 requests to /api/bookings
  - Log response times, status codes, errors to load-results.json
  - Run in BACKGROUND

Phase 2: WAIT FOR DATA
- Use TaskOutput to poll Agent 2's background task
- Wait until load-results.json has at least 100 entries
- Maximum wait: 60 seconds

Phase 3: ANALYZE PATTERNS (Sequential)
- Agent 3 (Pattern Analyzer): Read load-results.json
  - Identify failure patterns (which endpoints failed most?)
  - Calculate error rates, p95/p99 latencies
  - Correlate with chaos-config.json to find root causes
  - Write analysis to failure-patterns.json

Phase 4: PROPOSE FIXES (Sequential)
- Agent 4 (Fix Proposer): Read failure-patterns.json
  - For each pattern, propose specific code fixes
  - Include: file path, line number, what to change, why
  - Prioritize by impact (highest error rate first)
  - Write proposals to fix-proposals.json

Phase 5: REPORT
- Read all JSON files
- Create comprehensive report: chaos-test-report.md
- Include: chaos config, load results summary, failure patterns, fix proposals
- Highlight top 3 most critical issues

CRITICAL RULES:
1. Agents 1 & 2 MUST run in parallel using run_in_background: true
2. Poll Agent 2 with TaskOutput—don't assume it's done
3. Only spawn Agent 3 after sufficient data collected
4. Only spawn Agent 4 after Agent 3 completes
5. If background tasks timeout (>60s), proceed with partial data
6. All agent communication via JSON files

TASK COORDINATION:
- Use a single message with multiple Task calls for parallel agents
- Wait for previous agent completion before spawning next
- Check file existence before reading

ERROR HANDLING:
- If Agent 1 or 2 fails, note it but continue with available data
- If no data collected, report "insufficient data for analysis"
- If timeout occurs, save partial results and explain in report
```

## Step 3: Prepare the Test Environment

Before running chaos tests, ensure the orbital-travel-planner app is running:

```bash
cd /path/to/orbital-travel-planner
python -m flask run
```

In another terminal, verify endpoints work:

```bash
curl http://localhost:5000/api/destinations
curl http://localhost:5000/api/bookings
```

## Step 4: Run the Chaos Test

Invoke the skill:

```
/chaos-test
```

Watch the orchestration:

1. **Agents 1 & 2 spawn together** (you'll see both Task calls in one message)
2. **Polling begins** (TaskOutput checks Agent 2's progress)
3. **Agent 3 spawns** after data is ready
4. **Agent 4 spawns** after analysis completes
5. **Report generated** with all findings

## Step 5: Monitor Background Agents

While chaos testing runs, you can manually check progress:

```bash
# Watch the load results accumulate
watch -n 1 'wc -l load-results.json'

# See chaos injection points
cat chaos-config.json

# Monitor app logs for injected failures
tail -f /path/to/app/logs/*.log
```

## Step 6: Analyze the Report

Read the generated report:

```bash
cat chaos-test-report.md
```

It should include:
- **Chaos Configuration**: What failures were injected
- **Load Test Summary**: Total requests, success rate, latencies
- **Failure Patterns**: Which endpoints failed, why, how often
- **Fix Proposals**: Ranked list of code changes to improve resilience

## Step 7: Implement a Fix

Pick the top-priority fix from the report and implement it:

```
Based on the chaos-test-report.md, implement the highest-priority fix to improve resilience.
```

Claude should:
1. Read the fix proposal
2. Locate the relevant code
3. Apply the fix (e.g., add timeout, retry logic, error handling)
4. Verify the change

## Step 8: Verify the Fix

Re-run chaos testing to verify improvement:

```
/chaos-test
```

Compare the new report to the previous one:
- Did error rates decrease?
- Are latencies more stable?
- Did the specific failure pattern disappear?

## Step 9: Understanding Task Coordination

Let's examine how parallel vs. sequential execution works.

**Parallel (both in one message):**
```python
# Claude's internal task spawning
Task(agent_type="Bash", task="chaos injection", run_in_background=True)
Task(agent_type="Bash", task="load generation", run_in_background=True)
```

**Sequential (wait for completion):**
```python
# Wait for Agent 2
result = TaskOutput(task_id="agent_2_id", block=True)

# Only then spawn Agent 3
Task(agent_type="general-purpose", task="analyze patterns")
```

## Success Criteria ✅

- [ ] Four agents run with correct dependencies
- [ ] Agents 1 & 2 run in parallel (background)
- [ ] Agent 3 waits for Agent 2's data
- [ ] Agent 4 waits for Agent 3's analysis
- [ ] Report includes all phases
- [ ] You identified at least one real issue
- [ ] You can diagram the agent flow

### Troubleshooting

**Problem:** Agents run sequentially instead of parallel
- **Solution:** Ensure both Task calls are in the SAME message
- Check both have `run_in_background: true`

**Problem:** Background task never completes
- **Solution:** Add timeout to TaskOutput (e.g., `timeout: 60000`)
- Check the app is actually running

**Problem:** Insufficient data collected
- **Solution:** Increase number of requests in load generator
- Reduce wait threshold in the skill

**Problem:** Can't find failure patterns
- **Solution:** Inject more obvious failures (higher probability)
- Check chaos-config.json was actually applied

## Going Deeper (Optional)

### Challenge 1: Enhanced Chaos Injection

Modify Agent 1 to inject more sophisticated failures:
- Database connection failures
- Network timeouts
- Memory pressure
- Rate limit errors

### Challenge 2: Real-Time Monitoring

Add a fifth agent that monitors in real-time:
```
Agent 5 (Monitor): Runs continuously, tails logs, alerts on anomalies
```

### Challenge 3: Gradual Chaos

Instead of all-at-once chaos, gradually increase failure rates:
- Minute 1: 5% failure rate
- Minute 2: 10% failure rate
- Minute 3: 20% failure rate

Track when the system breaks.

### Challenge 4: Comparative Analysis

Run chaos testing on two branches:
- main branch (baseline)
- feature branch (after fix)

Compare results to quantify improvement.

## Real-World Applications

This pattern applies to many scenarios:

**Performance Testing:**
- Agent 1: Warm up cache
- Agent 2: Ramp up load
- Agent 3: Analyze metrics
- Agent 4: Identify bottlenecks

**Security Scanning:**
- Agent 1: Crawl endpoints
- Agent 2: Test authentication
- Agent 3: Find vulnerabilities
- Agent 4: Suggest mitigations

**Deployment Validation:**
- Agent 1: Deploy to staging
- Agent 2: Run smoke tests
- Agent 3: Compare to prod metrics
- Agent 4: Approve or rollback

## Key Patterns Learned

### Dependency Management
- **Independent**: Run in parallel
- **Sequential**: Wait for previous completion
- **Mixed**: Some parallel, some sequential

### Background Task Polling
```python
# Spawn background task
task_id = Task(..., run_in_background=True)

# Poll until ready
while not ready:
    output = TaskOutput(task_id, block=False, timeout=5000)
    ready = check_output_sufficient(output)

# Proceed with next step
```

### Graceful Degradation
- Set timeouts on background tasks
- Proceed with partial data if needed
- Report what worked and what didn't

## Stage 3 Complete! 🎉

You now master:
- Complex agent dependency graphs
- Parallel and sequential execution
- Background task management
- Chaos engineering patterns
- Fix verification loops

### Quick Knowledge Check

1. When should agents run in parallel vs. sequentially?
2. How do you check if a background agent is done?
3. What's the max wait time for background tasks?
4. How should agents communicate in parallel workflows?
5. What's graceful degradation in agent orchestration?

## What's Next?

In [Stage 4: Daily Workflow Skills](./stage4-workflow-skills.md), you'll build practical skills for real engineering workflows like retros, PR reviews, and onboarding!

---

**Navigation:**
⬅️ [Back: Stage 2](./stage2-meta-programming.md) | [Overview](./README.md) | ➡️ [Next: Stage 4](./stage4-workflow-skills.md)
