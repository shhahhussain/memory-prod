# Topic: asyncio.gather vs TaskGroup — Which One for Fan-Out

**Time:** 20 min
**Goal:** Understand WHY you use gather() and not TaskGroup for MINDY's agent dispatch

---

## What to Search
- "asyncio gather vs TaskGroup Python"
- "asyncio gather return_exceptions partial success"
- "asyncio TaskGroup cancel on failure"

## The Problem
MINDY dispatches to FINDR + TASKR + CAMPA in parallel. If TASKR fails (Asana is down), you still want FINDR + CAMPA results. You do NOT want everything to cancel.

## asyncio.gather (USE THIS)
```python
results = await asyncio.gather(
    findr.execute(request),
    taskr.execute(request),
    campa.execute(request),
    return_exceptions=True,  # KEY: failures become Exception objects, not raised
)

successes = [r for r in results if not isinstance(r, BaseException)]
failures = [r for r in results if isinstance(r, BaseException)]
# successes = [findr_result, campa_result]  ← TASKR failed but we still got 2/3
```

## asyncio.TaskGroup (DON'T USE)
```python
async with asyncio.TaskGroup() as tg:
    tg.create_task(findr.execute(request))
    tg.create_task(taskr.execute(request))  # If this fails...
    tg.create_task(campa.execute(request))
# ...ALL tasks get cancelled. ExceptionGroup raised. Zero results.
```

## With Timeouts
```python
tasks = [
    asyncio.wait_for(agent.execute(request), timeout=30.0)
    for agent in [findr, taskr, campa]
]
results = await asyncio.gather(*tasks, return_exceptions=True)
# TimeoutError for slow agents, real results for fast ones
```

## What to Understand
- [ ] `return_exceptions=True` makes failures non-fatal
- [ ] `TaskGroup` is all-or-nothing (Python 3.11+)
- [ ] `asyncio.wait_for()` adds per-agent timeouts
- [ ] How to separate successes from failures in results
