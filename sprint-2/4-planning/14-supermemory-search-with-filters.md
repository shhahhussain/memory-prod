# Topic: Supermemory — Search with Metadata Filters

**Time:** 15 min
**Goal:** Port POC's SVC - SM - Search to Python SDK with full filter support

---

## What to Search
- "supermemory Python SDK search filters"
- "supermemory API v4 search metadata filter"

## POC Search Contract
```json
{
  "q": "acme q1 budget",
  "limit": 5,
  "containerTags": ["orgmind-poc"],
  "filters": {
    "AND": [{"key": "status", "value": "active"}]
  }
}
```

## Python SDK
```python
from supermemory import AsyncSupermemory

client = AsyncSupermemory(api_key=settings.supermemory_api_key)

async def search_memory(
    query: str,
    container_tag: str = "orgmind-poc",
    limit: int = 5,
    status_filter: str = "active",
    extra_filters: list[dict] | None = None,
) -> list:
    filters = {"AND": [{"key": "status", "value": status_filter}]}
    if extra_filters:
        filters["AND"].extend(extra_filters)

    response = await client.search.documents(
        q=query,
        container_tags=[container_tag],
        limit=min(max(limit, 1), 100),  # Clamp to 1-100
        threshold=0.5,
        rerank=True,
        search_mode="hybrid",
        filters=filters,
    )
    return response.results
```

## Search Modes
- `"hybrid"` — memories (extracted facts) + document chunks (DEFAULT, use this)
- `"memories"` — extracted facts only

## What to Understand
- [ ] `search.documents()` for hybrid search (facts + chunks)
- [ ] `search.memories()` for extracted facts only
- [ ] `rerank=True` adds ~100ms but improves quality
- [ ] `threshold=0.5` is the similarity cutoff
- [ ] Filters use AND/OR with key-value pairs on metadata
- [ ] Default filter: `status=active` (matches POC behavior)
