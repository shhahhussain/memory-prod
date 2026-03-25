# Proactive Messages (Code-Ready Reference)

> For Claude Code: Send messages to Teams outside of a user turn (notifications, alerts).

## Save Conversation Reference

```python
# During a regular turn, save the reference
@AGENT_APP.activity("message")
async def on_message(context: TurnContext, state: TurnState):
    conv_ref = context.activity.get_conversation_reference()
    # Store in DB with user ID as key
    await save_conv_ref(context.activity.from_property.id, conv_ref)
```

## Send Proactive Message

```python
from microsoft_agents.hosting.aiohttp import CloudAdapter

async def send_proactive(adapter: CloudAdapter, conv_ref: dict, message: str):
    async def callback(turn_context: TurnContext):
        await turn_context.send_activity(message)

    await adapter.continue_conversation(conv_ref, callback)
```

## Use Cases for OrgMind
- Draft items awaiting review notification
- Scheduled memory digests
- Conflict resolution alerts
- Task deadline reminders

## IMPORTANT NOTES
1. Must save `conversation_reference` during a normal turn first
2. Proactive messages require the bot's app ID and password (auth must be configured)
3. Don't spam — Teams may throttle excessive proactive messages
4. Works in personal, group, and channel conversations
