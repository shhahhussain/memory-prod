# Topic: FINDR Agent — Research Specialist Port

**Time:** 15-20 min
**Goal:** Understand what FINDR does in POC and how to port it

---

## What to Search
- "Python async HTTP client httpx"
- "agent tool pattern Python"

## What FINDR Does (from POC)
1. Receives research query from MINDY
2. Builds memory search payload
3. Searches Supermemory for relevant context
4. (Optional) Adds mock external MCP signals (Kantar, Similarweb)
5. Composes findings with citations
6. Returns: findings, citations, source list, confidence
7. Fallback: supports write/review/approve/reject when routed for memory ops

## Output Contract
```python
from pydantic import BaseModel

class FindrResult(BaseModel):
    findings: str                    # Main research summary
    citations: list[str]             # Source references
    sources: list[dict]              # Detailed source objects
    confidence: float                # 0-1 confidence in findings
    memory_operation: str | None     # "write", "approve", etc. if applicable
```

## Skeleton
```python
class FindrAgent:
    def __init__(self, memory_client, llm_client):
        self.memory = memory_client
        self.llm = llm_client

    async def research(self, query: str, context: dict) -> FindrResult:
        # 1. Search Supermemory
        results = await self.memory.search.documents(
            q=query,
            container_tags=[context.get("container_tag", "orgmind-poc")],
            limit=5,
            rerank=True,
        )

        # 2. Build context from results
        memory_context = "\n".join(
            f"- {r.chunk or r.memory} (confidence: {r.similarity:.2f})"
            for r in results.results
        )

        # 3. Generate research response
        response = await self.llm.messages.create(
            model="claude-sonnet-4-5-20250514",
            max_tokens=1000,
            system="You are FINDR, a research specialist. Cite sources.",
            messages=[{"role": "user", "content": f"Research: {query}\n\nContext:\n{memory_context}"}],
        )

        # 4. Extract citations from response
        return FindrResult(
            findings=response.content[0].text,
            citations=extract_citations(response.content[0].text),
            sources=[{"id": r.id, "similarity": r.similarity} for r in results.results],
            confidence=calculate_confidence(results.results),
        )
```

## What to Understand
- [ ] FINDR's primary job is: search memory → add context → LLM → structured output
- [ ] Citations come from Supermemory result metadata
- [ ] Confidence is derived from search result similarities
- [ ] FINDR also handles memory write/review operations when routed that way
