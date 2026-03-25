# Topic: Intent Routing — LLM Classification Fallback (Tier 2)

**Time:** 20-30 min
**Goal:** Use a cheap LLM to classify ambiguous messages that keywords can't handle

---

## What to Search
- "Gemini Flash API Python classification"
- "LLM intent classification structured output"
- "cheap LLM classifier vs fine-tuned model"

## When This Fires
Only when keyword tier returns None (no keyword match).
Example: "Hey can you check if Acme's numbers make sense?" — no obvious keyword.

## POC Thresholds to Port
```python
READ_THRESHOLD = 0.75
REVIEW_THRESHOLD = 0.80
MUTATE_SUGGEST_THRESHOLD = 0.50
AUTO_WRITE_THRESHOLD = 0.70
CLARIFY_THRESHOLD = 0.65  # Below this → ask user
```

## Code Pattern
```python
from pydantic import BaseModel

class LLMClassification(BaseModel):
    intent: str
    confidence: float
    agent: str  # MINDY, FINDR, TASKR, CAMPA
    reasoning: str

async def llm_classify(text: str, last_topic: str, last_agent: str) -> LLMClassification:
    prompt = f"""Classify this message intent for an org intelligence system.
Recent topic: {last_topic}
Last agent: {last_agent}
Message: {text}

Return JSON: {{"intent": "<search|write|task|campaign|review|approve|reject>", "confidence": 0.0-1.0, "agent": "FINDR|TASKR|CAMPA", "reasoning": "..."}}"""

    # Use CHEAP model — Gemini Flash, not Claude Sonnet
    response = await gemini_flash.generate(prompt, max_tokens=100)
    return LLMClassification.model_validate_json(response.text)
```

## What to Understand
- [ ] Use Gemini Flash (cheap) not Claude Sonnet (expensive) for classification
- [ ] Always include conversation context (last_topic, last_agent) for follow-up detection
- [ ] If confidence < 0.65 → don't guess, ask the user to clarify
- [ ] Parse LLM output into Pydantic model for type safety
- [ ] This adds ~200-300ms latency (acceptable for ambiguous messages)
