# Topic: Python Project Structure for OrgMind

**Time:** 15-20 min
**Goal:** Decide on folder layout before writing any code

---

## What to Search
- "Python project structure FastAPI 2026"
- "Python monorepo src layout"
- "FastAPI project layout best practices"

## Target Structure
```
orgmind/
├── app.py                          # FastAPI entrypoint + M365 SDK setup
├── config/
│   ├── __init__.py
│   └── settings.py                 # Pydantic Settings
├── agents/
│   ├── __init__.py
│   ├── base.py                     # BaseAgent interface
│   ├── mindy.py                    # MINDY orchestrator
│   ├── findr.py                    # FINDR research agent
│   ├── taskr.py                    # TASKR project agent
│   └── campa.py                    # CAMPA campaign agent
├── services/
│   ├── __init__.py
│   ├── memory.py                   # Supermemory client wrapper
│   ├── postgres.py                 # asyncpg pool + queries
│   ├── context.py                  # Context window management
│   ├── conflict.py                 # Conflict resolution engine
│   ├── guardrails.py               # Write validation + guardrails
│   ├── dedupe.py                   # Dedupe key builder
│   └── context.py                  # Context window management
├── models/
│   ├── __init__.py
│   ├── memory.py                   # Memory, MemoryMetadata, WritePayload
│   ├── intent.py                   # Intent, RoutingDecision
│   ├── agent.py                    # AgentRequest, AgentResult
│   └── conflict.py                 # ConflictGroup, ConflictResolution
├── routes/
│   ├── __init__.py
│   └── messages.py                 # POST /api/messages handler
├── cards/
│   ├── __init__.py
│   ├── draft_review.py             # Draft review Adaptive Card
│   ├── conflict_picker.py          # Conflict override Adaptive Card
│   └── progress.py                 # Progress update card
├── tests/
│   ├── conftest.py
│   ├── test_mindy.py
│   ├── test_findr.py
│   ├── test_conflict.py
│   ├── test_guardrails.py
│   └── regression/
│       └── chat_regression.json    # Ported from POC
├── migrations/
│   └── 001_initial.sql
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

## What to Understand
- [ ] Why `services/` is separate from `agents/` (services are reusable, agents call services)
- [ ] Why `models/` holds Pydantic models (shared data contracts)
- [ ] Why `cards/` is separate (Adaptive Card JSON builders)
- [ ] How this maps to the POC's n8n folder structure (01-Surfaces → routes/, 02-Orchestrators → agents/mindy.py, 03-Services → services/, 04-Agents → agents/)
