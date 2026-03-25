# Topic: Progress Updates — Send → Update Pattern

**Time:** 10 min
**Goal:** Show "thinking..." progress while agents work

---

## What to Search
- "Teams bot update_activity Python"
- "Teams bot update message in place"

## Code
```python
async def handle_with_progress(context: TurnContext, query: str):
    # Step 1: Send "thinking" message
    msg = await context.send_activity("🔍 Searching memory...")

    # Step 2: Run agents (this takes time)
    intent = await router.classify(query)
    await context.update_activity(
        Activity(type="message", id=msg.id, text=f"🧠 Routing to {intent.agents}...")
    )

    results = await mindy.fan_out(intent.agents, query)
    await context.update_activity(
        Activity(type="message", id=msg.id, text=f"📝 Synthesizing {len(results)} agent results...")
    )

    # Step 3: Final response (replace with Adaptive Card or text)
    final_response = await mindy.synthesize(results)
    await context.update_activity(
        Activity(type="message", id=msg.id, text=final_response)
    )
```

## What to Understand
- [ ] `send_activity()` returns a message with an `id`
- [ ] `update_activity()` replaces that message's content in-place
- [ ] User sees the message change as agents complete
- [ ] This replaces POC's Slack multi-post sequence
- [ ] Final update can be an Adaptive Card instead of plain text
