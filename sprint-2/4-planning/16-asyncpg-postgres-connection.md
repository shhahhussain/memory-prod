# Topic: asyncpg — Async PostgreSQL Connection

**Time:** 20 min
**Goal:** Replace n8n Postgres nodes with async Python database access

---

## What to Search
- "asyncpg Python PostgreSQL async tutorial"
- "asyncpg connection pool FastAPI"
- "asyncpg vs SQLAlchemy async"

## Install
```bash
pip install asyncpg
```

## Connection Pool
```python
import asyncpg

class Database:
    def __init__(self):
        self.pool: asyncpg.Pool | None = None

    async def connect(self, dsn: str):
        self.pool = await asyncpg.create_pool(dsn=dsn, min_size=2, max_size=10)

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def fetch(self, query: str, *args) -> list[asyncpg.Record]:
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> asyncpg.Record | None:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def execute(self, query: str, *args) -> str:
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

db = Database()
```

## Usage Examples (porting POC queries)
```python
# SVC - PG - Config Get
config = await db.fetch("SELECT * FROM agents WHERE status = 'active'")

# SVC - PG - Prompt Get
prompt = await db.fetchrow(
    "SELECT prompt_text FROM prompts WHERE agent_id = $1", agent_id
)

# Conflict override with advisory lock
async with db.pool.acquire() as conn:
    async with conn.transaction():
        lock_key = hash(f"{container}|{group}") & 0x7FFFFFFF
        await conn.execute("SELECT pg_advisory_xact_lock($1)", lock_key)
        await conn.execute("INSERT INTO conflict_override ...", ...)
```

## FastAPI Lifecycle
```python
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
async def startup():
    await db.connect(settings.postgres_url)

@app.on_event("shutdown")
async def shutdown():
    await db.close()
```

## What to Understand
- [ ] `asyncpg` is the fastest async Postgres driver for Python
- [ ] Connection pool reuses connections (don't create new ones per query)
- [ ] `$1, $2` parameterized queries prevent SQL injection
- [ ] `conn.transaction()` for multi-statement atomic operations
- [ ] Advisory locks work within transactions
