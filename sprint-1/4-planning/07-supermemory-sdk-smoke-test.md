# Topic: Supermemory Python SDK — Smoke Test

**Time:** 20-30 min
**Goal:** Verify you can connect to Supermemory, write a memory, and search it back

---

## What to Search
- "supermemory Python SDK quickstart"
- "pip install supermemory async"

## Docs to Read
- https://supermemory.ai/docs/intro
- https://supermemory.ai/docs/integrations/supermemory-sdk
- Console (get API key): https://console.supermemory.ai

## Install
```bash
pip install supermemory
```

## Smoke Test Script
```python
import asyncio
from supermemory import AsyncSupermemory

async def main():
    client = AsyncSupermemory(api_key="sm_your_key_here")

    # 1. Write a test memory
    print("Writing memory...")
    await client.add(
        content="Test fact: OrgMind smoke test at 2026-03-21",
        container_tags=["orgmind-test"],
        metadata={"memory_type": "fact", "source_type": "human", "status": "active"}
    )

    # 2. Search it back
    print("Searching...")
    response = await client.search.memories(
        q="OrgMind smoke test",
        container_tags=["orgmind-test"]
    )
    print(f"Found {len(response.results)} results")
    for r in response.results:
        print(f"  - {r.memory}")

    # 3. Search documents (RAG chunks)
    response = await client.search.documents(
        q="OrgMind smoke test",
        container_tags=["orgmind-test"]
    )
    print(f"Found {len(response.results)} document results")

asyncio.run(main())
```

## What to Understand
- [ ] Difference between `search.memories()` (extracted facts) and `search.documents()` (RAG chunks)
- [ ] How `container_tags` work (scoping)
- [ ] How `metadata` is stored and filtered
- [ ] What the response object looks like
- [ ] AsyncSupermemory vs sync Supermemory
