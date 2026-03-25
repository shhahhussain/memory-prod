# Token Counting (Code-Ready Reference)

> For Claude Code: Use for context window budgeting.

## Anthropic Token Counting

```python
import anthropic

client = anthropic.AsyncAnthropic()

# Count tokens for a message
response = await client.messages.count_tokens(
    model="claude-sonnet-4-5-20250929",
    messages=[{"role": "user", "content": "Your message here"}],
)
print(response.input_tokens)  # int
```

## Approximate Counting (No API Call)

For budgeting without API calls, use the ~4 chars per token rule:

```python
def approx_tokens(text: str) -> int:
    return len(text) // 4

def fits_in_context(texts: list[str], max_tokens: int = 100000) -> bool:
    total = sum(approx_tokens(t) for t in texts)
    return total < max_tokens
```

## tiktoken (For OpenAI models — reference only)

```python
# Only if you need exact counts for OpenAI models
# pip install tiktoken
import tiktoken
enc = tiktoken.encoding_for_model("gpt-4")
tokens = enc.encode("text")
count = len(tokens)
```

## Context Budget Pattern

```python
MAX_CONTEXT_TOKENS = 80000  # Leave headroom in 200K context

def budget_context_pack(memories: list[str], system_prompt: str, user_message: str) -> list[str]:
    budget = MAX_CONTEXT_TOKENS
    budget -= approx_tokens(system_prompt)
    budget -= approx_tokens(user_message)
    budget -= 2000  # Reserve for response

    selected = []
    used = 0
    for mem in memories:
        cost = approx_tokens(mem)
        if used + cost > budget:
            break
        selected.append(mem)
        used += cost

    return selected
```

## IMPORTANT NOTES
1. Anthropic has a native `count_tokens` API — use it for exact counts
2. For budgeting, `len(text) // 4` is a good approximation
3. Always leave headroom for the response (2000-4000 tokens)
4. Claude Sonnet context: 200K tokens input
