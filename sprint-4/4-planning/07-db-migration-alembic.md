# Topic: Database Migrations with Alembic

**Time:** 20 min
**Goal:** Manage PostgreSQL schema changes properly

---

## What to Search
- "alembic PostgreSQL migration Python"
- "alembic async asyncpg"
- "alembic autogenerate SQLAlchemy"

## Install
```bash
pip install alembic sqlalchemy[asyncio] asyncpg
```

## What to Understand
- [ ] Alembic tracks which migrations have run
- [ ] Each migration is a Python file with upgrade() and downgrade()
- [ ] You can write raw SQL in migrations (don't need SQLAlchemy models)
- [ ] POC has 4 migration files to port — use as starting point
