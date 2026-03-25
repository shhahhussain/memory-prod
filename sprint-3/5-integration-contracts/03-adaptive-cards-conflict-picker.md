# Adaptive Cards — Conflict Picker (Code-Ready Reference)

> For Claude Code: Let users manually resolve conflicts via Adaptive Cards.

## Card Design

```python
def build_conflict_card(group: str, candidates: list[dict]) -> dict:
    body = [
        {"type": "TextBlock", "text": f"Conflict: {group}", "weight": "Bolder", "size": "Medium"},
        {"type": "TextBlock", "text": "Multiple versions found. Pick the correct one:", "wrap": True},
    ]

    for i, c in enumerate(candidates):
        body.append({"type": "Container", "items": [
            {"type": "TextBlock", "text": c["content"][:150], "wrap": True},
            {"type": "FactSet", "facts": [
                {"title": "Date", "value": c.get("metadata", {}).get("as_of", "unknown")},
                {"title": "Source", "value": c.get("metadata", {}).get("source_type", "unknown")},
                {"title": "Confidence", "value": f"{c.get('metadata', {}).get('confidence', 0):.0%}"},
            ]},
        ]})

    actions = [
        {"type": "Action.Submit", "title": f"Pick #{i+1}", "data": {"action": "resolve_conflict", "group": group, "winner_id": c.get("id")}}
        for i, c in enumerate(candidates)
    ]

    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard", "version": "1.5",
        "body": body, "actions": actions,
    }
```

## IMPORTANT NOTES
1. Show each candidate with its metadata so user can make informed choice
2. Action data includes `winner_id` — system marks others as losers
3. Log the manual resolution in audit log
