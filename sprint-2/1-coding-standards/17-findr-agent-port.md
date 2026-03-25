# FINDR Agent Port (Code-Ready Reference)

> For Claude Code: Port FINDR (research specialist) from n8n to Python.

## FINDR's Role

FINDR is the **search/research specialist**. It:
1. Receives a query from MINDY
2. Searches Supermemory (with filters)
3. Resolves conflicts in results
4. Builds a context pack
5. Generates a response with citations

## Implementation

```python
from agent_framework.anthropic import AnthropicClient
from agent_framework import tool
from typing import Annotated
from supermemory import AsyncSupermemory

sm_client = AsyncSupermemory()

@tool(approval_mode="never_require")
async def search_memory(
    query: Annotated[str, "The search query"],
    client_filter: Annotated[str, "Filter by client name (optional)"] = "",
) -> str:
    filters = {"AND": [{"key": "status", "value": "active"}]}
    if client_filter:
        filters["AND"].append({"key": "client", "value": client_filter})

    results = await sm_client.search.execute(
        q=query, container_tags=["orgmind"], limit=10, rerank=True,
    )

    if not results.results:
        return "No results found."

    output = []
    for r in results.results:
        content = r.memory or r.chunk or ""
        source = r.metadata.get("source_type", "unknown")
        as_of = r.metadata.get("as_of", "unknown")
        output.append(f"- {content} [source: {source}, as_of: {as_of}]")

    return "\n".join(output)

def create_findr(anthropic_client: AnthropicClient) -> "Agent":
    return anthropic_client.as_agent(
        name="FINDR",
        instructions="""You are FINDR, OrgMind's research specialist.

Your role: Search organizational memory to answer questions accurately.

Guidelines:
- Always cite sources with dates
- If conflicting information exists, present the most recent/authoritative
- If you can't find relevant information, say so clearly
- Be concise but thorough""",
        tools=[search_memory],
    )
```

## IMPORTANT NOTES
1. FINDR's system prompt comes from `prompts` table (fetch at startup)
2. Tool results include source metadata for citations
3. Conflict resolution happens in the tool, not the agent
4. Always filter by `status=active` by default
