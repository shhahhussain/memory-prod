# Supermemory Write with Metadata (Code-Ready Reference)

> For Claude Code: Full write pipeline matching POC's SVC - SM - Write.

## Write Pipeline

```
Content → Guardrails → Dedupe Key Builder → Supermemory Write
```

## Complete Write Function

```python
from supermemory import AsyncSupermemory
from orgmind.tools.guardrails import apply_guardrails, WritePayload, MemoryMetadata
from orgmind.tools.dedupe import enrich_write_payload

async def write_memory(
    client: AsyncSupermemory,
    content: str,
    metadata: dict,
    container_tag: str = "orgmind",
    actor: str = "system",
) -> dict:
    # 1. Build payload
    payload = WritePayload(
        content=content,
        container_tag=container_tag,
        metadata=MemoryMetadata(**{**metadata, "created_by": actor}),
    )

    # 2. Apply guardrails
    guardrail_result = apply_guardrails(payload)
    if not guardrail_result.write_allowed:
        return {"ok": False, "reason": "guardrails_blocked", "flags": guardrail_result.guardrail_flags}

    # 3. Enrich with dedupe key
    enriched = enrich_write_payload(guardrail_result.payload.model_dump())

    # 4. Write to Supermemory
    result = await client.documents.add(
        content=enriched["content"],
        container_tags=[enriched["container_tag"]],
        custom_id=enriched.get("custom_id", ""),
        metadata=enriched["metadata"],
    )

    return {
        "ok": True,
        "document_id": result.id,
        "status": result.status,
        "custom_id": enriched.get("custom_id"),
        "effective_status": guardrail_result.effective_status,
        "guardrail_flags": guardrail_result.guardrail_flags,
    }
```

## IMPORTANT NOTES
1. Always run guardrails → dedupe → write (same order as POC)
2. `customId` enables Supermemory dedup — same ID = update, not duplicate
3. Guardrail flags are informational — they don't block writes (just change status to draft)
