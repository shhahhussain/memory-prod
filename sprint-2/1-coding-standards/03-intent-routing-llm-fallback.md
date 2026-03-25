# Intent Routing — LLM Fallback (Code-Ready Reference)

> For Claude Code: MINDY's Tier 2 LLM-based classification for ambiguous messages.

## Use Haiku (cheap + fast) — NOT Sonnet

```python
import json
from agent_framework.anthropic import AnthropicClient
from orgmind.routing.models import Intent, RoutingDecision

CLASSIFICATION_PROMPT = """Classify the user's message into ONE intent:
- search: find/retrieve information
- task: create/update/list tasks
- campaign: draft/edit documents
- write: save a specific fact
- clarify: too vague

Respond with ONLY JSON: {"intent": "...", "confidence": 0.0-1.0, "reasoning": "..."}"""

async def llm_classify(message: str) -> RoutingDecision:
    classifier = AnthropicClient(model_id="claude-haiku-4-5").as_agent(
        name="IntentClassifier", instructions=CLASSIFICATION_PROMPT,
    )
    result = await classifier.run(f"Classify: {message}")

    try:
        text = result.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1].strip()
            if text.startswith("json"):
                text = text[4:].strip()
        parsed = json.loads(text)
        intent = Intent(parsed["intent"])
        confidence = float(parsed["confidence"])
    except (json.JSONDecodeError, KeyError, ValueError):
        return RoutingDecision(intent=Intent.CLARIFY, confidence=0.3, agents=[], extracted_params={"original": message}, tier="llm")

    INTENT_TO_AGENTS = {Intent.SEARCH: ["FINDR"], Intent.TASK: ["TASKR"], Intent.CAMPAIGN: ["CAMPA"]}
    return RoutingDecision(
        intent=intent, confidence=confidence,
        agents=INTENT_TO_AGENTS.get(intent, []),
        extracted_params={"original": message, "reasoning": parsed.get("reasoning", "")},
        tier="llm",
    )
```

## Full Router Pipeline

```python
async def route_message(message: str) -> RoutingDecision:
    decision = keyword_route(message)  # Tier 1
    if decision:
        return decision
    decision = await llm_classify(message)  # Tier 2
    if decision.confidence >= 0.65:
        return decision
    return RoutingDecision(intent=Intent.CLARIFY, confidence=decision.confidence, agents=[], extracted_params={"original": message}, tier="clarify")
```

## IMPORTANT NOTES
1. Use Haiku not Sonnet — save cost for simple classification
2. Always validate JSON output — LLMs can return garbage
3. Confidence < 0.65 → ask user to clarify
4. Cache results — same message shouldn't be classified twice
