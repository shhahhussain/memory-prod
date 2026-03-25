# Topic: Adaptive Cards — Conflict Override Picker

**Time:** 15 min
**Goal:** Build the "pick the correct memory" card for conflict resolution

---

## What to Search
- "Adaptive Cards Input.ChoiceSet Teams"
- "Adaptive Cards radio button selection"

## Conflict Picker Card JSON
```json
{
  "type": "AdaptiveCard",
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "version": "1.5",
  "body": [
    {
      "type": "TextBlock",
      "text": "⚠️ Conflict Detected: acme_budget_q1",
      "weight": "Bolder",
      "size": "Medium"
    },
    {
      "type": "TextBlock",
      "text": "Multiple memories disagree. Pick the correct one:",
      "wrap": true
    },
    {
      "type": "Input.ChoiceSet",
      "id": "winnerId",
      "style": "expanded",
      "choices": [
        {"title": "Acme Q1 budget is $50K (2026-01-30, conf: 0.95)", "value": "fact:abc123"},
        {"title": "Acme Q1 budget is $35K (2026-01-28, conf: 0.88)", "value": "fact:def456"}
      ]
    }
  ],
  "actions": [
    {
      "type": "Action.Submit",
      "title": "Set Winner",
      "data": {"action": "override_set", "conflictGroup": "acme_budget_q1"}
    },
    {
      "type": "Action.Submit",
      "title": "Clear Override",
      "data": {"action": "override_clear", "conflictGroup": "acme_budget_q1"}
    }
  ]
}
```

## Handling the Selection
```python
@AGENT_APP.activity("invoke")
async def on_invoke(context: TurnContext, _state: TurnState):
    data = context.activity.value
    action = data.get("action")

    if action == "override_set":
        winner_id = data.get("winnerId")
        conflict_group = data.get("conflictGroup")
        await conflict_service.set_override(conflict_group, winner_id, context.activity.from_property.name)
        await context.send_activity(f"Override set: {winner_id} is now the winner for {conflict_group}")

    elif action == "override_clear":
        conflict_group = data.get("conflictGroup")
        await conflict_service.clear_override(conflict_group)
        await context.send_activity(f"Override cleared for {conflict_group}")
```

## What to Understand
- [ ] `Input.ChoiceSet` with `style: "expanded"` = radio buttons
- [ ] Selected value comes in `context.activity.value["winnerId"]`
- [ ] `on_invoke` handles ALL card button clicks
- [ ] Need to distinguish actions by the `data.action` field
