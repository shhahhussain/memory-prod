# Topic: Agent Framework — Concurrent Fan-Out

**Time:** 30 min
**Goal:** Understand how to run multiple agents in parallel (MINDY dispatching to FINDR/TASKR/CAMPA)

---

## What to Search
- "Microsoft Agent Framework ConcurrentBuilder Python"
- "agent-framework FanOutEdgeGroup parallel"
- "agent framework concurrent execution samples"

## Docs to Read
- https://learn.microsoft.com/en-us/agent-framework/workflows/
- Blog: https://devblogs.microsoft.com/semantic-kernel/unlocking-enterprise-ai-complexity-multi-agent-orchestration-with-the-microsoft-agent-framework/

## What to Understand
- [ ] `ConcurrentBuilder` — how it works
- [ ] `FanOutEdgeGroup` — conditional parallel dispatch
- [ ] How results are collected from parallel agents
- [ ] What happens when one parallel agent fails (partial success?)
- [ ] How this compares to raw `asyncio.gather()`

## Key Question
Does the framework's ConcurrentBuilder support `return_exceptions=True` behavior (partial success), or does one failure kill everything? If it doesn't, you may need raw `asyncio.gather()` instead.

## n8n Equivalent
This replaces: MINDY dispatching to FINDR + TASKR + CAMPA simultaneously
