# Supermemory SDK — Smoke Test (Code-Ready Reference)

> For Claude Code: Use this as the authoritative reference for ALL Supermemory interactions in OrgMind.

## Installation

```bash
pip install supermemory
```

**Python:** >=3.8
**Current version:** 3.30.1+ (March 2026)

## Client Initialization

```python
import os
from supermemory import Supermemory, AsyncSupermemory

# Sync client
client = Supermemory(
    api_key=os.environ.get("SUPERMEMORY_API_KEY"),
    max_retries=2,      # default
    timeout=60.0,        # default, seconds
)

# Async client (USE THIS FOR ORGMIND — everything is async)
client = AsyncSupermemory(
    api_key=os.environ.get("SUPERMEMORY_API_KEY"),
)
```

**API keys start with `sm_`**. Get one at https://console.supermemory.ai

## Environment Variables

```bash
SUPERMEMORY_API_KEY=sm_your_key_here
```

## Core Operations

### 1. Add Content (Ingest)

```python
# Add text content
result = await client.documents.add(
    content="Nike Q4 campaign budget increased to $2.1M as per the March meeting.",
    container_tags=["project_nike"],
    metadata={"source": "meeting_notes", "category": "budget"},
    custom_id="nike-q4-budget-001",          # optional — enables dedup
    entity_context="Nike campaign planning",  # optional — guides extraction, max 1500 chars
)
print(result.id)       # document ID
print(result.status)   # "queued" | "processing" | "done"
```

### 2. Upload File

```python
from pathlib import Path

result = await client.documents.upload_file(
    file=Path("/path/to/document.pdf"),
    container_tags=["project_nike"],
)
```

Supported: PDF, DOC, DOCX, TXT, MD, JPG, PNG, GIF, WebP, CSV, MP4, YouTube URLs. Max 50MB.

### 3. Search — Documents (RAG Chunks)

```python
response = await client.search.execute(
    q="Nike campaign budget",
    container_tags=["project_nike"],
    limit=10,
    threshold=0.5,
    rerank=True,
)

for result in response.results:
    print(result.id)
    print(result.similarity)   # 0.0 - 1.0
    print(result.chunk)        # document content (if chunk)
    print(result.memory)       # extracted fact (if memory)
    print(result.metadata)     # dict
    print(result.updated_at)   # ISO timestamp
    print(result.version)      # int
```

### 4. Delete Document

```python
# By internal ID
await client.documents.delete(doc_id="abc123")

# By custom ID
await client.documents.delete(doc_id="nike-q4-budget-001")
```

### 5. List Documents

```python
docs = await client.documents.list(
    container_tags=["project_nike"],
    limit=10,
)
```

### 6. User Profile

```python
profile = await client.profile(container_tag="project_nike")
print(profile.profile.static)    # stable preferences
print(profile.profile.dynamic)   # recent activity
```

## REST API (Direct HTTP — Alternative Path)

**Base URL:** `https://api.supermemory.ai`
**Auth:** `Authorization: Bearer sm_your_key`

### POST /v3/documents — Add Content

```json
{
  "content": "string (required)",
  "customId": "string (optional)",
  "containerTag": "string (optional)",
  "metadata": {"key": "value"},
  "entityContext": "string (max 1500 chars)"
}
```

Response: `{"id": "string", "status": "queued|processing|done"}`

### POST /v4/search — Search

```json
{
  "q": "search query (required)",
  "containerTag": "string",
  "searchMode": "hybrid|memories",
  "limit": 10,
  "threshold": 0.5,
  "rerank": false,
  "filters": {
    "AND": [
      {"key": "category", "value": "budget"}
    ]
  }
}
```

Response:
```json
{
  "results": [
    {
      "id": "string",
      "memory": "extracted fact or null",
      "chunk": "document content or null",
      "similarity": 0.91,
      "metadata": {},
      "updatedAt": "ISO timestamp",
      "version": 1
    }
  ],
  "timing": 92,
  "total": 5
}
```

### Search Modes

| Mode | Returns | Use When |
|------|---------|----------|
| `hybrid` (default) | memories + document chunks | General search — best coverage |
| `memories` | extracted facts only | Quick factual lookups |

### Filter Syntax

```json
{
  "filters": {
    "AND": [
      {"key": "type", "value": "meeting"},
      {"key": "year", "value": "2024"}
    ]
  }
}
```

Filter types: string equality, `string_contains`, numeric comparisons, `array_contains`, `negate`.

## Conflict Resolution / Supersede

Supermemory handles supersedence **automatically**. When you add "Budget is now $2.5M", it supersedes an older memory "Budget is $2.1M". No explicit API call needed.

To explicitly forget: use MCP `memory` tool with `action: "forget"`.

## Smoke Test Script

```python
import asyncio
import os
from supermemory import AsyncSupermemory

async def smoke_test():
    client = AsyncSupermemory(api_key=os.environ["SUPERMEMORY_API_KEY"])

    # 1. Add content
    print("Adding content...")
    doc = await client.documents.add(
        content="OrgMind smoke test: The annual planning meeting is on April 15th.",
        container_tags=["orgmind_test"],
        metadata={"source": "smoke_test"},
        custom_id="smoke-test-001",
    )
    print(f"  Document ID: {doc.id}, Status: {doc.status}")

    # 2. Wait for processing (status goes queued -> processing -> done)
    import time
    time.sleep(3)

    # 3. Search
    print("\nSearching...")
    results = await client.search.execute(
        q="When is the annual planning meeting?",
        container_tags=["orgmind_test"],
    )
    for r in results.results:
        print(f"  Score: {r.similarity:.2f} | {r.memory or r.chunk}")

    # 4. Clean up
    print("\nCleaning up...")
    await client.documents.delete(doc_id="smoke-test-001")
    print("  Deleted.")

    print("\nSmoke test PASSED!")

if __name__ == "__main__":
    asyncio.run(smoke_test())
```

## IMPORTANT NOTES FOR CODE GENERATION

1. **Always use `AsyncSupermemory`** — OrgMind is fully async
2. **Container tags** scope memory per project/user — ALWAYS set them
3. **`custom_id`** enables dedup — use it for content that may be re-ingested
4. **Search returns both `memory` and `chunk`** — check which is non-null
5. **Supersede is automatic** — just add new content, engine resolves conflicts
6. **Processing is async** — `status: "queued"` means not yet searchable
7. **Responses are Pydantic models** — IDE autocomplete works
8. API keys start with `sm_`
