# Context Pack Builder (Code-Ready Reference)

> For Claude Code: Port the POC's `Code - Build Context Pack` node.

## Purpose

Assembles the context window for LLM calls: system prompt + memory results + user message, respecting token budgets.

## Implementation

```python
from pydantic import BaseModel

class ContextChunk(BaseModel):
    content: str
    source: str
    memory_type: str = ""
    confidence: float = 0.0
    as_of: str = ""
    conflict_group: str = ""

class ContextPack(BaseModel):
    system_prompt: str
    context_chunks: list[ContextChunk]
    user_message: str
    total_approx_tokens: int

def build_context_pack(
    system_prompt: str,
    search_results: list[dict],
    user_message: str,
    max_tokens: int = 80000,
) -> ContextPack:
    budget = max_tokens
    budget -= len(system_prompt) // 4
    budget -= len(user_message) // 4
    budget -= 2000  # Reserve for response

    chunks = []
    used = 0

    # Sort by relevance (similarity score)
    sorted_results = sorted(search_results, key=lambda r: r.get("similarity", 0), reverse=True)

    for r in sorted_results:
        content = r.get("memory") or r.get("chunk") or ""
        meta = r.get("metadata", {})
        cost = len(content) // 4

        if used + cost > budget:
            break

        chunks.append(ContextChunk(
            content=content,
            source=meta.get("source_type", "unknown"),
            memory_type=meta.get("memory_type", ""),
            confidence=float(meta.get("confidence", 0)),
            as_of=meta.get("as_of", ""),
            conflict_group=meta.get("conflict_group", ""),
        ))
        used += cost

    return ContextPack(
        system_prompt=system_prompt,
        context_chunks=chunks,
        user_message=user_message,
        total_approx_tokens=used + len(system_prompt) // 4 + len(user_message) // 4,
    )

def format_context_for_llm(pack: ContextPack) -> str:
    if not pack.context_chunks:
        return "No relevant context found in organizational memory."

    lines = ["## Retrieved Context\n"]
    for i, chunk in enumerate(pack.context_chunks, 1):
        meta_parts = []
        if chunk.source:
            meta_parts.append(f"source: {chunk.source}")
        if chunk.as_of:
            meta_parts.append(f"as_of: {chunk.as_of}")
        if chunk.confidence:
            meta_parts.append(f"confidence: {chunk.confidence:.0%}")
        meta = f" ({', '.join(meta_parts)})" if meta_parts else ""
        lines.append(f"{i}. {chunk.content}{meta}")

    return "\n".join(lines)
```

## IMPORTANT NOTES
1. Always sort by similarity/relevance before budgeting
2. Token budget: 80K of 200K — leaves room for response + thinking
3. Include metadata annotations for LLM to cite sources
4. Maps directly to POC's `Code - Build Context Pack` node
