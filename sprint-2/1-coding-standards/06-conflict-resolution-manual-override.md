# Conflict Resolution — Manual Override (Code-Ready Reference)

> For Claude Code: Port the POC's approve/reject flow for human-in-the-loop conflict resolution.

## POC Flow (from n8n)

1. User sends `approve:<customId>` or `reject:<customId>`
2. System looks up document by exact `customId` match
3. On approve: set `status=active`, `source_authority=1`, `is_current=true`
4. On reject: set `status=deprecated`, `is_current=false`

## Implementation

```python
from supermemory import AsyncSupermemory

async def handle_approve_reject(
    client: AsyncSupermemory,
    action: str,  # "approve" or "reject"
    custom_id: str,
    actor: str,
) -> dict:
    # Search for the exact document
    results = await client.search.execute(
        q=custom_id,
        container_tags=["orgmind"],
        limit=20,
    )

    # Find exact customId match
    target = None
    for r in results.results:
        doc_custom_id = (
            getattr(r, "custom_id", None)
            or r.metadata.get("customId")
            or r.metadata.get("custom_id")
        )
        if doc_custom_id == custom_id and r.metadata.get("status") == "draft":
            target = r
            break

    if not target:
        return {"ok": False, "error": f"No draft found with customId: {custom_id}"}

    # Build updated metadata
    from datetime import date
    new_metadata = {**target.metadata}
    new_metadata["source_id"] = "human-review"
    new_metadata["as_of"] = date.today().isoformat()
    new_metadata["source_authority"] = 1

    if action == "approve":
        new_metadata["status"] = "active"
        new_metadata["is_current"] = True
    else:
        new_metadata["status"] = "deprecated"
        new_metadata["is_current"] = False

    # Write back (Supermemory uses customId for dedup/update)
    result = await client.documents.add(
        content=target.chunk or target.memory or "",
        container_tags=["orgmind"],
        custom_id=custom_id,
        metadata=new_metadata,
    )

    return {
        "ok": True,
        "action": action,
        "custom_id": custom_id,
        "new_status": new_metadata["status"],
        "reviewed_by": actor,
    }
```

## Teams Integration

In Teams, this becomes an Adaptive Card with Approve/Reject buttons (see Sprint 3).

## IMPORTANT NOTES
1. Exact `customId` match required — not semantic search
2. Only `status=draft` items can be approved/rejected
3. Approved: `status=active`, `source_authority=1`, `is_current=true`
4. Rejected: `status=deprecated`, `is_current=false`
5. Write back uses same `customId` for Supermemory's dedup/update
