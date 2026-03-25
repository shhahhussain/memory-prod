# Teams Message Handler — @Mention (Code-Ready Reference)

> For Claude Code: Handle Teams @mention messages in group chats.

## How @mentions Work

In group chats, users must @mention the bot. The message text contains `<at>BotName</at>` prefix.

```python
from microsoft_agents.hosting.core import AgentApplication, TurnState, TurnContext

@AGENT_APP.activity("message")
async def on_message(context: TurnContext, state: TurnState):
    # Strip @mention from message text
    text = context.activity.text or ""

    # Remove <at>BotName</at> tags
    import re
    clean_text = re.sub(r"<at>[^<]+</at>\s*", "", text).strip()

    if not clean_text:
        return  # Empty after stripping mention

    # Route to MINDY
    response = await mindy_route(clean_text, actor=context.activity.from_property.name)
    await context.send_activity(response)
```

## Conversation Types

```python
@AGENT_APP.activity("message")
async def on_message(context: TurnContext, state: TurnState):
    conv_type = context.activity.conversation.conversation_type
    # "personal" — 1:1 DM with bot
    # "groupChat" — group chat
    # "channel" — Teams channel
```

## IMPORTANT NOTES
1. In group chats, messages only arrive when bot is @mentioned
2. Strip `<at>` tags before processing
3. In personal (1:1) chats, no @mention needed
4. `context.activity.from_property.name` gives the user's display name
