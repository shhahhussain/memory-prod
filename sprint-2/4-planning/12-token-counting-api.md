# Topic: Claude Token Counting API

**Time:** 15 min
**Goal:** Replace POC's char-based budgeting with real token counting

---

## What to Search
- "Claude token counting API Python"
- "anthropic beta messages count_tokens"
- "Claude context window management"

## POC Problem
POC used: `MAX_TOTAL_CHARS = 8000`, `MAX_CHUNKS = 8`. This is a rough estimate. Real token counting is more accurate.

## Code Pattern
```python
import anthropic

client = anthropic.AsyncAnthropic()

async def count_tokens(messages: list[dict], system: str) -> int:
    response = await client.beta.messages.count_tokens(
        model="claude-sonnet-4-5-20250514",
        system=system,
        messages=messages,
    )
    return response.input_tokens

# Usage
token_count = await count_tokens(conversation_messages, system_prompt)

SUMMARIZE_THRESHOLD = 0.75
MAX_TOKENS = 100_000  # Claude Sonnet context window

if token_count > SUMMARIZE_THRESHOLD * MAX_TOKENS:
    # Need to summarize old messages
    messages = await rolling_summarize(messages)
```

## What to Understand
- [ ] `client.beta.messages.count_tokens()` — exact token count without making an LLM call
- [ ] It's in `beta` namespace (may move to stable later)
- [ ] Use 75% threshold to trigger summarization (leave room for response)
- [ ] Claude Sonnet has 200K context window but 100K is practical limit
- [ ] This replaces POC's `MAX_TOTAL_CHARS = 8000`
