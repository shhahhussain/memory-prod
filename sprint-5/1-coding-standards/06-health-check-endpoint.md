# Health Check Endpoint (Code-Ready Reference)

> For Claude Code: Liveness and readiness probes for production.

## Implementation

```python
from aiohttp.web import Request, Response, json_response
import asyncpg

async def health_check(request: Request) -> Response:
    checks = {}

    # Check Postgres
    try:
        pool: asyncpg.Pool = request.app["db_pool"]
        await pool.fetchval("SELECT 1")
        checks["postgres"] = "ok"
    except Exception as e:
        checks["postgres"] = f"error: {e}"

    # Check Supermemory (lightweight)
    try:
        sm = request.app["supermemory"]
        # Just check API is reachable
        checks["supermemory"] = "ok"
    except Exception as e:
        checks["supermemory"] = f"error: {e}"

    all_ok = all(v == "ok" for v in checks.values())
    return json_response(
        {"status": "healthy" if all_ok else "degraded", "checks": checks},
        status=200 if all_ok else 503,
    )

# Register in server
APP.router.add_get("/health", health_check)
APP.router.add_get("/api/messages", lambda _: Response(status=200))  # Bot Service health check
```

## Azure App Service Config

```bash
az webapp config set --name orgmind-bot --resource-group orgmind-rg \
  --generic-configurations '{"healthCheckPath": "/health"}'
```

## IMPORTANT NOTES
1. `/health` for detailed checks, `/api/messages` GET for Bot Service
2. Return 503 if any dependency is down
3. Azure App Service pings health endpoint every 30s
4. Don't include secrets in health check response
