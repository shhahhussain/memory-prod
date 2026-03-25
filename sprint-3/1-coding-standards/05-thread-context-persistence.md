# Thread Context Persistence (Code-Ready Reference)

> For Claude Code: Maintain conversation context across messages in Teams.

## Using TurnState

```python
@AGENT_APP.activity("message")
async def on_message(context: TurnContext, state: TurnState):
    # Read conversation history
    history = state.get_value("conversation.history") or []

    # Add current message
    history.append({"role": "user", "content": context.activity.text})

    # Process with history
    response = await process_with_context(context.activity.text, history)

    # Save updated history
    history.append({"role": "assistant", "content": response})
    state.set_value("conversation.history", history[-20:])  # Keep last 20

    await context.send_activity(response)
```

## Conversation Reference (for Proactive Messages)

```python
# Save conversation reference for later
conv_ref = context.activity.get_conversation_reference()
# Store in DB for proactive messaging later
```

## IMPORTANT NOTES
1. `TurnState` persists across turns within a conversation
2. Use `MemoryStorage` for dev, `BlobStorage`/`CosmosDB` for production
3. Keep history bounded (last 20 messages) to prevent state bloat
4. Conversation reference needed for proactive messages
