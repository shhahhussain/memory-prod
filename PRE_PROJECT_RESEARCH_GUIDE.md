# OrgMind Phase 2 — Pre-Project Research Guide

**Purpose:** Everything Shah needs to study before writing a single line of code.
**Time needed:** 2-3 days of focused reading + running samples.
**Goal:** Walk into Day 1 looking like you've built Teams bots before.

---

## The Big Picture — 3 SDKs You Need to Understand

There are **3 distinct Microsoft SDKs** that work together. This is the #1 thing that confuses newcomers:

| SDK | What it does | Analogy |
|-----|-------------|---------|
| **Microsoft Agent Framework** | AI agent logic, multi-agent orchestration, workflows | The brain (MINDY, FINDR, TASKR, CAMPA live here) |
| **M365 Agents SDK** | Teams/channel connectivity, auth, message handling | The mouth/ears (receives Teams messages, sends replies) |
| **Teams SDK** | Higher-level Teams app features (tabs, extensions) | Optional — you may not need this |

**Agent Framework** = your agents' intelligence
**M365 Agents SDK** = how they talk to Teams

---

## PHASE 1: Core Framework (Days 1-2)

### 1.1 Microsoft Agent Framework (Python)

**What to read:**
- Overview: https://learn.microsoft.com/en-us/agent-framework/overview/
- Quickstart: https://learn.microsoft.com/en-us/agent-framework/tutorials/quick-start
- Workflows docs: https://learn.microsoft.com/en-us/agent-framework/workflows/
- RC announcement blog: https://devblogs.microsoft.com/foundry/microsoft-agent-framework-reaches-release-candidate/
- Multi-agent blog: https://devblogs.microsoft.com/semantic-kernel/unlocking-enterprise-ai-complexity-multi-agent-orchestration-with-the-microsoft-agent-framework/

**Repos to clone and explore:**
- Core framework: https://github.com/microsoft/agent-framework
- Samples (MUST READ): https://github.com/microsoft/Agent-Framework-Samples
  - Start with: `python/samples/03-workflows` (this is your MINDY orchestration pattern)
- Spec-to-Agents demo (multi-agent): https://github.com/microsoft/spec-to-agents
- AI Agents for Beginners course: https://github.com/microsoft/ai-agents-for-beginners

**Install:**
```bash
pip install agent-framework --pre
```

**Key concepts to understand:**
- Agents are created via `.as_agent()` on provider clients — NO class inheritance needed
- `WorkflowBuilder` with `add_edge()` for sequential chains
- `ConcurrentBuilder` for parallel fan-out (this is how MINDY dispatches to FINDR/TASKR/CAMPA)
- `FanOutEdgeGroup` for conditional parallel dispatch
- Handoff, checkpointing, human-in-the-loop patterns

**How n8n maps to Agent Framework:**
| n8n concept | Agent Framework equivalent |
|------------|--------------------------|
| Sequential node chain | `WorkflowBuilder` with `add_edge()` |
| Parallel execution | `ConcurrentBuilder` / `FanOutEdgeGroup` |
| HTTP/API nodes | Agent tools (annotated Python functions) |
| Webhook triggers | M365 SDK `/api/messages` endpoint |
| Credential management | Azure env vars + MSAL auth |

### 1.2 M365 Agents SDK (Python)

**What to read:**
- Overview: https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/agents-sdk-overview
- Quickstart: https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/quickstart
- Migration from Bot Framework: https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/bf-migration-python

**Repo:**
- https://github.com/microsoft/Agents-for-python

**Install (key packages):**
```bash
pip install microsoft-agents-hosting-core
pip install microsoft-agents-hosting-aiohttp
pip install microsoft-agents-hosting-teams
pip install microsoft-agents-activity
pip install microsoft-agents-authentication-msal
```

**Key pattern — decorator-based AgentApplication:**
```python
from microsoft_agents.hosting.aiohttp import CloudAdapter
from microsoft_agents.hosting.core import AgentApplication, TurnState, TurnContext, MemoryStorage

AGENT_APP = AgentApplication[TurnState](storage=STORAGE, adapter=ADAPTER, ...)

@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _state: TurnState):
    await context.send_activity(f"You said: {context.activity.text}")
```

> **NOTE:** Imports use underscores: `microsoft_agents`, NOT dots.

---

## PHASE 2: Teams Integration (Day 2)

### 2.1 Azure Bot Registration (step by step)

1. Azure Portal → Microsoft Entra ID → App registrations → New registration
2. Name: `OrgMind-Bot`, Account type: **Multitenant** (required for Teams)
3. Note the **Application (client) ID** = your `MicrosoftAppId`
4. Certificates & secrets → New client secret → save as `MicrosoftAppPassword`
5. Azure Portal → search **Azure Bot** → Create
6. Paste App ID, set pricing to F0 (free for dev)
7. Channels → Enable **Microsoft Teams**
8. Configuration → Messaging endpoint: `https://your-domain.azurewebsites.net/api/messages`

**Docs:**
- https://learn.microsoft.com/en-us/azure/bot-service/bot-service-quickstart-registration
- https://learn.microsoft.com/en-us/azure/bot-service/abs-quickstart

### 2.2 Teams App Manifest

Manifest is a JSON + 2 icons, zipped:

```json
{
  "$schema": "https://developer.microsoft.com/en-us/json-schemas/teams/v1.17/MicrosoftTeams.schema.json",
  "manifestVersion": "1.17",
  "id": "<your-app-id>",
  "bots": [{
    "botId": "<your-app-id>",
    "scopes": ["personal", "team", "groupChat"]
  }]
}
```

Package: `manifest.json` + `color.png` (192x192) + `outline.png` (32x32) → zip → sideload in Teams.

**Visual editor:** https://dev.teams.microsoft.com/
**Schema docs:** https://learn.microsoft.com/en-us/microsoftteams/platform/resources/schema/manifest-schema

### 2.3 Group Chat Messages

- When user @mentions bot in group chat, `activity.text` contains `<at>BotName</at>` prefix
- Strip it: `turn_context.activity.remove_recipient_mention()`
- `turn_context.send_activity()` auto-replies in the same conversation
- For proactive messages (later, outside a turn): save `conversation_reference`, use `adapter.continue_conversation()`

**Docs:** https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/channel-and-group-conversations

### 2.4 Adaptive Cards (for structured responses)

- JSON-based UI cards rendered natively in Teams
- Designer tool: https://adaptivecards.io/designer/ (set host app to "Microsoft Teams")
- Teams supports schema version up to **1.5**
- Send via `CardFactory.adaptive_card(card_json)`
- Handle button clicks via `turn_context.activity.value` (not `.text`)

### 2.5 Live Progress Updates (streaming alternative)

Teams doesn't support true token-by-token streaming. Instead, use **send → update** pattern:

```python
# Send initial message
msg = await turn_context.send_activity("Step 1/3: Searching memory...")

# Do work, then update same message
await turn_context.update_activity(
    Activity(type="message", id=msg.id, text="Step 2/3: Analyzing...")
)

# Final update with Adaptive Card
await turn_context.update_activity(
    Activity(type="message", id=msg.id, attachments=[CardFactory.adaptive_card(result_card)])
)
```

**Docs:** https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/update-and-delete-bot-messages

### 2.6 Deployment to Azure App Service

```bash
# Create resources
az group create --name orgmind-rg --location eastus
az appservice plan create --name orgmind-plan --resource-group orgmind-rg --sku B1 --is-linux
az webapp create --name orgmind-bot --resource-group orgmind-rg --plan orgmind-plan --runtime "PYTHON:3.11"

# Set env vars
az webapp config appsettings set --name orgmind-bot --resource-group orgmind-rg \
  --settings MicrosoftAppId="<id>" MicrosoftAppPassword="<secret>"

# Deploy
zip -r deploy.zip . -x ".git/*" "__pycache__/*" ".env"
az webapp deploy --name orgmind-bot --resource-group orgmind-rg --src-path deploy.zip --type zip
```

**For local dev:** Use ngrok to tunnel `localhost:3978` to a public HTTPS URL.

---

## PHASE 3: Supermemory Integration (Day 2-3)

### 3.1 Supermemory Docs

- Overview: https://supermemory.ai/docs/intro
- Quickstart: https://supermemory.ai/docs/quickstart
- API (ingesting): https://supermemory.ai/docs/memory-api/ingesting
- API (search): https://supermemory.ai/docs/search/overview
- MCP setup: https://supermemory.ai/docs/supermemory-mcp/setup
- SDK docs: https://supermemory.ai/docs/integrations/supermemory-sdk
- Console (get API key): https://console.supermemory.ai

### 3.2 Python SDK (recommended path)

```bash
pip install supermemory
```

```python
from supermemory import AsyncSupermemory

client = AsyncSupermemory(api_key="sm_your_key")

# Write memory
await client.add(
    content="Nike Q4 campaign budget increased to $2.1M",
    container_tags=["project_nike"],
    metadata={"source": "meeting_notes", "category": "budget"}
)

# Search memories (extracted facts)
response = await client.search.memories(
    q="Nike campaign budget",
    container_tags=["project_nike"]
)

# Search documents (RAG chunks)
response = await client.search.documents(
    q="campaign planning notes",
    container_tags=["project_nike"],
    limit=10, threshold=0.5, rerank=True
)

# User profile
profile = await client.profile(container_tag="project_nike")
```

### 3.3 REST API (if you need direct control)

**Base URL:** `https://api.supermemory.ai`
**Auth:** `Authorization: Bearer sm_your_key`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v3/documents` | POST | Add/ingest content |
| `/v3/documents/{id}` | GET | Get document status |
| `/v3/documents/{id}` | DELETE | Delete document |
| `/v4/search` | POST | Search memories + documents |
| `/v4/profile` | GET | User profile (static + dynamic) |

**Search modes:**
- `"hybrid"` — memories (extracted facts) + document chunks
- `"memories"` — extracted facts only

**Supersede/conflict:** Supermemory handles this **automatically**. No explicit supersede endpoint — add new content and the engine resolves contradictions.

### 3.4 MCP Integration (alternative path)

If agents use MCP tool-calling:

```bash
pip install mcp
```

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client("https://mcp.supermemory.ai/mcp", headers={"Authorization": f"Bearer {key}"}) as (read, write, _):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool("memory", arguments={"content": "...", "action": "save"})
        result = await session.call_tool("recall", arguments={"query": "...", "includeProfile": True})
```

**MCP tools available:** `memory` (save/forget), `recall` (search), `listProjects`, `whoAmI`

**Recommendation:** Use the **Python SDK** for direct API calls. Use **MCP** only if your agent framework expects tool-calling infrastructure.

---

## PHASE 4: Multi-Agent Patterns (Day 3)

### 4.1 Fan-Out Pattern (MINDY → agents)

Use `asyncio.gather(return_exceptions=True)` for partial-failure tolerance (if TASKR fails, still use FINDR + CAMPA results):

```python
import asyncio

class MindyOrchestrator:
    async def fan_out(self, agents: list[BaseAgent], request: AgentRequest) -> list[AgentResult]:
        tasks = [asyncio.wait_for(agent.execute(request), timeout=30.0) for agent in agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successes = [r for r in results if isinstance(r, AgentResult)]
        failures = [r for r in results if isinstance(r, BaseException)]

        for f in failures:
            logger.error("agent_failed", error=str(f))

        return successes
```

> **Why NOT `asyncio.TaskGroup`?** TaskGroup is all-or-nothing (one failure cancels everything). For your case, you want best-effort — synthesize from whatever agents succeed.

### 4.2 Intent Routing (Hybrid NLU)

```
Tier 1: Keyword/regex fast path (free, handles 60-70% of traffic)
Tier 2: Cheap LLM classifier (Gemini Flash or Haiku for ambiguous inputs)
Tier 3: Clarification (confidence < 0.65 → ask user)
```

```python
from pydantic import BaseModel
from enum import Enum

class Intent(str, Enum):
    SEARCH = "search"
    TASK = "task"
    CAMPAIGN = "campaign"
    CLARIFY = "clarify"

class RoutingDecision(BaseModel):
    intent: Intent
    confidence: float
    agents: list[str]
    reasoning: str
```

### 4.3 Pydantic Settings (config management)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    anthropic_api_key: str
    supermemory_api_key: str
    microsoft_app_id: str
    microsoft_app_password: str
    agent_timeout_seconds: float = 30.0

    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")
```

### 4.4 Framework Landscape (2026)

| Framework | Status | Notes |
|-----------|--------|-------|
| **Microsoft Agent Framework** | RC → GA Q1 2026 | YOUR CHOICE. Best for Teams + enterprise |
| **AutoGen** | DEPRECATED | Merged into MS Agent Framework |
| **Semantic Kernel** | DEPRECATED | Merged into MS Agent Framework |
| **LangGraph** | Stable | Best for complex stateful graphs |
| **CrewAI** | Active | Good for prototyping, less mature monitoring |
| **Pydantic AI** | Active | Lightweight, type-safe |

---

## Study Order (3-Day Plan)

### Day 1: Framework Foundations
- [ ] Read MS Agent Framework overview + quickstart
- [ ] Clone `Agent-Framework-Samples`, run the hello-world agent
- [ ] Read the workflows docs, run `03-workflows` samples
- [ ] Read the multi-agent orchestration blog post

### Day 2: Teams + Supermemory
- [ ] Read M365 Agents SDK quickstart
- [ ] Do the Azure bot registration (even if just for practice)
- [ ] Read Adaptive Cards docs, play with the designer
- [ ] Read Supermemory quickstart + SDK docs
- [ ] Write a test script: `add()` → `search.memories()` → verify

### Day 3: Integration Patterns
- [ ] Read the `updateActivity` pattern for live progress
- [ ] Study the `asyncio.gather` fan-out pattern
- [ ] Read pydantic-settings docs
- [ ] Map each n8n workflow to its Python equivalent (mental exercise)
- [ ] Review your own `PHASE2_ARCHITECTURE_v2.md` with fresh eyes

---

## Key Repos to Star/Clone

| Repo | Why |
|------|-----|
| https://github.com/microsoft/agent-framework | Core framework code |
| https://github.com/microsoft/Agent-Framework-Samples | Samples — START HERE |
| https://github.com/microsoft/Agents-for-python | M365 SDK (Teams layer) |
| https://github.com/microsoft/Agents | M365 SDK samples |
| https://github.com/microsoft/spec-to-agents | Multi-agent demo |
| https://github.com/microsoft/teams.py | Teams SDK (Python) |
| https://github.com/microsoft/botbuilder-python | Legacy Bot Framework (still useful for reference) |
| https://github.com/supermemoryai/python-sdk | Supermemory Python SDK |
| https://github.com/supermemoryai/supermemory-mcp | Supermemory MCP server |
| https://github.com/modelcontextprotocol/python-sdk | MCP Python SDK |

---

---

## MISSING FROM INITIAL RESEARCH — Found After POC Review

After reviewing all 39 n8n workflows, these POC features need **additional research** because they have non-trivial production equivalents:

### 5.1 Conflict Resolution Engine (CRITICAL)

The POC has a **full conflict resolution system** that's way more complex than just "pick the newest memory":
- Conflict groups (metadata.conflict_group)
- Multi-dimension scoring: type rank → recency → confidence → source authority → stable fallback
- Value-signature dedup (same content = non-meaningful conflict)
- Manual override system (set/get/clear/list) with advisory locks
- Audit logging (conflict_audit_log + conflict_audit_snapshot)
- Winner status sync back to Supermemory (active/deprecated)
- Tie detection → needs_human flag

**What to search:**
- "conflict resolution patterns distributed systems Python"
- "event sourcing conflict resolution"
- "advisory locks asyncpg Python" (for override races)
- "deterministic scoring algorithm Python dataclass"

### 5.2 Draft Queue / Human-in-the-Loop (CRITICAL)

The POC has a full draft review system:
- Facts/rules without source_id or as_of → auto-demoted to `status=draft`
- Draft queue: list, approve, reject, update operations
- Interactive review cards (approve/reject/update in chat)
- Selection by customId OR list index

**What to search:**
- "human in the loop AI agent Python"
- "approval queue pattern async Python"
- "Adaptive Cards action handling Teams bot" (this replaces Slack interactive blocks)

### 5.3 Email Surface (DEFERRED but still relevant)

The POC has a full email pipeline:
- Sender → client deterministic lookup (email match, then domain fallback)
- Campaign resolution (explicit in text → current active → upcoming)
- Confidence-based auto-send vs human approval queue
- Token-hashed approval links with 24h expiry
- Gmail bridge polling

**What to search:**
- "Azure Logic Apps email trigger" (replaces Gmail bridge)
- "Microsoft Graph API send email Python" (replaces SMTP)
- "email approval workflow Azure"
- NOTE: This might stay as-is or move to Phase 3. Check with Anna.

### 5.4 Slack Thread Context → Teams Thread Context

The POC maintains rich thread state:
- `slack_thread_context` (shared per-thread JSON)
- `slack_agent_context` (per-agent per-thread JSON)
- Last user text + last reply text per agent
- Vague follow-up detection for same-thread continuity
- Event deduplication (team_id + event_id)

**What to search:**
- "Teams bot conversation reference Python"
- "Teams bot proactive messages Python"
- "Teams conversation state management M365 Agents SDK"
- "Teams thread context persistence"

### 5.5 Guardrails + Dedupe Pipeline

The POC write path has 3 stages before hitting Supermemory:
1. **Validation** — memory_type ∈ {fact,rule,agent,vector}, source_type ∈ {slack,chat,email,doc,api,human,seed}
2. **Guardrails** — demotes to draft if missing source_id/as_of, normalizes dates
3. **Dedupe** — generates deterministic customId, ensures conflict_group exists

**What to search:**
- "pydantic validator custom Python" (replace n8n code nodes with Pydantic models)
- "deterministic ID generation Python hashlib"
- "data validation pipeline pattern Python"

### 5.6 Memory Extraction from LLM Responses

After the LLM responds, a second LLM call extracts new memories:
- Strict JSON schema output (shouldWrite, items[])
- Max 2 extracted items per response
- Metadata enrichment (memory_type, source_type, confidence, etc.)
- Mode-dependent write suppression (search/review = no writes)

**What to search:**
- "structured output LLM JSON Python"
- "Claude structured output tool_use"
- "pydantic model from LLM response"

### 5.7 Context Window Token Budgeting

POC uses char-based budgets (8000 chars, 8 chunks max). Prod needs real token counting:
- Claude Token Counting API: `client.beta.messages.count_tokens()`
- Rolling summarization when >75% capacity
- Per-agent scoped context (2-3 sentence summary, not full history)

**What to search:**
- "Claude token counting API Python anthropic"
- "rolling summarization conversation history LLM"
- "context window management multi-agent"

### 5.8 Asana Integration (TASKR)

TASKR creates tasks in Asana with:
- Natural language → title/owner/due/project/priority parsing
- Pending task state when required fields missing (multi-turn)
- Mock fallback when Asana unavailable

**What to search:**
- "Asana API Python create task"
- "asana python client library" (pip install asana)

### 5.9 Google Docs/Drive Integration (CAMPA)

CAMPA creates campaign briefs:
- Google Docs API for doc creation
- Template-based pre-filling
- Mock fallback when unavailable

**What to search:**
- "Google Docs API Python create document"
- "google-api-python-client docs"
- "Google Drive API Python upload"

### 5.10 Structured Logging (NEW in Prod, not in POC)

POC has zero structured logging. Use structlog for machine-parseable JSON logs.

**What to search:**
- "structured logging Python structlog"
- "structlog JSON Python FastAPI"

---

## POC → Prod Feature Completeness Matrix

| POC Feature | In Research Guide? | Extra Research Needed? |
|---|---|---|
| Supermemory search/write | ✅ Yes | No |
| Supermemory MCP | ✅ Yes | No |
| MS Agent Framework | ✅ Yes | No |
| M365 Agents SDK (Teams) | ✅ Yes | No |
| Adaptive Cards | ✅ Yes | No |
| Azure Bot Registration | ✅ Yes | No |
| Fan-out orchestration | ✅ Yes | No |
| Intent routing | ✅ Yes | No |
| Conflict resolution engine | ❌ Missing | ✅ Added above |
| Draft queue / human review | ❌ Missing | ✅ Added above |
| Thread context persistence | ❌ Missing | ✅ Added above |
| Guardrails + dedupe pipeline | ❌ Missing | ✅ Added above |
| Memory extraction from LLM | ❌ Missing | ✅ Added above |
| Token budgeting | ❌ Missing | ✅ Added above |
| Email surface | ❌ Missing | ✅ Added above |
| Asana integration | ❌ Missing | ✅ Added above |
| Google Docs integration | ❌ Missing | ✅ Added above |
| Observability (Langfuse + OTel) | ⏭️ Deferred to Phase 3 | N/A |
| Redis semantic cache | ⏭️ Deferred to Phase 3 | N/A |
| Azure Key Vault | ⏭️ Deferred to Phase 3 | N/A |
| Evaluation framework (Langfuse evals) | ⏭️ Deferred to Phase 3 | N/A |
| Pydantic settings/config | ✅ Yes | No |
| Azure deployment | ✅ Yes | No |

---

*Generated: March 2026 — Pre-project research for OrgMind Phase 2*
