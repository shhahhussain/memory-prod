# Supermemory Search with Filters (Code-Ready Reference)

> For Claude Code: Advanced search patterns for FINDR agent.

## Basic Search

```python
from supermemory import AsyncSupermemory

client = AsyncSupermemory()

results = await client.search.execute(
    q="Nike Q4 campaign budget",
    container_tags=["orgmind"],
    limit=10,
    threshold=0.5,
    rerank=True,
)
```

## Filtered Search (Metadata Filters)

### REST API format (for reference)

```json
{
  "q": "budget",
  "containerTag": "orgmind",
  "filters": {
    "AND": [
      {"key": "status", "value": "active"},
      {"key": "client", "value": "acme"}
    ]
  }
}
```

### Python SDK — pass filters via kwargs or use REST directly

```python
import httpx

async def search_with_filters(
    query: str,
    filters: dict | None = None,
    container_tag: str = "orgmind",
    limit: int = 10,
    search_mode: str = "hybrid",
    api_key: str = "",
) -> dict:
    async with httpx.AsyncClient() as http:
        response = await http.post(
            "https://api.supermemory.ai/v4/search",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "q": query,
                "containerTag": container_tag,
                "searchMode": search_mode,
                "limit": limit,
                "threshold": 0.5,
                "rerank": True,
                **({"filters": filters} if filters else {}),
            },
        )
        response.raise_for_status()
        return response.json()
```

## Common Filter Patterns

```python
# Active memories only (POC default)
ACTIVE_ONLY = {"AND": [{"key": "status", "value": "active"}]}

# Drafts only (for review queue)
DRAFTS_ONLY = {"AND": [{"key": "status", "value": "draft"}]}

# Client-specific
CLIENT_FILTER = lambda client: {"AND": [{"key": "status", "value": "active"}, {"key": "client", "value": client}]}

# Department-specific
DEPT_FILTER = lambda dept: {"AND": [{"key": "status", "value": "active"}, {"key": "department", "value": dept}]}
```

## IMPORTANT NOTES
1. Default filter should ALWAYS include `status=active` (matches POC)
2. `rerank=True` adds ~100ms but significantly improves relevance
3. Search mode: `hybrid` for general queries, `memories` for fact lookups
4. SDK may not expose all filter options — use REST API directly if needed
