# Topic: Adaptive Cards — Draft Review Card

**Time:** 20 min
**Goal:** Build the approve/reject/update card that replaces Slack interactive blocks

---

## What to Search
- "Adaptive Cards Action.Submit Teams Python"
- "Adaptive Cards designer Teams"
- "Adaptive Cards v1.5 schema"

## Designer Tool
https://adaptivecards.io/designer/ → Set host app to "Microsoft Teams"

## Draft Review Card JSON
```json
{
  "type": "AdaptiveCard",
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "version": "1.5",
  "body": [
    {
      "type": "TextBlock",
      "text": "Draft Review",
      "weight": "Bolder",
      "size": "Medium"
    },
    {
      "type": "TextBlock",
      "text": "Acme Q1 budget confirmed as $50K from client call",
      "wrap": true
    },
    {
      "type": "FactSet",
      "facts": [
        {"title": "Type", "value": "fact"},
        {"title": "Confidence", "value": "0.85"},
        {"title": "Status", "value": "draft"},
        {"title": "ID", "value": "fact_acme_q1_50k"}
      ]
    }
  ],
  "actions": [
    {
      "type": "Action.Submit",
      "title": "✅ Approve",
      "data": {"action": "approve", "customId": "fact_acme_q1_50k"}
    },
    {
      "type": "Action.Submit",
      "title": "❌ Reject",
      "data": {"action": "reject", "customId": "fact_acme_q1_50k"}
    },
    {
      "type": "Action.ShowCard",
      "title": "✏️ Update",
      "card": {
        "type": "AdaptiveCard",
        "body": [
          {
            "type": "Input.Text",
            "id": "newContent",
            "placeholder": "Enter updated content...",
            "isMultiline": true
          }
        ],
        "actions": [
          {
            "type": "Action.Submit",
            "title": "Submit Update",
            "data": {"action": "update", "customId": "fact_acme_q1_50k"}
          }
        ]
      }
    }
  ]
}
```

## Sending the Card
```python
from microsoft_agents.activity import CardFactory, Activity

await context.send_activity(Activity(
    type="message",
    attachments=[CardFactory.adaptive_card(card_json)]
))
```

## What to Understand
- [ ] `Action.Submit` sends data to your bot's invoke handler
- [ ] `Action.ShowCard` expands inline (for the update text input)
- [ ] Card data comes in `context.activity.value` (NOT `.text`)
- [ ] Teams supports Adaptive Cards up to v1.5
- [ ] This replaces Slack's `actions` blocks
