# Sprint 1 — Setup & Scaffolding Research

**Milestone:** M1 — Setup & Scaffolding (10-12h)
**Focus:** Project setup, Azure registration, framework hello-world, dev environment

---

## What to Research

### 1. Microsoft Agent Framework (Python) — Basics
- Overview: https://learn.microsoft.com/en-us/agent-framework/overview/
- Quickstart: https://learn.microsoft.com/en-us/agent-framework/tutorials/quick-start
- RC announcement: https://devblogs.microsoft.com/foundry/microsoft-agent-framework-reaches-release-candidate/

**Repos to clone and run:**
- https://github.com/microsoft/agent-framework
- https://github.com/microsoft/Agent-Framework-Samples (start with hello-world)

**Install:**
```bash
pip install agent-framework --pre
```

**Key concepts:**
- Agents created via `.as_agent()` — NO class inheritance
- `WorkflowBuilder` for sequential chains
- `ConcurrentBuilder` for parallel fan-out

---

### 2. M365 Agents SDK (Python) — Basics
- Overview: https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/agents-sdk-overview
- Quickstart: https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/quickstart
- Migration from Bot Framework: https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/bf-migration-python
- Repo: https://github.com/microsoft/Agents-for-python

**Install:**
```bash
pip install microsoft-agents-hosting-core
pip install microsoft-agents-hosting-aiohttp
pip install microsoft-agents-hosting-teams
pip install microsoft-agents-activity
pip install microsoft-agents-authentication-msal
```

> **NOTE:** Imports use underscores: `microsoft_agents`, NOT dots.

---

### 3. Azure Bot Registration
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

---

### 4. Pydantic Settings (Config Management)
- Replace n8n credential nodes with proper Python config
- Search: "pydantic-settings BaseSettings env file Python"

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    anthropic_api_key: str
    supermemory_api_key: str
    microsoft_app_id: str
    microsoft_app_password: str
    postgres_url: str
    agent_timeout_seconds: float = 30.0

    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")
```

---

### 5. Project Structure
- Search: "Python monorepo project structure FastAPI"
- Search: "Python project layout src layout 2026"

**Target layout (from arch doc):**
```
orgmind/
├── app.py                  # FastAPI + M365 SDK entrypoint
├── config/                 # Pydantic settings
├── agents/                 # MINDY, FINDR, TASKR, CAMPA
├── services/               # Supermemory, PG wrappers
├── models/                 # Pydantic data models
├── routes/                 # /api/messages etc.
├── tests/
└── requirements.txt
```

---

### 6. Supermemory Python SDK — Verify Access
- Docs: https://supermemory.ai/docs/intro
- SDK: https://supermemory.ai/docs/integrations/supermemory-sdk
- Console: https://console.supermemory.ai

```bash
pip install supermemory
```

Quick smoke test:
```python
from supermemory import AsyncSupermemory
client = AsyncSupermemory(api_key="sm_your_key")
response = await client.search.memories(q="test", container_tags=["orgmind-poc"])
```

---

### 7. Local Dev Tunnel (ngrok)
- Teams needs a public HTTPS URL even for local dev
- Search: "ngrok Teams bot local development"
- Alternative: Azure Dev Tunnels (`devtunnel`)

---

## Checklist
- [ ] Clone Agent Framework Samples repo, run hello-world
- [ ] Clone Agents-for-python repo, run echo bot sample
- [ ] Register Azure bot (even if throwaway for practice)
- [ ] Set up `.env` with all keys
- [ ] Verify Supermemory SDK connection
- [ ] Set up ngrok or dev tunnel
- [ ] Create project folder structure
