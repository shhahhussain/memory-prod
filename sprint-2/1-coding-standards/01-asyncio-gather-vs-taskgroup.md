# asyncio.gather vs TaskGroup (Code-Ready Reference)

> For Claude Code: Use this when implementing concurrent agent dispatch in MINDY.

## TL;DR: Use `asyncio.gather(return_exceptions=True)` for MINDY's fan-out

`TaskGroup` cancels ALL tasks if ANY fails. `gather` with `return_exceptions=True` lets you collect partial results.

**However**: OrgMind uses Agent Framework's `ConcurrentBuilder` which handles this natively. Use raw asyncio only for custom concurrent logic outside the framework.

## asyncio.gather — Partial Success

```python
import asyncio

async def fan_out_with_timeout(query: str, timeout: float = 30.0) -> list:
    tasks = [
        asyncio.wait_for(call_findr(query), timeout=timeout),
        asyncio.wait_for(call_taskr(query), timeout=timeout),
        asyncio.wait_for(call_campa(query), timeout=timeout),
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    successes = []
    for result in results:
        if isinstance(result, asyncio.TimeoutError):
            logger.warning("Agent timed out")
        elif isinstance(result, BaseException):
            logger.error(f"Agent failed: {result}")
        else:
            successes.append(result)
    return successes
```

## asyncio.TaskGroup — All-or-Nothing (DON'T USE for MINDY)

```python
# TaskGroup cancels ALL tasks if ANY fails — not what we want
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(call_findr("query"))
    t2 = tg.create_task(call_taskr("query"))  # if this fails, t1 and t3 get cancelled
    t3 = tg.create_task(call_campa("query"))
```

## OrgMind Pattern — Safe Dispatch

```python
from dataclasses import dataclass

@dataclass
class AgentResult:
    agent_name: str
    success: bool
    data: str | None = None
    error: str | None = None

async def mindy_dispatch(query: str, agents: dict[str, callable]) -> list[AgentResult]:
    async def safe_call(name: str, fn: callable) -> AgentResult:
        try:
            result = await asyncio.wait_for(fn(query), timeout=30.0)
            return AgentResult(agent_name=name, success=True, data=result)
        except asyncio.TimeoutError:
            return AgentResult(agent_name=name, success=False, error="timeout")
        except Exception as e:
            return AgentResult(agent_name=name, success=False, error=str(e))

    results = await asyncio.gather(*[safe_call(n, f) for n, f in agents.items()])
    return list(results)
```

## IMPORTANT NOTES
1. Prefer `ConcurrentBuilder` from Agent Framework over raw asyncio
2. Always use `return_exceptions=True` for partial-success scenarios
3. Wrap each task in `asyncio.wait_for()` for per-task timeouts
