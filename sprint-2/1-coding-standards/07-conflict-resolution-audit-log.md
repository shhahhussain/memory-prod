# Conflict Resolution — Audit Log (Code-Ready Reference)

> For Claude Code: Track all conflict resolution decisions for accountability.

## Schema (PostgreSQL)

```sql
CREATE TABLE IF NOT EXISTS conflict_audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conflict_group  TEXT NOT NULL,
    strategy        TEXT NOT NULL,  -- 'hierarchy' | 'manual' | 'merge'
    winner_id       TEXT,
    loser_ids       TEXT[] NOT NULL DEFAULT '{}',
    reason          TEXT NOT NULL,  -- 'recency' | 'confidence' | 'source_authority' | 'manual_approve' | 'manual_reject'
    actor           TEXT,           -- who triggered (user or 'system')
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_conflict_audit_group ON conflict_audit_log(conflict_group);
CREATE INDEX idx_conflict_audit_created ON conflict_audit_log(created_at);
```

## Python Implementation

```python
from datetime import datetime
from pydantic import BaseModel
import asyncpg

class AuditEntry(BaseModel):
    conflict_group: str
    strategy: str
    winner_id: str | None
    loser_ids: list[str]
    reason: str
    actor: str
    metadata: dict = {}

async def log_resolution(pool: asyncpg.Pool, entry: AuditEntry) -> str:
    row = await pool.fetchrow(
        """
        INSERT INTO conflict_audit_log (conflict_group, strategy, winner_id, loser_ids, reason, actor, metadata)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id
        """,
        entry.conflict_group, entry.strategy, entry.winner_id,
        entry.loser_ids, entry.reason, entry.actor,
        entry.metadata,
    )
    return str(row["id"])

async def get_audit_history(pool: asyncpg.Pool, conflict_group: str, limit: int = 10) -> list[dict]:
    rows = await pool.fetch(
        """SELECT * FROM conflict_audit_log WHERE conflict_group = $1 ORDER BY created_at DESC LIMIT $2""",
        conflict_group, limit,
    )
    return [dict(r) for r in rows]
```

## IMPORTANT NOTES
1. Log EVERY resolution — both automatic (hierarchy) and manual (approve/reject)
2. `actor` = "system" for automatic, user ID for manual
3. Use this for compliance auditing and debugging
