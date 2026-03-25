# Rolling Summarization (Code-Ready Reference)

> For Claude Code: Compress long conversations to fit context windows.

## When to Use

When conversation history exceeds context budget, summarize older messages and keep recent ones verbatim.

## Implementation

```python
from agent_framework.anthropic import AnthropicClient

SUMMARIZE_PROMPT = """Summarize this conversation into key facts and decisions.
Keep it concise — bullet points preferred. Preserve all specific data points, numbers, and action items."""

async def rolling_summarize(
    messages: list[dict],
    max_recent: int = 10,
    max_tokens: int = 80000,
) -> list[dict]:
    if approx_tokens(str(messages)) < max_tokens:
        return messages  # Fits — no summarization needed

    recent = messages[-max_recent:]
    older = messages[:-max_recent]

    if not older:
        return recent

    summarizer = AnthropicClient(model_id="claude-haiku-4-5").as_agent(
        name="Summarizer", instructions=SUMMARIZE_PROMPT,
    )

    older_text = "\n".join(f"{m.get('role', 'user')}: {m.get('content', '')}" for m in older)
    summary = await summarizer.run(older_text)

    return [
        {"role": "system", "content": f"[Conversation summary]\n{summary.text}"},
        *recent,
    ]
```

## IMPORTANT NOTES
1. Use Haiku for summarization — cheap
2. Keep last N messages verbatim, summarize older ones
3. Check token count BEFORE summarizing — skip if not needed
4. Preserve specific data points in summaries
