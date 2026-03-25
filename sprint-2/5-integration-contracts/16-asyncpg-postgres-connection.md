# asyncpg — PostgreSQL Connection (Code-Ready Reference)

> For Claude Code: Async PostgreSQL access for agent config, prompts, and audit logs.

## Installation

```bash
pip install asyncpg
```

## Connection Pool

```python
import asyncpg

async def create_pool(dsn: str) -> asyncpg.Pool:
    return await asyncpg.create_pool(
        dsn=dsn,
        min_size=2,
        max_size=10,
        command_timeout=30,
    )

# Usage
pool = await create_pool("postgresql://user:pass@localhost:5432/orgmind")
```

## CRUD Operations

```python
# Fetch one
row = await pool.fetchrow("SELECT * FROM agents WHERE key = $1", "MINDY")
print(dict(row))

# Fetch many
rows = await pool.fetch("SELECT * FROM agents WHERE is_active = $1", True)
agents = [dict(r) for r in rows]

# Insert
await pool.execute(
    "INSERT INTO agents (key, name, description) VALUES ($1, $2, $3)",
    "MINDY", "Orchestrator", "Intent routing + response synthesis",
)

# Update
await pool.execute(
    "UPDATE prompts SET content = $1, updated_at = now() WHERE agent_id = $2 AND prompt_type = $3",
    new_prompt, agent_id, "system",
)

# Transaction
async with pool.acquire() as conn:
    async with conn.transaction():
        await conn.execute("UPDATE ...", ...)
        await conn.execute("INSERT ...", ...)
```

## OrgMind Queries

```python
async def get_agent_config(pool: asyncpg.Pool, agent_key: str) -> dict | None:
    row = await pool.fetchrow("SELECT * FROM agents WHERE key = $1 AND is_active = true", agent_key)
    return dict(row) if row else None

async def get_prompt(pool: asyncpg.Pool, agent_key: str, prompt_type: str, env: str = "prod") -> str | None:
    row = await pool.fetchrow(
        """SELECT content FROM prompts p
        JOIN agents a ON a.id = p.agent_id
        WHERE a.key = $1 AND p.prompt_type = $2 AND p.environment = $3
        ORDER BY p.version DESC LIMIT 1""",
        agent_key, prompt_type, env,
    )
    return row["content"] if row else None

async def get_config(pool: asyncpg.Pool, key: str) -> dict | None:
    row = await pool.fetchrow("SELECT value FROM config_kv WHERE key = $1", key)
    return dict(row["value"]) if row else None
```

## Lifecycle

```python
# In app startup
pool = await create_pool(settings.postgres_url)

# In app shutdown
await pool.close()
```

## IMPORTANT NOTES
1. Always use connection pools — never single connections
2. Use `$1, $2` parameterized queries — never f-strings (SQL injection!)
3. asyncpg is ~3x faster than psycopg for async workloads
4. Schema is in `POC/orgmind_poc_schema_v1.sql`
