# Topic: Teams Message Handler — @Mention Handling

**Time:** 15 min
**Goal:** Handle incoming @mentions in Teams group chat

---

## What to Search
- "Teams bot @mention handler Python"
- "remove_recipient_mention Teams bot"
- "M365 Agents SDK on_message activity"

## How It Works
When user types `@MINDY what is Acme's budget?` in Teams group chat:
- `activity.text` = `"<at>MINDY</at> what is Acme's budget?"`
- You need to strip the `<at>...</at>` tag

## Code
```python
@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _state: TurnState):
    # Strip @mention
    context.activity.remove_recipient_mention()
    clean_text = context.activity.text.strip()

    if not clean_text:
        return  # Empty after stripping mention

    # Get conversation metadata
    conversation_id = context.activity.conversation.id
    user_name = context.activity.from_property.name
    user_id = context.activity.from_property.id

    # Hand off to MINDY
    result = await mindy.handle(clean_text, {
        "conversation_id": conversation_id,
        "actor": user_name,
        "user_id": user_id,
    })

    await context.send_activity(result)
```

## What to Understand
- [ ] `remove_recipient_mention()` strips the `<at>` tag
- [ ] `conversation.id` uniquely identifies the chat/thread
- [ ] `from_property.name` is the user's display name
- [ ] This replaces POC's `SURFACE - Slack - MINDY - POC` trigger
