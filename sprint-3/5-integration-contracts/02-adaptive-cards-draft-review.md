# Adaptive Cards — Draft Review (Code-Ready Reference)

> For Claude Code: Build Adaptive Cards for the draft review queue in Teams.

## Adaptive Card JSON for a Draft Item

```python
def build_draft_review_card(draft: dict) -> dict:
    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.5",
        "body": [
            {"type": "TextBlock", "text": "Draft Review", "weight": "Bolder", "size": "Medium"},
            {"type": "TextBlock", "text": draft["content"][:200], "wrap": True},
            {"type": "FactSet", "facts": [
                {"title": "Type", "value": draft.get("metadata", {}).get("memory_type", "fact")},
                {"title": "Source", "value": draft.get("metadata", {}).get("source_type", "unknown")},
                {"title": "Confidence", "value": f"{draft.get('metadata', {}).get('confidence', 0):.0%}"},
                {"title": "ID", "value": draft.get("custom_id", "N/A")},
            ]},
        ],
        "actions": [
            {"type": "Action.Submit", "title": "Approve", "style": "positive",
             "data": {"action": "approve", "custom_id": draft.get("custom_id")}},
            {"type": "Action.Submit", "title": "Reject", "style": "destructive",
             "data": {"action": "reject", "custom_id": draft.get("custom_id")}},
        ],
    }
```

## Sending an Adaptive Card

```python
from microsoft_agents.hosting.core import TurnContext
from microsoft_agents.activity import Activity, Attachment

async def send_draft_cards(context: TurnContext, drafts: list[dict]):
    for draft in drafts:
        card = build_draft_review_card(draft)
        attachment = Attachment(
            content_type="application/vnd.microsoft.card.adaptive",
            content=card,
        )
        await context.send_activity(Activity(type="message", attachments=[attachment]))
```

## Handling Button Clicks

```python
@AGENT_APP.activity("invoke")
async def on_invoke(context: TurnContext, state: TurnState):
    data = context.activity.value  # {"action": "approve", "custom_id": "..."}
    action = data.get("action")
    custom_id = data.get("custom_id")

    if action in ("approve", "reject"):
        result = await handle_approve_reject(sm_client, action, custom_id, context.activity.from_property.name)
        await context.send_activity(f"Draft {custom_id} has been {action}d.")
```

## IMPORTANT NOTES
1. Teams supports Adaptive Cards schema up to version **1.5**
2. Button clicks arrive as `invoke` activities, NOT `message`
3. `context.activity.value` contains the card action data (not `.text`)
4. Design cards at https://adaptivecards.io/designer/ (set host to Microsoft Teams)
