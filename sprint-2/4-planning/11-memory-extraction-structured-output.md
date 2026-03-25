# Topic: Memory Extraction — Structured Output from Claude

**Time:** 20-30 min
**Goal:** After LLM responds, extract new facts/memories using a second LLM call

---

## What to Search
- "Claude tool_use structured output Python"
- "anthropic SDK structured output"
- "pydantic model from LLM response"
- "Claude JSON mode Python"

## What It Does
After Claude generates a response to the user, a SECOND LLM call extracts any new facts mentioned. These get written to Supermemory.

## POC Contract
```json
{
  "shouldWrite": true,
  "items": [
    {
      "content": "Acme Q1 budget confirmed as $50K",
      "metadata": {
        "memory_type": "fact",
        "source_type": "chat",
        "confidence": 0.90,
        "as_of": "2026-03-21"
      }
    }
  ]
}
```

## Option A: Claude tool_use (RECOMMENDED)
```python
import anthropic

client = anthropic.AsyncAnthropic()

tools = [{
    "name": "extract_memories",
    "description": "Extract new facts/memories from the conversation",
    "input_schema": {
        "type": "object",
        "properties": {
            "should_write": {"type": "boolean", "description": "Whether new memories were found"},
            "items": {
                "type": "array",
                "maxItems": 2,
                "items": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "memory_type": {"type": "string", "enum": ["fact", "rule"]},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    },
                    "required": ["content", "memory_type", "confidence"]
                }
            }
        },
        "required": ["should_write", "items"]
    }
}]

response = await client.messages.create(
    model="claude-sonnet-4-5-20250514",
    max_tokens=500,
    tools=tools,
    tool_choice={"type": "tool", "name": "extract_memories"},
    messages=[{
        "role": "user",
        "content": f"Extract new facts from this conversation:\nUser: {user_text}\nAssistant: {assistant_reply}"
    }]
)

# Parse tool use result
tool_use = next(b for b in response.content if b.type == "tool_use")
extraction = tool_use.input  # Already parsed JSON
```

## Option B: Raw JSON output
```python
response = await client.messages.create(
    model="claude-sonnet-4-5-20250514",
    max_tokens=500,
    messages=[{
        "role": "user",
        "content": f"""Extract new facts. Return ONLY JSON:
{{"should_write": bool, "items": [{{"content": "...", "memory_type": "fact|rule", "confidence": 0.0-1.0}}]}}
Max 2 items. If no new facts, should_write=false.

Conversation:
User: {user_text}
Assistant: {assistant_reply}"""
    }]
)
extraction = json.loads(response.content[0].text)
```

## Mode-Dependent Write Suppression
```python
READ_ONLY_MODES = {"search", "review"}

if mode in READ_ONLY_MODES:
    extraction["should_write"] = False  # Force off
```

## What to Understand
- [ ] tool_use gives you guaranteed structured output (no JSON parsing errors)
- [ ] `tool_choice: {"type": "tool", "name": "..."}` forces the tool to be called
- [ ] Max 2 items per extraction (POC limit)
- [ ] search/review modes force `should_write = false`
- [ ] This is a SEPARATE LLM call from the main response generation
