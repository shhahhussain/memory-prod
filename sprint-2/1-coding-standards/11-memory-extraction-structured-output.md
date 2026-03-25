# Memory Extraction — Structured Output (Code-Ready Reference)

> For Claude Code: Port the POC's `Chain - Extract Memories` LLM call.

## POC Behavior

After the response LLM generates a reply, a second LLM call extracts structured memories from the conversation.

## Implementation

```python
import json
from pydantic import BaseModel, Field
from agent_framework.anthropic import AnthropicClient

class ExtractedMemory(BaseModel):
    content: str
    memory_type: str = "fact"  # fact | rule
    confidence: float = Field(ge=0.0, le=1.0)
    entity_type: str = "fact"
    client: str = "general"
    department: str = "general"

class ExtractionResult(BaseModel):
    should_write: bool
    memories: list[ExtractedMemory] = []

EXTRACTION_PROMPT = """You are a memory extraction agent for OrgMind.

Given a user message and assistant response, extract discrete factual memories worth saving.

Rules:
- Only extract CONCRETE facts, not opinions or greetings
- Each memory should be a standalone, self-contained statement
- Set confidence based on how certain the fact is (0.0-1.0)
- Set memory_type: "fact" for data points, "rule" for business rules/policies
- If nothing worth saving, set should_write=false

Return ONLY JSON:
{
  "should_write": true/false,
  "memories": [
    {"content": "...", "memory_type": "fact", "confidence": 0.9, "entity_type": "fact", "client": "general", "department": "general"}
  ]
}"""

async def extract_memories(user_message: str, assistant_reply: str, mode: str) -> ExtractionResult:
    # Search/review mode → never write
    if mode in ("search", "review"):
        return ExtractionResult(should_write=False)

    # Write mode → force single write from user text
    if mode == "write":
        return ExtractionResult(
            should_write=True,
            memories=[ExtractedMemory(content=user_message, confidence=0.95)],
        )

    # Auto mode → LLM extraction
    extractor = AnthropicClient(model_id="claude-haiku-4-5").as_agent(
        name="MemoryExtractor", instructions=EXTRACTION_PROMPT,
    )

    prompt = f"User: {user_message}\nAssistant: {assistant_reply}"
    result = await extractor.run(prompt)

    try:
        text = result.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1].strip()
            if text.startswith("json"):
                text = text[4:].strip()
        return ExtractionResult.model_validate_json(text)
    except Exception:
        return ExtractionResult(should_write=False)
```

## IMPORTANT NOTES
1. Use Haiku for extraction — fast and cheap
2. Mode determines behavior: auto=extract, write=force, search/review=skip
3. Validate LLM output with Pydantic model
4. Maps directly to POC's `Code - Parse Extraction JSON` node
