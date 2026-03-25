# Database Migrations — Alembic (Code-Ready Reference)

> For Claude Code: Schema migrations for PostgreSQL.

## Installation

```bash
pip install alembic asyncpg
```

## Setup

```bash
alembic init migrations
```

Edit `migrations/env.py`:
```python
from orgmind.settings import get_settings
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.postgres_url)
```

## Create Migration

```bash
alembic revision --autogenerate -m "add conflict audit log"
alembic upgrade head
alembic downgrade -1
```

## Without SQLAlchemy (Raw asyncpg)

If not using SQLAlchemy ORM, keep migrations as plain SQL files:

```
migrations/
├── 001_initial_schema.sql
├── 002_add_conflict_audit_log.sql
└── 003_add_indexes.sql
```

```python
import asyncpg
from pathlib import Path

async def run_migrations(pool: asyncpg.Pool, migrations_dir: str = "migrations"):
    # Create tracking table
    await pool.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INT PRIMARY KEY,
            applied_at TIMESTAMPTZ DEFAULT now()
        )
    """)

    applied = {r["version"] for r in await pool.fetch("SELECT version FROM schema_migrations")}
    migration_files = sorted(Path(migrations_dir).glob("*.sql"))

    for f in migration_files:
        version = int(f.stem.split("_")[0])
        if version not in applied:
            sql = f.read_text()
            async with pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute(sql)
                    await conn.execute("INSERT INTO schema_migrations (version) VALUES ($1)", version)
            print(f"Applied migration {f.name}")
```

## IMPORTANT NOTES
1. POC schema is in `POC/orgmind_poc_schema_v1.sql` — use as base
2. For simple projects, plain SQL migrations > Alembic ORM overhead
3. Always run migrations in transactions
4. Track applied migrations in a `schema_migrations` table
