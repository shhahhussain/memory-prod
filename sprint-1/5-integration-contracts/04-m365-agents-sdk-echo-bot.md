# M365 Agents SDK — Echo Bot (Code-Ready Reference)

> For Claude Code: Use this as the authoritative reference for building the Teams bot surface layer.

## Installation

```bash
pip install microsoft-agents-hosting-aiohttp
```

This pulls in all required dependencies:
- `microsoft-agents-hosting-core` — Core framework (AgentApplication, TurnContext, etc.)
- `microsoft-agents-activity` — Activity protocol types
- `microsoft-agents-hosting-teams` — Teams channel support (install separately if needed)
- `microsoft-agents-authentication-msal` — MSAL auth (install separately for prod)

**Python:** 3.10+ minimum, 3.11+ recommended
**Supports:** 3.10, 3.11, 3.12, 3.13, 3.14

## All Available Packages

| Package | Purpose |
|---------|---------|
| `microsoft-agents-hosting-core` | Core: AgentApplication, TurnContext, TurnState |
| `microsoft-agents-hosting-aiohttp` | aiohttp web server + CloudAdapter |
| `microsoft-agents-hosting-teams` | Teams-specific activity handlers |
| `microsoft-agents-activity` | Activity types and validators |
| `microsoft-agents-authentication-msal` | MSAL auth for production |
| `microsoft-agents-storage-blob` | Azure Blob Storage |
| `microsoft-agents-storage-cosmos` | CosmosDB storage |
| `microsoft-agents-copilotstudio-client` | Copilot Studio client |

## CRITICAL: Import Pattern

```python
# CORRECT — underscores
from microsoft_agents.hosting.core import AgentApplication, TurnState, TurnContext, MemoryStorage
from microsoft_agents.hosting.aiohttp import start_agent_process, jwt_authorization_middleware, CloudAdapter

# WRONG — dots (old pattern, DEPRECATED)
# from microsoft.agents.hosting.core import ...  # DO NOT USE
```

## Complete Echo Bot — 2 Files

### File 1: `start_server.py`

```python
from os import environ
from microsoft_agents.hosting.core import AgentApplication, AgentAuthConfiguration
from microsoft_agents.hosting.aiohttp import (
    start_agent_process,
    jwt_authorization_middleware,
    CloudAdapter,
)
from aiohttp.web import Request, Response, Application, run_app


def start_server(
    agent_application: AgentApplication, auth_configuration: AgentAuthConfiguration
):
    async def entry_point(req: Request) -> Response:
        agent: AgentApplication = req.app["agent_app"]
        adapter: CloudAdapter = req.app["adapter"]
        return await start_agent_process(req, agent, adapter)

    APP = Application(middlewares=[jwt_authorization_middleware])
    APP.router.add_post("/api/messages", entry_point)
    APP.router.add_get("/api/messages", lambda _: Response(status=200))
    APP["agent_configuration"] = auth_configuration
    APP["agent_app"] = agent_application
    APP["adapter"] = agent_application.adapter

    try:
        run_app(APP, host="localhost", port=environ.get("PORT", 3978))
    except Exception as error:
        raise error
```

### File 2: `app.py`

```python
from microsoft_agents.hosting.core import (
    AgentApplication,
    TurnState,
    TurnContext,
    MemoryStorage,
)
from microsoft_agents.hosting.aiohttp import CloudAdapter
from start_server import start_server


# Create the agent application
AGENT_APP = AgentApplication[TurnState](
    storage=MemoryStorage(), adapter=CloudAdapter()
)


# Handler for /help and welcome
async def _help(context: TurnContext, _: TurnState):
    await context.send_activity(
        "Welcome to OrgMind! Type /help for help or send a message."
    )


# Register handlers
AGENT_APP.conversation_update("membersAdded")(_help)
AGENT_APP.message("/help")(_help)


@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _):
    await context.send_activity(f"you said: {context.activity.text}")


# Start server
if __name__ == "__main__":
    try:
        start_server(AGENT_APP, None)  # None = anonymous mode (no auth for dev)
    except Exception as error:
        raise error
```

## Key API Surface

### AgentApplication

```python
AgentApplication[TurnState](
    storage: Storage,         # MemoryStorage() for dev, BlobStorage for prod
    adapter: CloudAdapter,    # Handles HTTP ↔ Activity translation
)
```

**Handler registration patterns:**

```python
# Decorator pattern
@AGENT_APP.activity("message")
async def on_message(context: TurnContext, state: TurnState): ...

# Function call pattern
AGENT_APP.conversation_update("membersAdded")(handler_func)
AGENT_APP.message("/help")(handler_func)
```

### TurnContext

```python
context.activity.text          # User's message text
context.activity.from_property # Sender info
context.activity.conversation  # Conversation reference

await context.send_activity("text")              # Send a text message
await context.send_activity(Activity(...))       # Send structured activity
await context.update_activity(Activity(...))     # Update existing message
await context.delete_activity(activity_id)       # Delete a message
```

### TurnState

```python
state.get_value("conversation.key")    # Read state
state.set_value("conversation.key", v) # Write state
```

## Testing Locally

```bash
# Terminal 1: run the bot
python app.py
# Output: Running on http://localhost:3978

# Terminal 2: install and run test tool
npm install -g @microsoft/teams-app-test-tool
teamsapptester
# Opens browser at http://localhost:56150
```

## Default Port

The M365 Agents SDK convention is **port 3978**. This is what the test tool expects.

## IMPORTANT NOTES FOR CODE GENERATION

1. **Imports use underscores**: `microsoft_agents`, NOT `microsoft.agents`
2. **Port 3978** is the convention — test tools expect this
3. **`auth_configuration=None`** enables anonymous mode for local dev
4. **aiohttp** is the web framework — NOT FastAPI, NOT Flask
5. **`MemoryStorage()`** for dev — use `BlobStorage` or `CosmosDbStorage` for prod
6. The M365 SDK handles Teams **messaging**. The Agent Framework handles **AI logic**. They are separate layers.
