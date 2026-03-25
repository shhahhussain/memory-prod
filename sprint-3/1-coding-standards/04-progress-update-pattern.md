# Progress Update Pattern (Code-Ready Reference)

> For Claude Code: Show live progress in Teams while agents work.

## Send → Update Pattern

Teams doesn't support true streaming. Instead, send a message and update it.

```python
from microsoft_agents.hosting.core import TurnContext
from microsoft_agents.activity import Activity

async def process_with_progress(context: TurnContext, query: str):
    # Step 1: Send initial "thinking" message
    msg = await context.send_activity("Searching organizational memory...")

    # Step 2: Do work
    search_results = await search_memory(query)

    # Step 3: Update message
    await context.update_activity(Activity(
        type="message", id=msg.id,
        text=f"Found {len(search_results)} results. Generating response...",
    ))

    # Step 4: Generate response
    response = await generate_response(search_results, query)

    # Step 5: Final update with result
    await context.update_activity(Activity(
        type="message", id=msg.id, text=response,
    ))
```

## With Adaptive Card Progress

```python
async def process_with_card_progress(context: TurnContext, query: str):
    # Send progress card
    progress_card = {"type": "AdaptiveCard", "version": "1.5", "body": [
        {"type": "TextBlock", "text": "Processing...", "weight": "Bolder"},
        {"type": "TextBlock", "text": "Step 1/3: Searching memory...", "isSubtle": True},
    ]}

    attachment = Attachment(content_type="application/vnd.microsoft.card.adaptive", content=progress_card)
    msg = await context.send_activity(Activity(type="message", attachments=[attachment]))

    # ... do work, then update with final card ...
```

## IMPORTANT NOTES
1. `send_activity()` returns the message ID — save it for updates
2. `update_activity()` replaces the entire message content
3. Don't update too frequently — Teams may rate-limit
4. Final message should be the complete response (not "Done!")
