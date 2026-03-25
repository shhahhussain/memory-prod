# Topic: Proactive Messages — Sending Outside a Turn

**Time:** 15 min
**Goal:** Send messages to Teams without a user triggering it (for approval notifications)

---

## What to Search
- "Teams bot proactive messages Python"
- "M365 Agents SDK continue_conversation"
- "Teams bot send message without user trigger"

## When You Need This
- Email approval queue → post notification to Teams channel
- Nightly consolidation job → post summary to Teams
- Background agent completed → notify user

## Code
```python
# STEP 1: Save conversation reference during a normal turn
conversation_references = {}  # In production, store in PostgreSQL

@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _state: TurnState):
    # Save for later proactive use
    ref = TurnContext.get_conversation_reference(context.activity)
    conversation_references[context.activity.conversation.id] = ref
    # ... handle message normally

# STEP 2: Send proactive message later
async def send_proactive(conversation_id: str, message: str):
    ref = conversation_references.get(conversation_id)
    if not ref:
        return  # Never talked to this conversation

    async def callback(turn_context: TurnContext):
        await turn_context.send_activity(message)

    await adapter.continue_conversation(
        ref,
        callback=callback,
        bot_app_id=settings.microsoft_app_id,
    )
```

## What to Understand
- [ ] Must save `conversation_reference` during a normal turn first
- [ ] `continue_conversation()` creates a new turn context without user input
- [ ] Store references in PostgreSQL, not in-memory (survives restarts)
- [ ] This replaces POC's Slack `chat.postMessage` for approval notifications
