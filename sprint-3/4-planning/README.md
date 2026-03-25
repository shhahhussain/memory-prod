# Sprint 3 — Surface Swap (Slack → Teams) Research

**Milestone:** M3 — Surface Swap (18-22h)
**Focus:** Replace Slack surface with Microsoft Teams, Adaptive Cards, thread context

---

## What to Research

### 1. Teams Bot Message Handling

**The 3 SDKs (don't confuse them):**
| SDK | What it does |
|-----|-------------|
| **Microsoft Agent Framework** | AI agent logic (already built in Sprint 2) |
| **M365 Agents SDK** | Teams connectivity — THIS is Sprint 3 |
| **Teams SDK** | Optional higher-level features |

**Key pattern — decorator-based AgentApplication:**
```python
from microsoft_agents.hosting.aiohttp import CloudAdapter
from microsoft_agents.hosting.core import AgentApplication, TurnState, TurnContext, MemoryStorage

AGENT_APP = AgentApplication[TurnState](storage=STORAGE, adapter=ADAPTER, ...)

@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _state: TurnState):
    text = context.activity.text
    # Strip @mention
    context.activity.remove_recipient_mention()
    # Hand off to MINDY orchestrator
    result = await mindy.handle(text, build_context(context))
    await context.send_activity(result)
```

**Docs:**
- https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/agents-sdk-overview
- https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/channel-and-group-conversations

**Search queries:**
- "M365 Agents SDK Python bot message handler"
- "Teams bot group chat @mention Python"
- "Teams bot remove_recipient_mention"

---

### 2. Thread Context Persistence (Slack → Teams Migration)

**POC had:**
- `slack_thread_context` — shared per-thread JSON
- `slack_agent_context` — per-agent per-thread JSON
- `last_user_text` + `last_reply_text` per agent
- Vague follow-up detection
- Event deduplication (team_id + event_id)

**Teams equivalent:**
- `conversation_reference` — Teams' native conversation identifier
- `context.activity.conversation.id` — unique per thread/chat
- `context.activity.reply_to_id` — for threaded replies
- Need to build same PG tables but keyed by Teams conversation IDs

**Search queries:**
- "Teams bot conversation reference Python"
- "Teams bot conversation state management"
- "Teams conversation.id vs reply_to_id threading"
- "M365 Agents SDK TurnState persistence"

---

### 3. Adaptive Cards (Replaces Slack Blocks)

POC used Slack interactive blocks for:
- Draft review cards (approve/reject/update buttons)
- Conflict override cards (pick winner dropdown)
- Progress step posts

**Teams equivalent: Adaptive Cards**
- JSON-based, rendered natively in Teams
- Designer: https://adaptivecards.io/designer/ (set host to "Microsoft Teams")
- Teams supports schema up to **v1.5**

**Send a card:**
```python
from microsoft_agents.activity import CardFactory

card_json = {
    "type": "AdaptiveCard",
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.5",
    "body": [
        {"type": "TextBlock", "text": "Draft Review", "weight": "Bolder", "size": "Medium"},
        {"type": "TextBlock", "text": "Acme Q1 budget is $50K", "wrap": True}
    ],
    "actions": [
        {"type": "Action.Submit", "title": "Approve", "data": {"action": "approve", "customId": "fact_123"}},
        {"type": "Action.Submit", "title": "Reject", "data": {"action": "reject", "customId": "fact_123"}}
    ]
}
await context.send_activity(Activity(
    type="message",
    attachments=[CardFactory.adaptive_card(card_json)]
))
```

**Handle button clicks:**
```python
@AGENT_APP.activity("invoke")
async def on_invoke(context: TurnContext, _state: TurnState):
    # Button data comes in activity.value, NOT activity.text
    action_data = context.activity.value
    action = action_data.get("action")  # "approve" or "reject"
    custom_id = action_data.get("customId")
    # ... handle action
```

**Search queries:**
- "Adaptive Cards Python Teams bot"
- "Adaptive Cards Action.Submit handler Python"
- "Adaptive Cards designer Teams"
- "Teams bot on_invoke_activity Adaptive Card"

---

### 4. Live Progress Updates (Streaming Alternative)

Teams doesn't support token-by-token streaming. Use **send → update** pattern:

```python
# Step 1: Send initial "thinking" message
msg = await context.send_activity("Searching memory...")

# Step 2: Update same message as agents complete
await context.update_activity(
    Activity(type="message", id=msg.id, text="FINDR found 3 results. Analyzing...")
)

# Step 3: Final update with full Adaptive Card response
await context.update_activity(
    Activity(type="message", id=msg.id, attachments=[CardFactory.adaptive_card(final_card)])
)
```

**POC equivalent:** Slack's multi-post sequence in `Code - Build Ordered Slack Posts`

**Docs:** https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/update-and-delete-bot-messages

**Search queries:**
- "Teams bot update message Python"
- "Teams bot streaming alternative update_activity"

---

### 5. Teams App Manifest & Sideloading

**Manifest structure:**
```json
{
  "$schema": "https://developer.microsoft.com/en-us/json-schemas/teams/v1.17/MicrosoftTeams.schema.json",
  "manifestVersion": "1.17",
  "id": "<app-id>",
  "bots": [{
    "botId": "<app-id>",
    "scopes": ["personal", "team", "groupChat"]
  }]
}
```

Package: `manifest.json` + `color.png` (192x192) + `outline.png` (32x32) → zip → sideload

**Visual editor:** https://dev.teams.microsoft.com/
**Schema docs:** https://learn.microsoft.com/en-us/microsoftteams/platform/resources/schema/manifest-schema

**Search queries:**
- "Teams app manifest sideload Python bot"
- "Teams Developer Portal app registration"

---

### 6. Proactive Messages (for Approval Notifications)

POC posted Slack messages for email approval queue. Teams needs proactive messaging:

```python
# Save reference during a conversation turn
conversation_ref = TurnContext.get_conversation_reference(context.activity)

# Later, send proactive message
await adapter.continue_conversation(
    conversation_ref,
    callback=send_approval_notification,
    bot_app_id=settings.microsoft_app_id,
)
```

**Search queries:**
- "Teams bot proactive messages Python"
- "M365 Agents SDK continue_conversation"
- "Teams bot send message outside turn context"

---

### 7. Event Deduplication (Teams-specific)

POC had `slack_event_dedupe` table. Teams may send duplicate activities.

**Search queries:**
- "Teams bot duplicate message handling"
- "Teams activity deduplication id"

---

## Checklist
- [ ] Build echo bot with M365 Agents SDK
- [ ] Handle @mention stripping in group chat
- [ ] Build Adaptive Card for draft review (approve/reject/update)
- [ ] Build Adaptive Card for conflict picker
- [ ] Handle Action.Submit invoke for card buttons
- [ ] Implement send → update progress pattern
- [ ] Create Teams app manifest and sideload
- [ ] Test proactive messaging
- [ ] Migrate thread context tables (slack_ → teams_)
- [ ] Test event deduplication
