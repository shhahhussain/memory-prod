# Intent Routing — Keyword Tier (Code-Ready Reference)

> For Claude Code: MINDY's Tier 1 fast-path intent classification.

## POC Behavior (from n8n)

Prefix-based: `write:` → write, `search:` → search, `review:` → review, `approve:` / `reject:` → approve/reject, default → `auto`

## Production Intent Model

```python
from enum import Enum
from pydantic import BaseModel

class Intent(str, Enum):
    SEARCH = "search"
    TASK = "task"
    CAMPAIGN = "campaign"
    WRITE = "write"
    REVIEW = "review"
    APPROVE = "approve"
    REJECT = "reject"
    HELP = "help"
    CLARIFY = "clarify"

class RoutingDecision(BaseModel):
    intent: Intent
    confidence: float
    agents: list[str]
    extracted_params: dict
    tier: str  # "keyword" | "llm" | "clarify"
```

## Keyword Router

```python
import re

KEYWORD_RULES: list[tuple[re.Pattern, Intent, list[str]]] = [
    # Explicit prefix commands (from POC)
    (re.compile(r"^write:\s*", re.I), Intent.WRITE, []),
    (re.compile(r"^search:\s*", re.I), Intent.SEARCH, ["FINDR"]),
    (re.compile(r"^review:\s*", re.I), Intent.REVIEW, ["FINDR"]),
    (re.compile(r"^approve:\s*", re.I), Intent.APPROVE, []),
    (re.compile(r"^reject:\s*", re.I), Intent.REJECT, []),
    (re.compile(r"^/?(help|commands)\b", re.I), Intent.HELP, []),
    # Task signals
    (re.compile(r"\b(create|add|assign|update|close)\s+(a\s+)?(task|ticket|todo)", re.I), Intent.TASK, ["TASKR"]),
    (re.compile(r"\b(my|open|pending)\s+(tasks|tickets|todos)", re.I), Intent.TASK, ["TASKR"]),
    # Campaign signals
    (re.compile(r"\b(draft|create|edit)\s+(a\s+)?(campaign|brief|doc|proposal)", re.I), Intent.CAMPAIGN, ["CAMPA"]),
    # Search signals (catch-all for questions)
    (re.compile(r"\b(what|who|when|where|how|why|tell me|find|look up)", re.I), Intent.SEARCH, ["FINDR"]),
]

def keyword_route(message: str) -> RoutingDecision | None:
    stripped = message.strip()
    for pattern, intent, agents in KEYWORD_RULES:
        match = pattern.search(stripped)
        if match:
            clean_text = pattern.sub("", stripped).strip()
            return RoutingDecision(
                intent=intent, confidence=0.95, agents=agents,
                extracted_params={"clean_text": clean_text}, tier="keyword",
            )
    return None  # Fall through to LLM tier
```

## IMPORTANT NOTES
1. Order of KEYWORD_RULES matters — first match wins
2. Prefix commands checked FIRST
3. Return `None` for ambiguous → LLM tier handles it
4. Maps to POC's `Set - Normalize Surface Payload` node
