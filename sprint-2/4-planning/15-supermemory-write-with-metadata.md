# Topic: Supermemory — Write with Full Metadata

**Time:** 15 min
**Goal:** Port POC's SVC - SM - Write to Python SDK

---

## What to Search
- "supermemory Python SDK add document metadata"
- "supermemory API v3 documents create"

## Full Write Pipeline (replaces 4 n8n workflows)
```python
from supermemory import AsyncSupermemory

client = AsyncSupermemory(api_key=settings.supermemory_api_key)

async def write_memory(payload: WritePayload) -> dict:
    """
    Replaces:
    - SVC - SM - Write (main)
    - SVC - Util - Guardrails (now in Pydantic model)
    - SVC - Util - Dedupe Key Builder (now in dedupe.py)
    """
    # 1. Validation + Guardrails happen in Pydantic model (already done)

    # 2. Dedupe key
    if not payload.custom_id:
        payload.custom_id = build_dedupe_key(
            payload.content, payload.metadata.memory_type, payload.container_tag
        )
    payload.metadata.conflict_group = ensure_conflict_group(
        payload.custom_id, payload.metadata.conflict_group
    )

    # 3. Write to Supermemory
    result = await client.add(
        content=payload.content,
        container_tags=[payload.container_tag],
        metadata=payload.metadata.model_dump(exclude_none=True),
        custom_id=payload.custom_id,
    )

    return {
        "ok": True,
        "document_id": result.id if hasattr(result, 'id') else None,
        "custom_id": payload.custom_id,
        "status": payload.metadata.status,
        "guardrail_flags": [payload.metadata.guardrail_reason] if payload.metadata.guardrail_reason else [],
    }
```

## Metadata Fields (full set from POC)
```python
metadata = {
    "memory_type": "fact",          # fact|rule|agent|vector
    "source_type": "chat",          # slack|chat|email|doc|api|human|seed|teams
    "created_by": "Shah",
    "source_id": "chat-session-123",
    "confidence": 0.95,
    "as_of": "2026-03-21",
    "project": "orgmind-poc",
    "schema_version": "v2",
    "entity_type": "fact",
    "client": "acme",
    "department": "marketing",
    "source_authority": 2,
    "status": "active",             # active|draft|deprecated
    "conflict_group": "acme_budget_q1",
    "is_current": True,
}
```

## What to Understand
- [ ] `client.add()` is the write method
- [ ] `custom_id` enables overwrites (same ID = update, not duplicate)
- [ ] `container_tags` scopes the memory
- [ ] Metadata is a flat dict (Supermemory stores as JSON)
- [ ] This single function replaces 4 n8n workflow calls
