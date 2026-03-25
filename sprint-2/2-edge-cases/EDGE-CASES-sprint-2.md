# Sprint 2 — Edge Cases & Known Pitfalls

> **Scope:** Async fan-out, intent routing, conflict resolution, guardrails, dedupe, draft queue, memory extraction, token counting, Supermemory search/write, asyncpg, FINDR/TASKR/CAMPA agents, context pack builder

---

## Research-Verified Findings

The following were independently verified via Claude deep-research against official documentation:

- **Supermemory `customId` = upsert:** Passing the same `customId` in a write call overwrites the previous memory (not duplicates). This confirms our idempotent retry pattern in EC-2.13.
- **Claude empty `content` array:** Confirmed that Claude can return `response.content = []` on safety refusals. Always check before indexing. (EC-2.8)
- **asyncpg prepared statement cache:** Confirmed that `InvalidCachedStatementError` is thrown when schema changes invalidate cached statements. Use `statement_cache_size=0` during migrations or explicit column lists. (EC-4.12 / Sprint 4)

---

## 1. Async Fan-Out Orchestration

### EC-2.1 — One agent times out, others succeed

**Scenario:** MINDY fires `asyncio.gather(findr(), taskr(), campa())`. FINDR hangs on Supermemory. After 30s, `asyncio.gather` raises `TimeoutError` — but `return_exceptions=False` means **all** successful results are discarded.

**Why dangerous:** You silently drop TASKR and CAMPA results. MINDY returns an empty synthesis. The user gets nothing despite two agents succeeding.

```python
# WRONG — TimeoutError cancels everything
results = await asyncio.gather(findr(), taskr(), campa())

# CORRECT — per-agent timeout + collect partial results
async def with_timeout(coro, agent_name: str, timeout: float):
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning("agent_timeout", agent=agent_name)
        return AgentResult(agent=agent_name, error="timeout", data=None)
    except Exception as e:
        logger.error("agent_error", agent=agent_name, exc=str(e))
        return AgentResult(agent=agent_name, error=str(e), data=None)

results = await asyncio.gather(
    with_timeout(findr(), "FINDR", 20.0),
    with_timeout(taskr(), "TASKR", 15.0),
    with_timeout(campa(), "CAMPA", 25.0),
    return_exceptions=False,  # safe now — each coro catches its own errors
)

# MINDY synthesizes from results, filtering errors
available = [r for r in results if r.error is None]
```

### EC-2.2 — All agents fail simultaneously

**Scenario:** Supermemory goes down. All three agents fail during memory reads at the same millisecond. MINDY's synthesizer receives `[AgentResult(error=...), ...]` for all agents.

**Why dangerous:** Synthesizer calls `results[0].data["memories"]` → `AttributeError` on `None`. Unhandled exception propagates to Teams as a raw 500.

```python
async def mindy_synthesize(results: list[AgentResult]) -> str:
    successful = [r for r in results if r.error is None and r.data]
    if not successful:
        errors = {r.agent: r.error for r in results}
        logger.error("all_agents_failed", errors=errors)
        return "I'm having trouble reaching my knowledge systems. Please try again in a moment."
    return await llm_synthesize(successful)
```

### EC-2.3 — Concurrent messages from same user (race condition)

**Scenario:** User sends message A, then message B immediately. Both enter MINDY. Message A reads user context from DB → modifies it → writes back. Message B reads the **same stale snapshot** before A's write completes. Last-write-wins corrupts state.

```python
# Per-user async lock to serialize MINDY invocations (single instance)
_user_locks: dict[str, asyncio.Lock] = {}

async def handle_user_message(user_id: str, message: str):
    if user_id not in _user_locks:
        _user_locks[user_id] = asyncio.Lock()
    async with _user_locks[user_id]:
        return await mindy_orchestrate(user_id, message)

# For multi-instance: use PostgreSQL advisory lock
async with pool.acquire() as conn:
    await conn.execute("SELECT pg_advisory_lock(hashtext($1))", f"user_lock:{user_id}")
    try:
        return await mindy_orchestrate(user_id, message)
    finally:
        await conn.execute("SELECT pg_advisory_unlock(hashtext($1))", f"user_lock:{user_id}")
```

### EC-2.4a — Race conditions in shared state (immutable snapshots)

**Scenario:** MINDY fans out to FINDR, TASKR, CAMPA — all receive a reference to the same `context` dict. FINDR mutates `context["memories"]` mid-flight. TASKR reads `context["memories"]` and gets FINDR's half-modified data. Subtle corruption with no error raised.

**Why dangerous:** Non-deterministic data corruption that only surfaces under specific timing. Impossible to reproduce reliably in tests.

```python
import copy

async def fan_out_agents(context: dict, agents: list[Agent]) -> list[AgentResult]:
    # CRITICAL: Each agent gets an IMMUTABLE SNAPSHOT, not a mutable reference
    tasks = {
        agent.name: asyncio.create_task(
            with_timeout(
                agent.run(copy.deepcopy(context)),  # Deep copy prevents cross-agent mutation
                agent.name,
                agent.timeout,
            )
        )
        for agent in agents
    }
    await asyncio.gather(*tasks.values(), return_exceptions=True)
    return {name: task.result() for name, task in tasks.items() if not task.exception()}
```

### EC-2.4 — Positional result mismatch in gather

**Scenario:** You iterate `zip(agent_names, results)` — if you later reorder the gather args, results silently misalign.

```python
# CORRECT — always name your results explicitly
agent_tasks = {
    "FINDR": asyncio.create_task(findr()),
    "TASKR": asyncio.create_task(taskr()),
    "CAMPA": asyncio.create_task(campa()),
}
await asyncio.gather(*agent_tasks.values(), return_exceptions=True)
agent_results = {
    name: task.result() if not task.exception() else task.exception()
    for name, task in agent_tasks.items()
}
```

---

## 2. Intent Routing

### EC-2.5 — "yes" / "no" messages with no context

**Scenario:** User asked MINDY to draft a campaign. MINDY responds with a draft and asks "Shall I save this?". User replies "yes". Keyword router sees no keywords → Haiku classifier → `unknown_intent` (confidence 0.3). Clarification loop triggers — infuriating the user.

```python
class ConversationState(BaseModel):
    pending_confirmation: str | None = None
    last_intent: IntentEnum | None = None

async def route_intent(message: str, state: ConversationState) -> RoutedIntent:
    msg_lower = message.strip().lower()

    # FIRST: Check for confirmation responses in context
    if state.pending_confirmation and msg_lower in {"yes", "no", "y", "n", "ok", "sure", "cancel"}:
        affirmative = msg_lower in {"yes", "y", "ok", "sure"}
        return RoutedIntent(
            intent=IntentEnum.CONFIRM if affirmative else IntentEnum.CANCEL,
            confidence=1.0,
            context=state.pending_confirmation
        )

    # Then: keyword regex tier
    # Then: LLM classifier tier
```

### EC-2.6 — Multi-intent messages

**Scenario:** `"Search for Acme's Q4 budget and create a follow-up task for next Tuesday"` — this is FINDR + TASKR simultaneously. Router returns a single intent. FINDR runs. The task creation is silently dropped.

```python
async def classify_multi_intent(message: str, llm_client) -> list[RoutedIntent]:
    prompt = """Analyze this message and identify ALL intents present.
    Return JSON: {"intents": [{"intent": "...", "sub_message": "...", "confidence": 0.0}]}
    Valid intents: search_memory, create_task, draft_campaign, get_status, clarify
    Message: {message}"""

    response = await llm_call(prompt.format(message=message))
    parsed = safe_parse_llm_json(response)
    intents = [RoutedIntent(**i) for i in parsed.get("intents", [])]

    # If multiple high-confidence intents — fan out to multiple agents
    high_conf = [i for i in intents if i.confidence >= 0.75]
    return high_conf if high_conf else intents[:1]


# Alternative: Sequential processing with results array (better for dependent intents)
async def process_multi_intent_sequential(
    intents: list[RoutedIntent], context: dict
) -> list[AgentResult]:
    """Process intents sequentially when later intents may depend on earlier results."""
    results = []
    for intent in intents:
        agent = get_agent_for_intent(intent.intent)
        result = await agent.run(context, sub_message=intent.sub_message)
        results.append(result)
        # Feed result into context for next intent (e.g., search then create task from results)
        context = {**context, f"prev_{intent.intent.value}_result": result}
    return results
```

### EC-2.7 — LLM classifier returning invalid intent label

**Scenario:** Haiku returns `{"intent": "search_memories"}` but your enum is `SEARCH_MEMORY` (no trailing 's'). `IntentEnum("search_memories")` raises `ValueError`.

```python
INTENT_ALIASES = {
    "search_memories": "search_memory",
    "create_tasks": "create_task",
    "draft_campaigns": "draft_campaign",
    "search": "search_memory",
    "task": "create_task",
}

@field_validator('intent', mode='before')
@classmethod
def normalize_intent(cls, v: str) -> str:
    normalized = v.lower().strip().replace(' ', '_').replace('-', '_')
    return INTENT_ALIASES.get(normalized, normalized)
```

---

## 3. LLM Response Edge Cases

### EC-2.8 — Empty content array from Claude

**Scenario:** Claude returns `response.content = []` (safety refusal or network truncation). Code does `response.content[0].text` → `IndexError`.

```python
def extract_text_from_claude(response) -> str:
    if not response.content:
        raise LLMEmptyResponseError(
            f"Claude returned empty content, stop_reason={response.stop_reason}"
        )
    text_blocks = [b.text for b in response.content if b.type == "text"]
    if not text_blocks:
        tool_blocks = [b for b in response.content if b.type == "tool_use"]
        raise LLMNoTextBlockError(f"Only tool_use blocks: {[b.name for b in tool_blocks]}")
    return "\n".join(text_blocks)
```

### EC-2.8a — Claude returning multiple content blocks (text + tool_use mixed)

**Scenario:** Claude returns `response.content` with mixed block types: `[TextBlock, ToolUseBlock, TextBlock]`. Code assumes only one text block and does `response.content[0].text` — misses the second text block and ignores the tool call entirely.

**Why dangerous:** Lost tool calls mean agents never execute requested actions. Lost text blocks mean incomplete responses.

```python
def extract_all_blocks(response) -> tuple[str, list[dict]]:
    """Iterate ALL content blocks — never assume a single block."""
    text_parts = []
    tool_calls = []

    for block in response.content:
        match block.type:
            case "text":
                text_parts.append(block.text)
            case "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })
            case _:
                logger.warning("unknown_content_block_type", block_type=block.type)

    return "\n".join(text_parts), tool_calls
```

### EC-2.9 — `stop_reason: "max_tokens"` with mid-JSON truncation

**Scenario:** Claude hits `max_tokens` mid-JSON. Response: `{"memories": [{"id": "abc` — `json.loads()` throws `JSONDecodeError`.

```python
def safe_parse_llm_json(response) -> dict:
    if response.stop_reason == "max_tokens":
        raise LLMTruncatedResponseError(
            f"Response truncated at max_tokens. "
            f"Increase max_tokens or reduce prompt size. "
            f"Partial: {response.content[0].text[:200] if response.content else 'empty'}"
        )

    raw = extract_text_from_claude(response)

    # Strip markdown fences (```json ... ```) — thorough version
    raw = strip_markdown_fences(raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise LLMMalformedJSONError(f"JSON parse failed: {e}. Raw: {raw[:500]}")


def strip_markdown_fences(text: str) -> str:
    """Remove all markdown code fences wrapping JSON. Handles nested and multiline."""
    text = text.strip()
    # Remove opening fence: ```json or ``` at start of string
    text = re.sub(r'^```(?:json|JSON)?\s*\n?', '', text)
    # Remove closing fence: ``` at end of string
    text = re.sub(r'\n?\s*```\s*$', '', text)
    return text.strip()
```

### EC-2.10 — Gemini fallback returns different response structure

**Scenario:** Claude returns `response.content[0].text`. Gemini returns `response.candidates[0].content.parts[0].text`. Fallback passes Gemini response to same parser → `AttributeError`.

```python
class LLMResponse(BaseModel):
    text: str
    stop_reason: str
    model: str

def normalize_claude_response(resp) -> LLMResponse:
    return LLMResponse(
        text=extract_text_from_claude(resp),
        stop_reason=resp.stop_reason,
        model=resp.model,
    )

def normalize_gemini_response(resp) -> LLMResponse:
    candidate = resp.candidates[0]
    stop = candidate.finish_reason.name  # STOP, MAX_TOKENS, SAFETY
    text = candidate.content.parts[0].text if candidate.content.parts else ""
    return LLMResponse(
        text=text,
        stop_reason="max_tokens" if stop == "MAX_TOKENS" else "end_turn",
        model="gemini",
    )
```

### EC-2.11 — LLM hallucinating extra/missing JSON keys

**Scenario:** You ask for `{"intent": str, "confidence": float}`. Claude returns `{"intent": str, "confidence": float, "reasoning": "..."}`. With `extra='forbid'` → `ValidationError`. With `extra='ignore'` → silent discard.

```python
class IntentClassification(BaseModel):
    model_config = ConfigDict(extra='ignore')  # Tolerate LLM verbosity
    intent: IntentEnum
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator('intent', mode='before')
    @classmethod
    def normalize_intent(cls, v):
        if isinstance(v, str):
            normalized = v.lower().replace(' ', '_').replace('-', '_')
            try:
                return IntentEnum(normalized)
            except ValueError:
                raise ValueError(f"Unknown intent: {v!r}. Valid: {[e.value for e in IntentEnum]}")
        return v

# IMPORTANT: Do NOT use pydantic discriminated unions for LLM output parsing.
# LLMs don't reliably produce the exact discriminator field values needed.
# Instead, use manual dispatch after parsing into a generic model:
#
#   parsed = IntentClassification.model_validate(llm_json)
#   match parsed.intent:
#       case IntentEnum.SEARCH_MEMORY: return handle_search(parsed)
#       case IntentEnum.CREATE_TASK: return handle_task(parsed)
#       case _: return handle_unknown(parsed)
```

---

## 4. Supermemory Edge Cases

### EC-2.12 — Search returning 0 results (empty context)

**Scenario:** FINDR searches for `"Q4 campaign budget"`. No matches. Prompt template does `context = results[0]["content"]` → `IndexError`. Even guarded, sending empty context produces hallucinated "memories."

```python
async def search_memories(query: str, mode: str = "hybrid") -> str:
    results = await supermemory_client.search(query=query, mode=mode)

    if not results or len(results) == 0:
        return "No relevant memories found for this query."

    MIN_SCORE = 0.65
    relevant = [r for r in results if r.get("score", 0) >= MIN_SCORE]
    if not relevant:
        return f"No memories above relevance threshold ({MIN_SCORE}) for: {query}"

    return "\n\n".join(
        f"[Memory {i+1} | score={r['score']:.2f} | as_of={r.get('metadata',{}).get('as_of','unknown')}]\n{r['content']}"
        for i, r in enumerate(relevant)
    )
```

### EC-2.13 — Network timeout during write — did it persist?

**Scenario:** MINDY writes a memory. Supermemory receives it, but response takes >30s. Your client times out. Did the write succeed? You retry → duplicate memory with same `customId`.

```python
async def write_memory_idempotent(client, content: str, custom_id: str, metadata: dict) -> str:
    for attempt in range(3):
        try:
            result = await client.add(
                content=content,
                customId=custom_id,
                metadata=metadata,
                timeout=aiohttp.ClientTimeout(total=45)
            )
            return result["id"]
        except asyncio.TimeoutError:
            # Check if write actually succeeded before retrying
            existing = await client.search(filters={"customId": custom_id}, limit=1)
            if existing:
                logger.warning("memory_write_timeout_but_succeeded", custom_id=custom_id)
                return existing[0]["id"]
            if attempt == 2:
                raise
            await asyncio.sleep(2 ** attempt)
```

### EC-2.14 — Filter syntax error silently returns wrong results

**Scenario:** You pass `filters={"metadata.source_authority": "crm"}` but API expects `{"source_authority": "crm"}`. API ignores the unknown filter and returns **all** memories unfiltered.

```python
class SupermemoryFilter(BaseModel):
    model_config = ConfigDict(extra='forbid')  # Catches typos
    source_authority: str | None = None
    as_of_gte: str | None = None
    as_of_lte: str | None = None
    memory_type: str | None = None

async def search_with_validation(query: str, filter: SupermemoryFilter):
    filter_dict = {k: v for k, v in filter.model_dump().items() if v is not None}
    results = await client.search(query=query, filters=filter_dict)
    if len(results) > 100 and filter_dict:
        logger.warning("supermemory_filter_possible_miss",
                       filter=filter_dict, result_count=len(results))
    return results
```

### EC-2.15 — `customId` collision in dedupe

**Scenario:** Two different memories generate the same `customId` from truncated hashes. Writing memory B overwrites memory A silently.

```python
import hashlib, uuid

def generate_memory_custom_id(user_id: str, client_id: str, content: str, memory_type: str) -> str:
    namespace = f"{user_id}:{client_id}:{memory_type}"
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{namespace}:{content_hash}"))
```

### EC-2.15a — Supermemory rate limiting

**Scenario:** Multiple agents fan-out simultaneously, each making 2-3 Supermemory calls. 6-9 concurrent API calls hit Supermemory's rate limit. All return `429 Too Many Requests`. Every agent fails.

**Why dangerous:** Fan-out amplifies rate limit risk. Without client-side throttling, burst traffic patterns will reliably trigger 429s.

```python
import asyncio

class RateLimitedClient:
    """Wrap Supermemory client with semaphore-based rate limiting."""

    def __init__(self, client, max_concurrent: int = 5):
        self._client = client
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def search(self, **kwargs):
        async with self._semaphore:
            for attempt in range(3):
                try:
                    return await self._client.search(**kwargs)
                except APIError as e:
                    if e.status == 429:
                        retry_after = int(e.headers.get("retry-after", 2 ** attempt))
                        logger.warning("supermemory_rate_limited", retry_after=retry_after)
                        await asyncio.sleep(retry_after)
                    else:
                        raise
            raise RateLimitExceededError("Supermemory rate limit after 3 retries")

    async def add(self, **kwargs):
        async with self._semaphore:
            return await self._client.add(**kwargs)


# Usage at startup:
raw_client = AsyncSupermemory(api_key=key, session=session)
supermemory = RateLimitedClient(raw_client, max_concurrent=5)
```

---

## 5. Conflict Resolution Edge Cases

### EC-2.16 — Perfect tie (identical `as_of`, `confidence`, `source_authority`)

**Scenario:** Two memories have identical sort keys. Python's sort is stable but non-deterministic across restarts.

```python
import hashlib

def conflict_sort_key(memory: dict) -> tuple:
    # Deterministic tiebreaker: hash of the memory ID
    id_hash = int(hashlib.md5(memory["id"].encode()).hexdigest(), 16)
    return (
        memory.get("as_of", ""),
        memory.get("confidence", 0.0),
        memory.get("source_authority", ""),
        id_hash,  # Deterministic tiebreak
    )
```

### EC-2.17 — Conflict group with only 1 item

**Scenario:** Group with 1 item is not a conflict — but resolver still calls `resolve_conflict(group)` → `IndexError`.

```python
def resolve_conflicts(groups: list[list[dict]]) -> list[dict]:
    resolved = []
    for group in groups:
        if len(group) <= 1:
            if group:
                resolved.append(group[0])
            continue
        winner = sorted(group, key=conflict_sort_key, reverse=True)[0]
        resolved.append(winner)
    return resolved
```

### EC-2.18 — Race condition: two concurrent approve/reject on same conflict

**Scenario:** Two users simultaneously click "Approve" on the same conflict card.

```python
async def approve_conflict(conflict_id: str, approved_memory_id: str, user_id: str):
    # SELECT FOR UPDATE provides row-level locking — no external lock needed
    async with pool.acquire() as conn:
        async with conn.transaction():
            conflict = await conn.fetchrow(
                "SELECT status, resolved_by FROM conflict_queue WHERE id=$1 FOR UPDATE",
                conflict_id
            )
            if conflict is None:
                raise ConflictNotFoundError(f"Conflict {conflict_id} no longer exists")
            if conflict["status"] != "pending":
                logger.info("conflict_already_resolved", resolved_by=conflict["resolved_by"])
                return  # Idempotent

            await supermemory_client.set_canonical(approved_memory_id)
            await conn.execute(
                "UPDATE conflict_queue SET status='resolved', resolved_by=$1, resolved_at=NOW() WHERE id=$2",
                user_id, conflict_id
            )
```

### EC-2.19 — Conflict resolution during concurrent memory write

**Scenario:** Resolver reads M1 and M2, determines M1 wins. Simultaneously, M3 is written with higher confidence. Resolver commits — M3 was never evaluated.

```python
async def resolve_and_write(conflict_group: list[dict]):
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Use PostgreSQL sequence for atomic generation counter
            snapshot_gen = await conn.fetchval("SELECT nextval('memory_write_generation_seq')")
            winner = sorted(conflict_group, key=conflict_sort_key, reverse=True)[0]

            current_gen = await conn.fetchval("SELECT last_value FROM memory_write_generation_seq")
            if current_gen != snapshot_gen:
                logger.warning("conflict_resolution_invalidated_by_concurrent_write")
                return await rerun_conflict_detection(winner["group_id"])

            await commit_resolution(winner)
```

---

## 6. PostgreSQL (asyncpg) Edge Cases

### EC-2.20 — Connection pool exhaustion

**Scenario:** 40 concurrent Teams messages. Each holds a DB connection for 5–20s. Pool size is 20. The 21st waits forever.

```python
pool = await asyncpg.create_pool(
    dsn,
    min_size=5,
    max_size=20,
    command_timeout=30,
    timeout=10,  # Fail fast on pool exhaustion
)

async def db_fetch(query: str, *args):
    try:
        async with pool.acquire(timeout=10) as conn:
            return await conn.fetch(query, *args)
    except asyncpg.exceptions.TooManyConnectionsError:
        raise ServiceUnavailableError("Database pool exhausted")
    except asyncio.TimeoutError:
        raise ServiceUnavailableError("Database pool acquire timeout")
```

### EC-2.21 — Transaction deadlocks between concurrent agent DB writes

**Scenario:** TASKR writes to `tasks` then `projects`. CAMPA writes to `projects` then `tasks`. Deadlock detected → one transaction killed.

```python
MAX_DEADLOCK_RETRIES = 3

async def execute_with_deadlock_retry(pool, tx_coroutine, *args):
    for attempt in range(MAX_DEADLOCK_RETRIES):
        try:
            async with pool.acquire() as conn:
                async with conn.transaction():
                    return await tx_coroutine(conn, *args)
        except asyncpg.exceptions.DeadlockDetectedError:
            if attempt == MAX_DEADLOCK_RETRIES - 1:
                raise
            wait = 0.1 * (2 ** attempt)
            logger.warning("deadlock_detected_retrying", attempt=attempt)
            await asyncio.sleep(wait)

# Prevention: always acquire locks in consistent alphabetical table order
```

### EC-2.22 — NULL in aggregations swallowing data

**Scenario:** `SELECT AVG(confidence) FROM memories WHERE client_id=$1` returns `NULL` if all rows have `confidence IS NULL`. `float(result["avg"])` → `TypeError`.

```python
row = await conn.fetchrow(
    "SELECT COALESCE(AVG(confidence), 0.0) AS avg_conf, COUNT(*) AS total "
    "FROM memories WHERE client_id=$1",
    client_id
)
```

### EC-2.22a — Connection drops during long queries (Azure LB idle timeout)

**Scenario:** A complex aggregation query runs for >4 minutes. Azure's load balancer has a 4-minute idle TCP timeout. The LB silently drops the connection. asyncpg waits forever for a response that will never arrive.

**Why dangerous:** Query appears to hang indefinitely. No timeout error is raised because the TCP connection was RST'd silently.

```python
# FIX: Set TCP keepalives at the PostgreSQL server level
# In postgresql.conf (or Azure Flexible Server params):
#   tcp_keepalives_idle = 120      # Start keepalive probes after 120s idle
#   tcp_keepalives_interval = 30   # Probe every 30s
#   tcp_keepalives_count = 3       # Give up after 3 failed probes

# Also set command_timeout on the pool to catch runaway queries:
pool = await asyncpg.create_pool(
    dsn,
    command_timeout=120,  # Hard kill after 2 minutes
    server_settings={
        "tcp_keepalives_idle": "120",
        "tcp_keepalives_interval": "30",
        "tcp_keepalives_count": "3",
    },
)
```

### EC-2.22b — SERIAL overflow on high-volume tables

**Scenario:** `agent_runs` table uses `SERIAL` (32-bit integer, max 2,147,483,647). At 100 agent runs/minute = ~4 million/month. With gaps from failed transactions, you hit overflow in ~1.5 years. PostgreSQL throws `integer out of range`.

**Why dangerous:** Production crash with no warning. Alembic migration to change column type requires full table rewrite and downtime.

```sql
-- ALWAYS use BIGSERIAL from day one for any auto-increment column
CREATE TABLE agent_runs (
    id BIGSERIAL PRIMARY KEY,  -- NOT SERIAL
    agent_name TEXT NOT NULL,
    started_at TIMESTAMPTZ DEFAULT NOW()
);

-- If you already have SERIAL, migrate early:
-- ALTER TABLE agent_runs ALTER COLUMN id TYPE BIGINT;
```

### EC-2.22c — Unicode encoding from Teams messages

**Scenario:** Teams user pastes emoji or non-Latin characters: `"Find the 📊 report for Müller GmbH"`. Raw string interpolation into SQL: `f"SELECT * FROM memories WHERE content LIKE '%{query}%'"` → SQL injection AND encoding errors.

**Why dangerous:** SQL injection via crafted Unicode. Even without injection, raw interpolation breaks on multi-byte characters.

```python
# ALWAYS use parameterized queries — never f-string SQL
# asyncpg handles encoding automatically with parameterized queries

# WRONG
await conn.fetch(f"SELECT * FROM memories WHERE content LIKE '%{query}%'")

# CORRECT
await conn.fetch(
    "SELECT * FROM memories WHERE content ILIKE $1",
    f"%{query}%"
)
```

---

## 7. Pydantic Validation Edge Cases

### EC-2.23 — `None` vs missing key behavior

**Scenario:** LLM returns `{"intent": "search_memory"}` (no `confidence` key). Model has `confidence: float | None = None`. Code does `if result.confidence > 0.5` → `TypeError: '>' not supported between NoneType and float`.

```python
class IntentResult(BaseModel):
    intent: IntentEnum
    confidence: float = 0.0  # Default 0.0, not None — safer for comparisons

    @property
    def is_high_confidence(self) -> bool:
        return (self.confidence or 0.0) >= 0.75
```

### EC-2.24 — `datetime` serialization format mismatch

**Scenario:** asyncpg returns `datetime` objects. Pydantic serializes as `"2025-03-21T15:00:00"` (no timezone). Supermemory expects `"2025-03-21T15:00:00Z"` (UTC suffix). Filters return 0 results.

```python
from datetime import datetime, timezone
from pydantic import field_serializer

class MemoryMetadata(BaseModel):
    as_of: datetime

    @field_serializer('as_of')
    def serialize_as_of(self, dt: datetime) -> str:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
```

### EC-2.25 — Nested validation errors losing field path

**Scenario:** `ValidationError` on nested model shows `agents.0.skills.2.config.timeout` but `str(e)` truncates. Production logs are useless.

```python
def log_validation_error(e: ValidationError, model_name: str):
    for error in e.errors():
        structlog.get_logger().error(
            "pydantic_validation_error",
            model=model_name,
            field_path=".".join(str(loc) for loc in error["loc"]),
            error_type=error["type"],
            message=error["msg"],
            input_value=str(error.get("input", ""))[:200],
        )
```

---

## Quick Reference

| # | Failure | Trigger | Fix |
|---|---------|---------|-----|
| 2.1 | All results dropped | 1 agent timeout | Per-agent `wait_for` wrapper |
| 2.2 | 500 on all-fail | All agents down | Graceful degradation message |
| 2.3 | Context race | 2 rapid messages | Per-user asyncio lock / PG advisory lock |
| 2.5 | "yes" misrouted | Confirmation without context | Check `pending_confirmation` first |
| 2.6 | Intent silently dropped | Multi-intent message | Multi-intent classifier |
| 2.8 | IndexError | Empty Claude content | Check `response.content` length |
| 2.9 | JSONDecodeError | `max_tokens` truncation | Check `stop_reason` before parsing |
| 2.12 | Hallucinated memories | Empty Supermemory results | Explicit "no results" message |
| 2.13 | Duplicate writes | Write timeout + retry | Search-before-retry on `customId` |
| 2.16 | Non-deterministic winner | Perfect tie in conflict | Hash-based tiebreaker |
| 2.18 | Double-approve | Concurrent conflict actions | `SELECT FOR UPDATE` in transaction |
| 2.20 | Hang under load | Pool exhaustion | `timeout=10` on acquire |
| 2.22a | Query hangs forever | Azure LB 4-min idle TCP | `tcp_keepalives_idle` server setting |
| 2.22b | Integer overflow crash | SERIAL max exceeded | Use BIGSERIAL from day one |
| 2.22c | SQL injection / encoding | Unicode from Teams | Always use parameterized queries |
| 2.23 | TypeError on None | Missing JSON key from LLM | Default `0.0` not `None` |
| 2.4a | Cross-agent data corruption | Shared mutable context | `copy.deepcopy(context)` per agent |
| 2.8a | Lost tool calls / text | Mixed content blocks | Iterate ALL blocks with match/case |
| 2.15a | All agents 429'd | Burst Supermemory calls | Semaphore-based `RateLimitedClient` |
