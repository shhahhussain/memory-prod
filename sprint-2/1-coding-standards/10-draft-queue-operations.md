# Draft Queue Operations (Code-Ready Reference)

> For Claude Code: Port the POC's draft review workflow.

## What is the Draft Queue?

Memories that fail guardrails (missing source_id/as_of) get `status=draft`. Users can review, approve, or reject them.

## Implementation

```python
from supermemory import AsyncSupermemory

async def list_drafts(client: AsyncSupermemory, container_tag: str = "orgmind", limit: int = 20) -> list[dict]:
    results = await client.search.execute(
        q="draft items",
        container_tags=[container_tag],
        limit=limit,
        filters={"AND": [{"key": "status", "value": "draft"}]},
    )
    return [{"id": r.id, "content": r.memory or r.chunk, "metadata": r.metadata, "similarity": r.similarity} for r in results.results]

async def approve_draft(client: AsyncSupermemory, custom_id: str, actor: str) -> dict:
    # See 06-conflict-resolution-manual-override.md for full implementation
    return await handle_approve_reject(client, "approve", custom_id, actor)

async def reject_draft(client: AsyncSupermemory, custom_id: str, actor: str) -> dict:
    return await handle_approve_reject(client, "reject", custom_id, actor)
```

## Teams Integration

Draft queue maps to:
- `review:` command → list drafts as Adaptive Cards
- Each card has Approve/Reject buttons with `customId` in the action payload
- Button click → `approve:<customId>` or `reject:<customId>` flow

## IMPORTANT NOTES
1. Drafts are filtered by `status=draft` in Supermemory metadata
2. POC exposed this via `review:`, `approve:`, `reject:` chat commands
3. In Teams, use Adaptive Cards with action buttons instead of text commands
