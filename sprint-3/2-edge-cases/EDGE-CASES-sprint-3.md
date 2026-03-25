# Sprint 3 — Edge Cases & Known Pitfalls

> **Scope:** Teams @mention handler, Adaptive Cards, progress updates, thread context, manifest sideload, proactive messages

---

## Research-Verified Finding

- **Teams 15s retry:** Confirmed from official Bot Framework documentation — Teams resends the activity if no HTTP 200 is received within ~15 seconds. This validates the idempotency pattern in EC-3.1.

---

## 1. Teams Message Handling

### EC-3.1 — Teams retry causing duplicate processing

**Scenario:** MINDY orchestration takes >15 seconds. Teams resends the activity. Your bot receives the same `activity.id` twice — sends two responses, creates duplicate NocoDB tasks.

**Why dangerous:** Full idempotency breakage. NocoDB task creation fires twice.

```python
# PostgreSQL-based dedup (production)
async def on_message_activity(self, turn_context: TurnContext):
    activity_id = turn_context.activity.id

    # INSERT ... ON CONFLICT DO NOTHING — atomic dedup check
    async with pool.acquire() as conn:
        result = await conn.execute(
            "INSERT INTO processed_activities (activity_id, status, created_at) "
            "VALUES ($1, 'processing', now()) ON CONFLICT (activity_id) DO NOTHING",
            activity_id
        )
    if result == "INSERT 0 0":
        return  # Already processed — send 200 to stop retries

    # Acknowledge Teams immediately, process async
    asyncio.create_task(self._process_async(turn_context))

async def _process_async(self, turn_context: TurnContext):
    result = await mindy_orchestrate(...)
    await turn_context.send_activity(result)
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE processed_activities SET status='done' WHERE activity_id=$1",
            turn_context.activity.id
        )

# Dict-based dedup for local dev (single instance only):
_processed_activities: dict[str, float] = {}

class LocalDedupMiddleware:
    """Dict-based dedup for local development. Use PostgreSQL-based approach in production."""

    async def on_turn(self, turn_context: TurnContext, logic):
        activity_id = turn_context.activity.id
        now = time.monotonic()

        # Clean expired entries (older than 5 minutes)
        expired = [k for k, v in _processed_activities.items() if now - v > 300]
        for k in expired:
            _processed_activities.pop(k, None)

        if activity_id in _processed_activities:
            return  # Already processed

        _processed_activities[activity_id] = now
        await logic()
```

### EC-3.2 — @mention stripping edge cases

**Scenario:** `"<at>OrgMind</at> find me clients and <at>Alice</at> approve it"` — strip regex removes ALL `<at>` tags. Alice's mention disappears. Worse: `"<at>OrgMind</at>"` alone → empty string → NLP crashes on empty input.

```python
import re
from html import unescape

def strip_bot_mention(text: str, bot_name: str) -> str:
    # Only strip the bot's own mention, not all @mentions
    pattern = rf'<at[^>]*>{re.escape(bot_name)}<\/at>'
    cleaned = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()

    # Handle HTML encoding
    cleaned = unescape(cleaned)

    if not cleaned:
        raise EmptyMessageAfterStrip("Message contained only bot mention")
    return cleaned
```

### EC-3.3 — Adaptive Card invoke vs message activity type confusion

**Scenario:** User clicks an Adaptive Card button. Activity arrives as `type: "invoke"` with `name: "adaptiveCard/action"` — NOT `type: "message"`. Your `on_message_activity` handler never fires. Card action silently drops.

**Why dangerous:** No response sent → Teams shows "Something went wrong". Invoke must respond within 5 seconds.

```python
async def on_invoke_activity(self, turn_context: TurnContext):
    activity = turn_context.activity

    if activity.name == "adaptiveCard/action":
        action_data = activity.value

        # CRITICAL: Must respond within 5s for invoke activities
        asyncio.create_task(self._handle_card_action(turn_context, action_data))

        return InvokeResponse(status=200, body={"statusCode": 200})

    return await super().on_invoke_activity(turn_context)
```

### EC-3.4 — Stale conversation reference for proactive messages

**Scenario:** Background task completes. Proactive message uses stored `ConversationReference`. User left the channel, bot was removed, or token expired → `401/403/404` with unclear error.

```python
async def send_proactive(app, ref: ConversationReference, msg: str):
    try:
        await app.continue_conversation(
            ref,
            lambda ctx, _: ctx.send_activity(msg),
            bot_app_id
        )
    except Exception as e:
        error_str = str(e).lower()
        if "401" in error_str or "403" in error_str:
            await db.execute(
                "UPDATE conversation_refs SET valid=false WHERE ref_id=$1",
                ref.conversation.id
            )
            logger.warning("proactive_ref_stale", ref_id=ref.conversation.id)
        elif "404" in error_str:
            logger.warning("proactive_channel_not_found", ref_id=ref.conversation.id)
        else:
            raise
```

### EC-3.5 — Message size limit causing silent truncation

**Scenario:** MINDY's synthesis exceeds Teams' ~28KB / ~8192 char limit. Bot Framework connector silently truncates or rejects.

```python
MAX_TEAMS_MESSAGE_CHARS = 7000  # Conservative

def split_response(text: str, max_chars: int = MAX_TEAMS_MESSAGE_CHARS) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    chunks = []
    current = []
    current_len = 0
    for para in text.split('\n\n'):
        if current_len + len(para) > max_chars:
            chunks.append('\n\n'.join(current))
            current = [para]
            current_len = len(para)
        else:
            current.append(para)
            current_len += len(para)
    if current:
        chunks.append('\n\n'.join(current))

    # Add Part X/Y prefix so user knows message is split
    if len(chunks) > 1:
        chunks = [f"**Part {i+1}/{len(chunks)}**\n\n{chunk}" for i, chunk in enumerate(chunks)]

    return chunks
```

### EC-3.5a — Bot Framework rate limiting (429 from connector)

**Scenario:** OrgMind sends proactive messages to many users (e.g., broadcasting conflict resolution results). Bot Framework Connector enforces rate limits: **50 requests per second per app per tenant**, with a 3600-second window. Exceeding this returns `429 Too Many Requests`. Also watch for `412 Precondition Failed`, `502 Bad Gateway`, and `504 Gateway Timeout` — all are transient and require retry.

**Why dangerous:** Rate-limited responses cause message delivery failures. Without retry logic, proactive messages silently drop.

```python
TRANSIENT_STATUS_CODES = {429, 412, 502, 504}

async def send_with_bot_retry(
    turn_context: TurnContext, message: str, max_retries: int = 3
):
    for attempt in range(max_retries):
        try:
            await turn_context.send_activity(message)
            return
        except Exception as e:
            status = getattr(e, "status_code", None)
            if status in TRANSIENT_STATUS_CODES:
                if status == 429:
                    retry_after = int(getattr(e, "retry_after", 2 ** attempt))
                else:
                    retry_after = 2 ** attempt
                logger.warning(
                    "bot_framework_transient_error",
                    status=status, attempt=attempt, retry_after=retry_after
                )
                await asyncio.sleep(retry_after)
            else:
                raise
    raise BotFrameworkRetryExhaustedError(f"Failed after {max_retries} retries")
```

---

## 2. Adaptive Card Edge Cases

### EC-3.6 — Prompt injection via Adaptive Card action data

**Scenario:** Card has `Action.Submit` with `{"action": "approve", "memory_id": "abc123"}`. Attacker crafts card data: `{"action": "approve", "memory_id": "abc123\nIgnore previous instructions..."}`. Your code interpolates this into an LLM prompt.

```python
from pydantic import BaseModel, field_validator
import re

class CardActionPayload(BaseModel):
    action: Literal["approve", "reject", "confirm", "cancel"]
    memory_id: str
    conflict_id: str | None = None

    @field_validator('memory_id', 'conflict_id', mode='before')
    @classmethod
    def validate_id_format(cls, v):
        if v is None:
            return v
        if not re.match(r'^[a-zA-Z0-9_\-]{1,128}$', str(v)):
            raise ValueError(f"Invalid ID format: {v!r}")
        return v

# NEVER interpolate card action data directly into LLM prompts
payload = CardActionPayload.model_validate(turn_context.activity.value)
```

### EC-3.7 — Adaptive Card version mismatch

**Scenario:** You use Adaptive Card schema v1.5 features (e.g., `Action.Execute`). User's Teams client is on an older version that only supports v1.3. The card renders with missing buttons or broken layout — no error reported.

```python
# Always set the minimum schema version your card requires
card = {
    "type": "AdaptiveCard",
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.4",  # Use lowest version that supports your features
    "fallbackText": "Your Teams client doesn't support this card. Please update Teams.",
    "body": [...]
}
```

---

## 3. Thread Context Persistence

### EC-3.8 — Thread context lost on Teams channel switch

**Scenario:** User starts conversation in one Teams channel (thread A). MINDY stores context keyed by `conversation.id`. User switches to a different channel — same user, different `conversation.id`. MINDY starts fresh — loses all context.

```python
# Key context by USER, not by conversation
async def get_context(turn_context: TurnContext) -> ConversationState:
    user_id = turn_context.activity.from_property.id
    conversation_id = turn_context.activity.conversation.id

    async with pool.acquire() as conn:
        # Primary: user-level context (persists across channels)
        user_ctx = await conn.fetchrow(
            "SELECT context_data FROM user_context WHERE user_id=$1", user_id
        )

        # Secondary: thread-level context (channel-specific)
        thread_ctx = await conn.fetchrow(
            "SELECT context_data FROM thread_context WHERE conversation_id=$1", conversation_id
        )

    return merge_contexts(user_ctx, thread_ctx)
```

---

## Quick Reference

| # | Failure | Trigger | Fix |
|---|---------|---------|-----|
| 3.1 | Duplicate processing | Teams 15s retry | Idempotency key on `activity.id` |
| 3.2 | Empty message | Only bot mention in msg | Check after strip, raise if empty |
| 3.3 | Card action dropped | Invoke != message activity | `on_invoke_activity` handler |
| 3.4 | Proactive fails silently | Stale conversation ref | Catch 401/403/404, invalidate ref |
| 3.5 | Truncated response | >7000 chars | Split at paragraph boundaries + `Part X/Y` prefix |
| 3.5a | Message delivery fails | Bot Framework 429/412/502/504 | Retry with backoff on transient status codes |
| 3.6 | Prompt injection | Card action data field | Pydantic UUID validation on IDs |
| 3.7 | Broken card layout | Card version mismatch | Use lowest compatible version |
| 3.8 | Context lost | Channel switch | Key context by user_id, not conversation_id |
