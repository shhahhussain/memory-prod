# Sprint 5 — Edge Cases & Known Pitfalls

> **Scope:** pytest-asyncio, regression tests, GitHub Actions CI/CD, Azure App Service deploy, health checks

---

## Research-Verified Findings

- **Azure SIGTERM grace period:** Confirmed ~30 seconds by default. Configurable via the `WEBSITES_SHUTDOWN_TIME` app setting (value in seconds). (EC-5.2)
- **Azure container start time limit:** `WEBSITES_CONTAINER_START_TIME_LIMIT` defaults to 230 seconds, max 1800 seconds. Set this if your cold start initialization is slow. (EC-5.1)

---

## 1. Deployment & Azure Edge Cases

### EC-5.1 — Cold start timeout on first request

**Scenario:** Azure App Service cold-starts your app. First Teams message arrives before `asyncpg.create_pool()` completes (2–5s). Request handler calls `pool.acquire()` on `None` → `AttributeError`. Or pool is initializing → `acquire()` hangs for 15s → Teams retries → duplicate processing.

```python
class AppState:
    _pool: asyncpg.Pool | None = None
    _ready: asyncio.Event = asyncio.Event()

    async def startup(self):
        self._pool = await asyncpg.create_pool(dsn, min_size=2, max_size=20)
        await self._warmup_pool()
        self._ready.set()

    async def get_pool(self) -> asyncpg.Pool:
        await asyncio.wait_for(self._ready.wait(), timeout=30)
        return self._pool

# Azure App Setting to increase cold start tolerance (default 230s, max 1800s):
#   WEBSITES_CONTAINER_START_TIME_LIMIT=600
#
# This gives the container 600 seconds to start and respond to health checks.
# Set this if pool initialization + warm-up takes >230 seconds.
```

### EC-5.2 — SIGTERM with only 30s grace period

**Scenario:** Azure sends SIGTERM then SIGKILL after 30 seconds. In-flight MINDY orchestration takes 25s. At second 30, SIGKILL fires mid-write to Supermemory. Write half-persisted. New instance processes same message (retry) with corrupted context.

```python
import signal, asyncio

shutdown_event = asyncio.Event()
in_flight_tasks: set[asyncio.Task] = set()

async def tracked_task(coro, task_id: str):
    task = asyncio.current_task()
    in_flight_tasks.add(task)
    try:
        return await coro
    finally:
        in_flight_tasks.discard(task)

async def graceful_shutdown():
    shutdown_event.set()
    if in_flight_tasks:
        try:
            await asyncio.wait_for(
                asyncio.gather(*in_flight_tasks, return_exceptions=True),
                timeout=25  # 25s for in-flight, 5s for cleanup
            )
        except asyncio.TimeoutError:
            logger.warning("forced_shutdown_tasks_incomplete", count=len(in_flight_tasks))
    await db_pool.close()

loop = asyncio.get_event_loop()
loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(graceful_shutdown()))

# WARNING: Community reports that Linux App Service may SIGKILL immediately
# without sending SIGTERM in some edge cases. Defensively, add middleware that
# returns 503 as soon as SIGTERM is received, so the load balancer stops
# routing new requests while in-flight tasks drain:

from aiohttp import web

@web.middleware
async def shutdown_middleware(request, handler):
    if shutdown_event.is_set():
        return web.json_response(
            {"error": "Server shutting down"}, status=503,
            headers={"Retry-After": "5"}
        )
    return await handler(request)

# Configure SIGTERM grace period via Azure App Setting:
#   WEBSITES_SHUTDOWN_TIME=30  (default is ~30s, can increase if needed)
```

### EC-5.3 — Health check returning 200 before pools initialized

**Scenario:** `/health` returns 200 unconditionally. Azure routes traffic before pools are ready. First request → pool not initialized → crash.

```python
@app.get("/health/live")
async def liveness():
    return {"status": "alive"}  # Always 200

@app.get("/health/ready")
async def readiness():
    checks = {}
    try:
        await asyncio.wait_for(db_pool.fetchval("SELECT 1"), timeout=2)
        checks["postgres"] = "ok"
    except Exception as e:
        checks["postgres"] = str(e)

    all_ok = all(v == "ok" for v in checks.values())
    return JSONResponse({"checks": checks}, status_code=200 if all_ok else 503)

# Azure: startup probe on /health/ready with failureThreshold=3
```

### EC-5.4 — Multi-instance user state inconsistency (no sticky sessions)

**Scenario:** User sends message → Instance A. MINDY stores state in local `dict`. Next message → Instance B (round-robin). Instance B has no state → context lost.

```python
# WRONG — instance-local state
_user_sessions: dict[str, ConversationState] = {}

# CORRECT — Use M365 SDK's built-in state management with external storage
# MemoryStorage() for dev, BlobStorage/CosmosDB for production
# The SDK handles serialization and multi-instance access automatically
from microsoft_agents.hosting.core import AgentApplication, TurnState, MemoryStorage

# Dev:
AGENT_APP = AgentApplication[TurnState](storage=MemoryStorage(), adapter=CloudAdapter())

# Prod: Use Azure Blob Storage or CosmosDB (Microsoft's recommended pattern)
# pip install microsoft-agents-storage-blob
# from microsoft_agents.storage.blob import BlobStorage
# AGENT_APP = AgentApplication[TurnState](storage=BlobStorage(...), adapter=CloudAdapter())
```

---

## 2. Testing Edge Cases

### EC-5.5 — pytest-asyncio event loop lifetime mismatch

**Scenario:** Session-scoped fixture creates asyncpg pool. Function-scoped test uses a different event loop. `pool.acquire()` raises `RuntimeError: Task got Future attached to a different loop`.

```python
# In pyproject.toml:
[tool.pytest.ini_options]
asyncio_mode = "auto"

# Use loop_scope to match fixture scope with event loop
@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def pg_pool():
    pool = await asyncpg.create_pool("postgresql://localhost/test_db")
    yield pool
    await pool.close()
```

### EC-5.6 — Tests passing locally but failing in CI (Docker networking)

**Scenario:** Tests expect `localhost:5432` for PostgreSQL. CI uses Docker service containers. The hostname is `postgres` not `localhost`. Tests fail with `ConnectionRefusedError`.

```python
# conftest.py — environment-aware fixtures
@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def pg_pool():
    dsn = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/test_orgmind"
    )
    pool = await asyncpg.create_pool(dsn, min_size=2, max_size=5)
    yield pool
    await pool.close()

# In GitHub Actions workflow:
# env:
#   TEST_DATABASE_URL: postgresql://postgres:postgres@postgres:5432/test_orgmind
```

### EC-5.7 — Flaky tests from shared database state

**Scenario:** Test A creates a task in NocoDB. Test B queries all tasks — finds test A's leftovers. Test B asserts `len(tasks) == 1` but gets 2.

```python
@pytest_asyncio.fixture(autouse=True)
async def clean_db(pg_pool):
    """Truncate all tables before each test"""
    async with pg_pool.acquire() as conn:
        # Truncate in dependency order
        await conn.execute("TRUNCATE agent_runs, conflict_queue, tasks CASCADE")
    yield
    # Optionally clean up after too
```

### EC-5.8 — Testing ExceptionGroup from TaskGroup

**Scenario:** `pytest.raises(ValueError)` doesn't catch `ExceptionGroup(ValueError)`. TaskGroup wraps ALL exceptions in ExceptionGroup.

```python
async def test_taskgroup_cancels_siblings():
    cancel_observed = False

    async def slow_task():
        nonlocal cancel_observed
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            cancel_observed = True
            raise

    async def failing_task():
        raise ValueError("Agent failed")

    with pytest.raises(ExceptionGroup) as exc_info:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(slow_task())
            tg.create_task(failing_task())

    assert exc_info.group_contains(ValueError)
    assert cancel_observed
```

### EC-5.9 — Mock LLM returning inconsistent response shapes

**Scenario:** `FakeLLMGateway` returns raw strings. Real Claude returns `{"content": [{"type": "text", "text": "..."}]}`. Agent code works with mock but crashes in production.

```python
class FakeLLMGateway:
    """Mock that returns the same shape as the real normalized LLMResponse"""
    def __init__(self, responses: dict[str, str]):
        self._responses = responses

    async def complete(self, prompt: str, max_tokens: int = 1024) -> LLMResponse:
        for key, resp in self._responses.items():
            if key in prompt:
                return LLMResponse(text=resp, stop_reason="end_turn", model="fake")
        return LLMResponse(text="{}", stop_reason="end_turn", model="fake")

# Always return the NORMALIZED type, not raw strings
```

---

## 3. CI/CD Edge Cases

### EC-5.10 — GitHub Actions secret not available in PR from fork

**Scenario:** External contributor opens a PR. GitHub Actions doesn't expose secrets to fork PRs (security). Your integration tests fail because `ANTHROPIC_API_KEY` is empty.

```python
# In CI workflow:
# - Run unit tests on all PRs (no secrets needed)
# - Run integration tests only on pushes to main (secrets available)

# .github/workflows/ci.yml
jobs:
  unit-tests:
    if: always()  # Run on all PRs
    steps:
      - run: pytest tests/unit/

  integration-tests:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - run: pytest tests/integration/
```

### EC-5.11 — Azure App Service deploy with zero-downtime failure

**Scenario:** Rolling deploy starts new instance. New instance fails health check (bad config). Azure stops routing to new instance but already stopped old instance. Brief outage window where no instance serves traffic.

```python
# Azure App Service deployment slot strategy:
# 1. Deploy to staging slot
# 2. Run health check on staging slot
# 3. Swap staging → production (atomic, zero-downtime)
# 4. If swap fails, staging stays as-is, production unchanged

# In Azure CLI:
# az webapp deployment slot create --name orgmind --slot staging
# az webapp deploy --slot staging ...
# az webapp deployment slot swap --name orgmind --slot staging --target-slot production
```

---

## Quick Reference

| # | Failure | Trigger | Fix |
|---|---------|---------|-----|
| 5.1 | AttributeError on None pool | Cold start | `asyncio.Event` readiness gate + `WEBSITES_CONTAINER_START_TIME_LIMIT=600` |
| 5.2 | Half-written memory | SIGKILL at 30s | Track in-flight tasks, 25s drain budget, 503 middleware after SIGTERM |
| 5.3 | Crash on first request | Health 200 before ready | Separate `/live` vs `/ready` endpoints |
| 5.4 | Context lost | Multi-instance round-robin | BlobStorage/CosmosDB via M365 SDK, not local dict |
| 5.5 | Wrong event loop | Fixture scope mismatch | `loop_scope="session"` |
| 5.6 | CI connection refused | Docker networking | Env-aware `TEST_DATABASE_URL` |
| 5.7 | Flaky test assertions | Shared DB state | `TRUNCATE CASCADE` in autouse fixture |
| 5.8 | `pytest.raises` misses error | ExceptionGroup wrapping | `pytest.raises(ExceptionGroup)` |
| 5.9 | Mock/prod shape mismatch | Raw string mock | Return normalized `LLMResponse` type |
| 5.10 | CI secrets missing | Fork PR | Unit tests only on PRs, integration on main |
| 5.11 | Brief outage | Failed rolling deploy | Deployment slot swap strategy |
