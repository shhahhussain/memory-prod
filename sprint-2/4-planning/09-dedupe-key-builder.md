# Topic: Dedupe Key Builder — Deterministic Custom IDs

**Time:** 15 min
**Goal:** Port the n8n dedupe key generator to Python

---

## What to Search
- "deterministic ID generation Python hashlib"
- "content-based deduplication key Python"

## What It Does
When a memory write doesn't have a `customId`, generate one deterministically so the same content always gets the same ID (prevents duplicates).

## Code Pattern
```python
import hashlib
from datetime import date

def build_dedupe_key(
    content: str,
    memory_type: str,
    container_tag: str,
    conflict_group: str | None = None,
) -> str:
    """Generate deterministic customId from content + metadata."""
    normalized = content.strip().lower()
    raw = f"{container_tag}|{memory_type}|{normalized}"
    hash_part = hashlib.sha256(raw.encode()).hexdigest()[:12]
    prefix = memory_type[:4]  # "fact", "rule", "agen", "vect"
    return f"{prefix}_{hash_part}"

def ensure_conflict_group(
    custom_id: str,
    conflict_group: str | None,
) -> str:
    """If no explicit conflict_group, default to customId."""
    return conflict_group if conflict_group else custom_id
```

## Usage
```python
payload = WritePayload(content="Acme Q1 budget is $50K", metadata=metadata)

if not payload.custom_id:
    payload.custom_id = build_dedupe_key(
        payload.content, payload.metadata.memory_type, payload.container_tag
    )

payload.metadata.conflict_group = ensure_conflict_group(
    payload.custom_id, payload.metadata.conflict_group
)
```

## What to Understand
- [ ] Same content + type + container = same customId (deterministic)
- [ ] `conflict_group` defaults to `customId` when not set
- [ ] This replaces `SVC - Util - Dedupe Key Builder` n8n workflow
- [ ] SHA256 truncated to 12 chars is collision-resistant enough for this use case
