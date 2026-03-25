# Topic: Rolling Summarization for Context Window

**Time:** 15-20 min
**Goal:** When conversation gets too long, summarize old messages to free up token space

---

## What to Search
- "rolling summarization conversation history LLM"
- "conversation context compression LLM"
- "sliding window summarization chat"

## When This Fires
When `count_tokens()` > 75% of max context → summarize oldest messages.

## Code Pattern
```python
async def rolling_summarize(messages: list[dict], keep_recent: int = 5) -> list[dict]:
    """Keep last N messages verbatim, summarize everything before."""
    if len(messages) <= keep_recent:
        return messages

    old_messages = messages[:-keep_recent]
    recent_messages = messages[-keep_recent:]

    # Summarize old messages with cheap/fast model
    summary_response = await gemini_flash.generate(
        f"Summarize this conversation history in 2-3 sentences, preserving key facts and decisions:\n\n"
        + "\n".join(f"{m['role']}: {m['content']}" for m in old_messages),
        max_tokens=200,
    )

    # Replace old messages with summary
    summary_message = {
        "role": "user",
        "content": f"[Previous conversation summary: {summary_response.text}]"
    }

    return [summary_message] + recent_messages
```

## What to Understand
- [ ] Keep last 5 messages verbatim (recent context matters most)
- [ ] Summarize everything older into 2-3 sentences
- [ ] Use CHEAP model for summarization (Gemini Flash, not Claude Sonnet)
- [ ] Summary goes as first message in the new context
- [ ] POC had fixed 8-message window — this is smarter
