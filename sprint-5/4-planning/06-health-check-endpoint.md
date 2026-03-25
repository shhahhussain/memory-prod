# Topic: Health Check Endpoint

**Time:** 10 min
**Goal:** Create /health endpoint for monitoring

---

## What to Search
- "FastAPI health check endpoint"
- "Azure App Service health check configuration"

## Code
```python
@app.get("/health")
async def health():
    checks = {}

    # Supermemory
    try:
        await supermemory_client.search.memories(q="ping", container_tags=["orgmind-poc"], limit=1)
        checks["supermemory"] = {"ok": True}
    except Exception as e:
        checks["supermemory"] = {"ok": False, "error": str(e)}

    # PostgreSQL
    try:
        await db.fetchrow("SELECT 1")
        checks["postgres"] = {"ok": True}
    except Exception as e:
        checks["postgres"] = {"ok": False, "error": str(e)}

    all_ok = all(c["ok"] for c in checks.values())
    return {
        "status": "healthy" if all_ok else "degraded",
        "checks": checks,
        "version": "1.0.0",
    }
```

## Azure Config
```bash
az webapp config set --name orgmind-bot --resource-group orgmind-rg \
  --generic-configurations '{"healthCheckPath": "/health"}'
```

## What to Understand
- [ ] Check all external dependencies (Supermemory, PostgreSQL)
- [ ] Return "degraded" not "unhealthy" if one service is down (bot can still partially work)
- [ ] Azure health check restarts the app if it fails repeatedly
- [ ] This replaces POC's `UTIL - Health Check` workflow
