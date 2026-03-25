# Topic: M365 Agents SDK — Build an Echo Bot

**Time:** 45-60 min
**Goal:** Get a basic Teams bot running that echoes messages back

---

## What to Search
- "M365 Agents SDK Python quickstart echo bot"
- "microsoft-agents-hosting-aiohttp bot sample"
- "Teams bot Python hello world 2026"

## Docs to Read
- https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/agents-sdk-overview
- https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/quickstart

## Repo to Clone
```bash
git clone https://github.com/microsoft/Agents-for-python
# Find the echo bot sample
```

## Install
```bash
pip install microsoft-agents-hosting-core
pip install microsoft-agents-hosting-aiohttp
pip install microsoft-agents-hosting-teams
pip install microsoft-agents-activity
pip install microsoft-agents-authentication-msal
```

## What to Understand
- [ ] `AgentApplication` class — the main entry point
- [ ] `@AGENT_APP.activity("message")` decorator — how messages are handled
- [ ] `TurnContext` — what it gives you (activity text, conversation id, etc.)
- [ ] `TurnState` — what state management looks like
- [ ] `context.send_activity()` — how to reply
- [ ] Imports use **underscores**: `microsoft_agents` NOT dots

## Quick Test
```python
from microsoft_agents.hosting.core import AgentApplication, TurnState, TurnContext

@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _state: TurnState):
    await context.send_activity(f"You said: {context.activity.text}")
```
