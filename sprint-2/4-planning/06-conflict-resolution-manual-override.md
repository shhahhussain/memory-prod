# Topic: Conflict Resolution — Manual Override System

**Time:** 20-30 min
**Goal:** Understand the human override system for conflict winners

---

## What to Search
- "advisory locks asyncpg Python"
- "PostgreSQL advisory lock race condition"
- "manual override pattern database"

## What It Does
Humans can override the algorithmic winner. If they say "No, the $35K budget is correct, not $50K", that override persists.

## POC Operations
- `set` — set a manual winner for a conflict group
- `get_many` — get all active overrides
- `clear` — remove an override (go back to algorithmic)
- `list` — list all overrides

## Database Table
```sql
CREATE TABLE conflict_override (
    id SERIAL PRIMARY KEY,
    container_tag TEXT NOT NULL,
    conflict_group TEXT NOT NULL,
    winner TEXT NOT NULL,           -- format: "type:id" (e.g., "fact:abc123")
    set_by TEXT NOT NULL,
    set_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    cleared_at TIMESTAMPTZ,
    clear_reason TEXT,
    -- Exclusion constraint: only ONE active override per container+group
    EXCLUDE USING gist (
        container_tag WITH =,
        conflict_group WITH =
    ) WHERE (cleared_at IS NULL)
);
```

## Advisory Locks (Race Condition Prevention)
```python
async def set_override(conn, container_tag: str, conflict_group: str, winner: str, set_by: str):
    # Advisory lock prevents two users setting override simultaneously
    lock_key = hash(f"{container_tag}|{conflict_group}") & 0x7FFFFFFF
    await conn.execute("SELECT pg_advisory_xact_lock($1)", lock_key)

    # Clear any existing override
    await conn.execute("""
        UPDATE conflict_override
        SET cleared_at = NOW(), clear_reason = 'replaced'
        WHERE container_tag = $1 AND conflict_group = $2 AND cleared_at IS NULL
    """, container_tag, conflict_group)

    # Set new override
    await conn.execute("""
        INSERT INTO conflict_override (container_tag, conflict_group, winner, set_by)
        VALUES ($1, $2, $3, $4)
    """, container_tag, conflict_group, winner, set_by)
```

## Winner Status Sync
After setting/clearing an override, sync back to Supermemory:
- Winner → `status = 'active'`
- Non-winners → `status = 'deprecated'`

## What to Understand
- [ ] Advisory locks are PostgreSQL's way to prevent race conditions without table locks
- [ ] `pg_advisory_xact_lock` releases automatically when transaction ends
- [ ] Exclusion constraint ensures only ONE active override per group
- [ ] Override expiry is optional (can set `expires_at`)
- [ ] After override, Supermemory statuses are synced
