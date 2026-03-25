# Topic: Conflict Resolution — Audit Logging

**Time:** 15 min
**Goal:** Understand how conflict decisions are logged for traceability

---

## What to Search
- "audit log pattern PostgreSQL immutable"
- "event sourcing audit trail Python"

## POC Tables
```sql
CREATE TABLE conflict_audit_log (
    id SERIAL PRIMARY KEY,
    run_hash TEXT UNIQUE NOT NULL,   -- idempotent insertion
    container_tag TEXT NOT NULL,
    conflict_group TEXT NOT NULL,
    winner_id TEXT,
    strategy TEXT,                    -- "hierarchy", "manual", "merge"
    needs_human BOOLEAN DEFAULT FALSE,
    candidate_count INT,
    resolution_reason TEXT,
    resolved_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE conflict_audit_snapshot (
    id SERIAL PRIMARY KEY,
    audit_log_id INT REFERENCES conflict_audit_log(id),
    candidate_id TEXT,
    candidate_hash TEXT,
    rank INT,
    score_details JSONB
);
```

## Code Pattern
```python
import hashlib

def compute_run_hash(conflict_group: str, candidate_ids: list[str]) -> str:
    """Deterministic hash so same conflict resolution = same run_hash = no duplicate logs."""
    raw = f"{conflict_group}|{'|'.join(sorted(candidate_ids))}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

async def log_resolution(conn, resolution: ConflictResolution):
    run_hash = compute_run_hash(resolution.conflict_group, resolution.candidate_ids)

    # Idempotent insert (run_hash is UNIQUE)
    await conn.execute("""
        INSERT INTO conflict_audit_log (run_hash, container_tag, conflict_group, winner_id, strategy, needs_human, candidate_count, resolution_reason)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (run_hash) DO NOTHING
    """, run_hash, resolution.container_tag, resolution.conflict_group,
         resolution.winner_id, resolution.strategy, resolution.needs_human,
         resolution.candidate_count, resolution.resolution_reason)
```

## What to Understand
- [ ] `run_hash` makes audit insertion idempotent (same conflict = no duplicate)
- [ ] Snapshot table stores per-candidate score details
- [ ] Audit log is append-only / immutable
- [ ] `ON CONFLICT DO NOTHING` = safe to call multiple times
