# Topic: Intent Routing — Keyword/Regex Fast Path (Tier 1)

**Time:** 15-20 min
**Goal:** Build the cheap, free intent classifier that handles 60-70% of messages

---

## What to Search
- "keyword intent classifier Python"
- "regex intent routing chatbot"
- "fast intent classification without LLM"

## POC Behavior to Port
POC used hard prefixes: `search:`, `write:`, `review:`, `approve:`, `reject:`, `update:`
Prod needs natural language but keywords still work for obvious cases.

## Code Pattern
```python
from enum import Enum

class Intent(str, Enum):
    SEARCH = "search"
    WRITE = "write"
    TASK = "task"
    CAMPAIGN = "campaign"
    REVIEW = "review"
    APPROVE = "approve"
    REJECT = "reject"
    CONFLICT = "conflict"
    CLARIFY = "clarify"

KEYWORD_MAP = {
    Intent.SEARCH: ["find", "search", "what do we know", "look up", "research", "tell me about"],
    Intent.WRITE: ["remember", "save", "store", "write", "note that"],
    Intent.TASK: ["create task", "add task", "assign", "due date", "project task"],
    Intent.CAMPAIGN: ["campaign", "brief", "draft doc", "campaign brief"],
    Intent.APPROVE: ["approve", "yes go ahead", "looks good", "lgtm"],
    Intent.REJECT: ["reject", "don't send", "cancel", "no"],
    Intent.REVIEW: ["review", "show drafts", "pending", "what's waiting"],
}

def keyword_classify(text: str) -> tuple[Intent, float] | None:
    lower = text.lower().strip()
    for intent, keywords in KEYWORD_MAP.items():
        if any(kw in lower for kw in keywords):
            return (intent, 0.95)
    return None  # Falls through to LLM tier
```

## What to Understand
- [ ] This runs BEFORE any LLM call (free, instant)
- [ ] Returns None when no keyword matches → triggers LLM fallback
- [ ] Confidence is fixed at 0.95 for keyword matches
- [ ] Order matters — first match wins
- [ ] Edge cases: "search for a task" matches SEARCH, not TASK
