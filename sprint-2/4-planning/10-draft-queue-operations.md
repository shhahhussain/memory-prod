# Topic: Draft Queue — List / Approve / Reject / Update

**Time:** 20 min
**Goal:** Port the POC's draft review system to Python

---

## What to Search
- "state machine pattern Python approval"
- "Supermemory update document metadata"
- "approval workflow async Python"

## POC Operations

### List Drafts
```python
async def list_drafts(memory_client, container_tag: str) -> list[Memory]:
    response = await memory_client.search.documents(
        q="draft items",
        container_tags=[container_tag],
        limit=20,
        filters={"AND": [{"key": "status", "value": "draft"}]}
    )
    return response.results
```

### Approve (draft → active)
```python
async def approve_draft(memory_client, custom_id: str, approved_by: str):
    # Find the draft by customId
    results = await memory_client.search.documents(
        q=custom_id, container_tags=["orgmind-poc"], limit=5
    )
    draft = find_exact_match(results, custom_id)
    if not draft:
        raise ValueError(f"Draft {custom_id} not found")

    # Rewrite with active status
    await memory_client.add(
        content=draft.content,  # Keep original content
        container_tags=["orgmind-poc"],
        custom_id=custom_id,   # Same ID = overwrites
        metadata={
            **draft.metadata,
            "status": "active",
            "source_id": "human-review",
            "source_authority": 1,
            "as_of": str(date.today()),
            "is_current": True,
        }
    )
```

### Reject (draft → deprecated)
```python
async def reject_draft(memory_client, custom_id: str, rejected_by: str):
    draft = await find_draft(memory_client, custom_id)
    await memory_client.add(
        content=draft.content,
        container_tags=["orgmind-poc"],
        custom_id=custom_id,
        metadata={
            **draft.metadata,
            "status": "deprecated",
            "is_current": False,
        }
    )
```

### Update (rewrite content, keep draft)
```python
async def update_draft(memory_client, custom_id: str, new_content: str):
    draft = await find_draft(memory_client, custom_id)
    await memory_client.add(
        content=new_content,  # New content
        container_tags=["orgmind-poc"],
        custom_id=custom_id,
        metadata={
            **draft.metadata,
            "status": "draft",  # Still draft
        }
    )
```

## Selection Methods
POC supports two ways to select a draft:
1. By `customId` — exact match
2. By list index — "approve 3" means approve the 3rd item from list

## What to Understand
- [ ] Approve = rewrite same customId with `status: active`
- [ ] Reject = rewrite same customId with `status: deprecated`
- [ ] Update = rewrite content but keep `status: draft`
- [ ] Selection by index requires remembering the last list order
- [ ] `source_id: "human-review"` marks it was human-approved
