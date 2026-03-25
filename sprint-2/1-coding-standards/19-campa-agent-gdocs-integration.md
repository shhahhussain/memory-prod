# CAMPA Agent Port (Code-Ready Reference)

> For Claude Code: Port CAMPA (campaign/doc drafting) from n8n to Python.

## CAMPA's Role

CAMPA drafts campaign briefs, documents, and proposals. It searches memory for context, then generates structured documents.

## Implementation

```python
from agent_framework.anthropic import AnthropicClient
from agent_framework import tool
from typing import Annotated

@tool(approval_mode="never_require")
async def search_campaign_context(
    query: Annotated[str, "Search for campaign-related context"],
) -> str:
    results = await sm_client.search.execute(
        q=query, container_tags=["orgmind"], limit=10, rerank=True,
    )
    if not results.results:
        return "No relevant campaign context found."

    return "\n".join(
        f"- {r.memory or r.chunk}" for r in results.results if r.memory or r.chunk
    )

@tool(approval_mode="never_require")
async def save_draft(
    title: Annotated[str, "Document title"],
    content: Annotated[str, "Document content"],
    doc_type: Annotated[str, "Type: brief, proposal, report"] = "brief",
) -> str:
    result = await sm_client.documents.add(
        content=f"# {title}\n\n{content}",
        container_tags=["orgmind"],
        metadata={
            "memory_type": "agent",
            "source_type": "agent",
            "entity_type": "document",
            "document_type": doc_type,
            "status": "draft",
            "created_by": "CAMPA",
        },
    )
    return f"Draft saved: {title} (id: {result.id})"

def create_campa(anthropic_client: AnthropicClient) -> "Agent":
    return anthropic_client.as_agent(
        name="CAMPA",
        instructions="""You are CAMPA, OrgMind's campaign and document drafting specialist.
Your role: Draft campaign briefs, proposals, and documents.
Always search for context first before drafting.
Structure documents with clear sections and headers.""",
        tools=[search_campaign_context, save_draft],
    )
```

## IMPORTANT NOTES
1. CAMPA always searches for context BEFORE drafting
2. Drafts are saved to Supermemory with `status=draft` and `entity_type=document`
3. Users can review/approve drafts via the draft queue
