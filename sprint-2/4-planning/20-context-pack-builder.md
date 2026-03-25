# Topic: Context Pack Builder — Assembling LLM Input

**Time:** 15 min
**Goal:** Port POC's Code - Build Context Pack to Python

---

## What to Search
- "LLM context assembly Python"
- "prompt template builder Python"

## What It Does
After searching Supermemory + fetching PG config, assembles everything into the LLM prompt.

## POC Rules
- Max chunks: 8
- Max serialized chars: 8000 (prod: use real token counting)
- Max project rows: 12
- For compare queries (Acme vs Globex), enforce representation from both sides

## Code Pattern
```python
from pydantic import BaseModel

class ContextPack(BaseModel):
    system_prompt: str
    memory_chunks: list[dict]
    project_rows: list[dict]
    user_text: str
    mode: str
    actor: str

    def to_chat_input(self) -> str:
        chunks_text = "\n".join(
            f"[{i+1}] {c.get('content', '')} "
            f"(type: {c.get('memory_type', '?')}, confidence: {c.get('confidence', '?')}, "
            f"as_of: {c.get('as_of', '?')})"
            for i, c in enumerate(self.memory_chunks[:8])
        )

        projects_text = "\n".join(
            f"- {p.get('name', '?')}: {p.get('status', '?')}"
            for p in self.project_rows[:12]
        )

        return f"""{self.system_prompt}

## Retrieved Context
{chunks_text}

## Active Projects
{projects_text}

## User Question
{self.user_text}"""

async def build_context_pack(
    search_results: list,
    db: Database,
    user_text: str,
    mode: str,
    actor: str,
) -> ContextPack:
    # Fetch system prompt
    prompt_row = await db.fetchrow("SELECT prompt_text FROM prompts WHERE agent_id = 'mindy'")
    system_prompt = prompt_row["prompt_text"] if prompt_row else "You are MINDY, an AI orchestrator."

    # Fetch project config
    projects = await db.fetch("SELECT * FROM projects WHERE status = 'active' LIMIT 12")

    # Build memory chunks with metadata
    chunks = [
        {
            "content": r.chunk or r.memory,
            "memory_type": r.metadata.get("memory_type", "unknown"),
            "source_type": r.metadata.get("source_type", "unknown"),
            "confidence": r.similarity,
            "as_of": r.metadata.get("as_of", "unknown"),
            "conflict_group": r.metadata.get("conflict_group", ""),
            "source_authority": r.metadata.get("source_authority", 5),
        }
        for r in search_results[:8]
    ]

    return ContextPack(
        system_prompt=system_prompt,
        memory_chunks=chunks,
        project_rows=[dict(p) for p in projects],
        user_text=user_text,
        mode=mode,
        actor=actor,
    )
```

## What to Understand
- [ ] Context pack = system prompt + memory chunks + project rows + user question
- [ ] 8 chunks max, 12 project rows max
- [ ] Chunk metadata includes: type, confidence, as_of, conflict_group, source_authority
- [ ] This feeds directly into the Claude messages API call
- [ ] POC fetched prompt and config from separate PG services — now it's just 2 queries
