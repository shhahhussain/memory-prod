# Sprint 2 — Core Agent Port (n8n → Python) Research

**Milestone:** M2 — Core Agent Port (50-60h)
**Focus:** Port all 4 agents + orchestration + memory services to Python

This is the **biggest sprint** — 40% of the entire project. Everything else depends on this.

---

## What to Research

### 1. Multi-Agent Orchestration (MINDY)

**How n8n maps to Python:**
| n8n concept | Python equivalent |
|------------|------------------|
| Sequential node chain | `WorkflowBuilder` with `add_edge()` |
| Parallel execution | `ConcurrentBuilder` / `asyncio.gather()` |
| HTTP/API nodes | Agent tools (annotated Python functions) |
| Execute Workflow | Direct function calls / agent dispatch |

**Fan-out pattern (CRITICAL):**
```python
import asyncio

async def fan_out(agents, request):
    tasks = [asyncio.wait_for(agent.execute(request), timeout=30.0) for agent in agents]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    successes = [r for r in results if not isinstance(r, BaseException)]
    return successes
```

> Use `asyncio.gather(return_exceptions=True)` NOT `asyncio.TaskGroup` — you want partial success.

**Docs:**
- Workflows: https://learn.microsoft.com/en-us/agent-framework/workflows/
- Multi-agent blog: https://devblogs.microsoft.com/semantic-kernel/unlocking-enterprise-ai-complexity-multi-agent-orchestration-with-the-microsoft-agent-framework/
- Samples: `python/samples/03-workflows` in Agent-Framework-Samples repo

**Search queries:**
- "Microsoft Agent Framework Python multi-agent orchestration"
- "asyncio gather return_exceptions fan out pattern"
- "agent as tools pattern Python"

---

### 2. Intent Routing — Hybrid NLU

POC used hardcoded prefixes (`search:`, `write:`, `review:`). Prod needs natural language.

**3-tier approach:**
```
Tier 1: Keyword/regex fast path (free, 60-70% of traffic)
Tier 2: Cheap LLM classifier (Gemini Flash for ambiguous)
Tier 3: Clarification (confidence < 0.65 → ask user)
```

**POC intent thresholds to port:**
- read threshold: 0.75
- review threshold: 0.80
- mutate suggest threshold: 0.50
- auto-write threshold: 0.70

**Search queries:**
- "hybrid intent classifier keyword LLM fallback Python"
- "Gemini Flash API Python classification"
- "pydantic enum intent routing"

---

### 3. Conflict Resolution Engine (CRITICAL — complex POC logic)

The POC has a full multi-dimension conflict resolver. Must port accurately.

**POC scoring dimensions (in order):**
1. Type rank (unknown penalized)
2. Recency (as_of desc)
3. Confidence (desc)
4. Source authority (asc — lower = higher)
5. Stable fallback by index

**Additional POC logic:**
- Groups by `metadata.conflict_group`
- Lazy conflict detection from type/client/content tokens
- Value-signature dedup (same normalized content = not a real conflict)
- Tie → `needs_human=true`
- Manual override system (set/get/clear/list) with advisory locks in PG
- Audit logging to `conflict_audit_log` + `conflict_audit_snapshot`
- Winner status sync back to Supermemory

**Search queries:**
- "conflict resolution patterns distributed systems Python"
- "multi-dimension scoring algorithm Python dataclass"
- "advisory locks asyncpg Python"
- "event sourcing audit log pattern"
- "deterministic tie-breaking algorithm"

---

### 4. Guardrails + Dedupe Pipeline

POC write path: Validation → Guardrails → Dedupe → Supermemory Write

**Validation rules:**
- `memory_type` ∈ {fact, rule, agent, vector}
- `source_type` ∈ {slack, chat, email, doc, api, human, seed}

**Guardrail rules:**
- fact/rule without `source_id` or `as_of` → demoted to `status=draft`
- `guardrail_reason = 'missing_source_id_or_as_of'`

**Dedupe rules:**
- Generate deterministic `customId` when absent
- Ensure `conflict_group` exists (defaults to customId)

**Search queries:**
- "pydantic validator custom field Python"
- "pydantic model validator pre post"
- "deterministic ID generation Python hashlib"
- "data validation pipeline pattern Python"

---

### 5. Draft Queue / Human-in-the-Loop

POC operations: list, approve, reject, update

**Approve:** status draft → active, source_authority=1, source_id='human-review'
**Reject:** status draft → deprecated
**Update:** rewrite content, keep status=draft

**Search queries:**
- "human in the loop AI agent approval Python"
- "state machine pattern Python approval workflow"

---

### 6. Memory Extraction from LLM Responses

After LLM responds, second LLM call extracts memories.

**POC contract:**
```json
{
  "shouldWrite": true,
  "items": [
    {
      "content": "...",
      "metadata": {
        "memory_type": "fact",
        "source_type": "chat",
        "confidence": 0.95,
        "as_of": "2026-03-21"
      }
    }
  ]
}
```

- Max 2 items per extraction
- search/review modes → shouldWrite forced false

**Search queries:**
- "Claude structured output tool_use Python"
- "pydantic model from LLM JSON response"
- "anthropic SDK structured output"

---

### 7. Context Window Token Budgeting

POC: char-based (8000 chars, 8 chunks). Prod: real tokens.

**Claude Token Counting API:**
```python
response = await client.beta.messages.count_tokens(
    model="claude-sonnet-4-5-20250514",
    system=system_prompt,
    messages=messages,
)
token_count = response.input_tokens
```

**Rules:**
- Summarize when >75% capacity
- Per-agent scoped context (2-3 sentences, not full history)
- Max 8 memory chunks in context pack

**Search queries:**
- "Claude token counting API Python anthropic"
- "rolling summarization conversation history"
- "context window management multi-agent system"

---

### 8. Supermemory Integration (Deep)

**Python SDK (recommended):**
```python
from supermemory import AsyncSupermemory

client = AsyncSupermemory(api_key="sm_key")

# Search with filters (mirrors POC SVC - SM - Search)
response = await client.search.documents(
    q=query,
    container_tags=["orgmind-poc"],
    limit=5,
    threshold=0.5,
    rerank=True,
    filters={"AND": [{"key": "status", "value": "active"}]}
)

# Write with metadata (mirrors POC SVC - SM - Write)
await client.add(
    content="Acme Q1 budget is $50K",
    container_tags=["orgmind-poc"],
    metadata={
        "memory_type": "fact",
        "source_type": "chat",
        "status": "active",
        "conflict_group": "acme_budget_q1",
        "confidence": 0.95,
        "as_of": "2026-03-21"
    },
    custom_id="fact_acme_budget_q1_50k"
)
```

**Search queries:**
- "supermemory Python SDK async"
- "supermemory API search filters metadata"

---

### 9. Specialist Agents

**FINDR (Research):**
- Searches Supermemory for context
- Returns findings + citations + confidence
- Search: "Python async HTTP client httpx"

**TASKR (Project):**
- Parses natural language → task fields
- Creates Asana tasks
- Multi-turn: stores pending state when fields missing
- Search: "Asana API Python create task", "pip install asana"

**CAMPA (Campaign):**
- Creates Google Docs with campaign briefs
- Template-based pre-filling
- Search: "Google Docs API Python create document", "google-api-python-client"

---

### 10. PostgreSQL Async Access

POC used n8n Postgres nodes. Prod needs async Python.

**Search queries:**
- "asyncpg Python PostgreSQL async"
- "SQLAlchemy async Python 2026"
- "asyncpg connection pool"

```python
import asyncpg

pool = await asyncpg.create_pool(dsn=settings.postgres_url)
async with pool.acquire() as conn:
    rows = await conn.fetch("SELECT * FROM agents WHERE status = 'active'")
```

---

## Checklist
- [ ] Understand `asyncio.gather` fan-out pattern
- [ ] Port conflict resolution scoring to Python dataclass
- [ ] Port guardrails/dedupe to Pydantic validators
- [ ] Test Supermemory SDK with filters + metadata writes
- [ ] Test Claude structured output for memory extraction
- [ ] Test Claude token counting API
- [ ] Test asyncpg connection to project Postgres
- [ ] Test Asana API create task
- [ ] Test Google Docs API create document
- [ ] Map all POC payload contracts to Pydantic models
