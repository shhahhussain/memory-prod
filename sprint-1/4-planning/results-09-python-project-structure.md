# Python Project Structure (Code-Ready Reference)

> For Claude Code: Use this as the canonical project layout for OrgMind production code.

## Recommended Project Structure

```
orgmind/
├── pyproject.toml              # Project metadata, dependencies
├── .env                        # Local env vars (git-ignored)
├── .env.example                # Template for env vars (committed)
├── .gitignore
├── README.md
│
├── src/
│   └── orgmind/
│       ├── __init__.py
│       ├── app.py              # Entry point — aiohttp server + AgentApplication
│       ├── server.py           # start_server() function
│       ├── settings.py         # OrgMindSettings (pydantic-settings)
│       │
│       ├── agents/             # Agent definitions
│       │   ├── __init__.py
│       │   ├── mindy.py        # MINDY — orchestrator (intent routing + synthesis)
│       │   ├── findr.py        # FINDR — research/search specialist
│       │   ├── taskr.py        # TASKR — task/project management
│       │   └── campa.py        # CAMPA — campaign/doc drafting
│       │
│       ├── tools/              # Agent tools (functions agents can call)
│       │   ├── __init__.py
│       │   ├── memory_tools.py # Supermemory search/write tools
│       │   ├── task_tools.py   # NocoDB/project management tools
│       │   └── doc_tools.py    # Google Docs/document tools
│       │
│       ├── memory/             # Supermemory integration layer
│       │   ├── __init__.py
│       │   ├── client.py       # AsyncSupermemory wrapper
│       │   ├── search.py       # Search with filters, context building
│       │   └── ingest.py       # Document ingestion, dedup
│       │
│       ├── teams/              # Teams-specific handlers
│       │   ├── __init__.py
│       │   ├── handlers.py     # Message handlers, @mention parsing
│       │   ├── cards.py        # Adaptive Card builders
│       │   └── proactive.py    # Proactive messaging
│       │
│       ├── routing/            # Intent routing
│       │   ├── __init__.py
│       │   ├── classifier.py   # Keyword + LLM intent classification
│       │   └── models.py       # Intent, RoutingDecision Pydantic models
│       │
│       └── shared/             # Shared utilities
│           ├── __init__.py
│           ├── models.py       # Shared Pydantic models
│           ├── logging.py      # Structured logging setup
│           └── exceptions.py   # Custom exceptions
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Shared fixtures
│   ├── test_agents/
│   │   ├── test_mindy.py
│   │   ├── test_findr.py
│   │   ├── test_taskr.py
│   │   └── test_campa.py
│   ├── test_routing/
│   │   └── test_classifier.py
│   ├── test_memory/
│   │   └── test_search.py
│   └── test_teams/
│       └── test_handlers.py
│
├── manifests/                  # Teams app manifests
│   ├── manifest.json
│   ├── color.png
│   └── outline.png
│
└── scripts/
    ├── smoke_test.py           # End-to-end smoke test
    └── seed_memory.py          # Seed Supermemory with test data
```

## pyproject.toml

```toml
[project]
name = "orgmind"
version = "0.1.0"
description = "OrgMind — AI agent memory framework for organizational knowledge"
requires-python = ">=3.11"
dependencies = [
    # Agent Framework (AI logic)
    "agent-framework-anthropic",

    # M365 Agents SDK (Teams surface)
    "microsoft-agents-hosting-aiohttp",
    "microsoft-agents-hosting-teams",
    "microsoft-agents-authentication-msal",

    # Memory
    "supermemory>=3.30",

    # Config
    "pydantic-settings>=2.0",
    "python-dotenv>=1.0",

    # Database
    "asyncpg>=0.29",

    # Logging
    "structlog>=24.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=5.0",
    "black>=24.0",
    "ruff>=0.3",
    "mypy>=1.8",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.black]
line-length = 100

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]

[tool.mypy]
python_version = "3.11"
strict = true
```

## .env.example

```bash
# LLM
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_CHAT_MODEL_ID=claude-sonnet-4-5-20250929
GEMINI_API_KEY=...

# Memory
SUPERMEMORY_API_KEY=sm_...

# Teams Bot
TEAMS__APP_ID=
TEAMS__APP_PASSWORD=
TEAMS__TENANT_ID=common

# Infrastructure
PORT=3978
LOG_LEVEL=INFO
POSTGRES_URL=postgresql://user:pass@localhost:5432/orgmind

# Agent Config
LLM__MAX_TOKENS=4096
LLM__TEMPERATURE=0.7
MEMORY__THRESHOLD=0.5
MEMORY__RERANK=true
```

## .gitignore Additions

```gitignore
# Env
.env
.env.local
.env.production

# Python
__pycache__/
*.pyc
.venv/
dist/
*.egg-info/

# IDE
.vscode/
.idea/

# OS
.DS_Store
```

## Entry Point Pattern

```python
# src/orgmind/app.py
from dotenv import load_dotenv
load_dotenv()  # MUST be called before Settings()

from orgmind.settings import get_settings
from orgmind.server import start_server
from orgmind.agents.mindy import create_mindy_app

settings = get_settings()
agent_app = create_mindy_app(settings)

if __name__ == "__main__":
    start_server(agent_app, auth_configuration=None)
```

## IMPORTANT NOTES FOR CODE GENERATION

1. **Use `src/` layout** — prevents import ambiguity
2. **`load_dotenv()` MUST be called before `Settings()`** — Agent Framework doesn't auto-load .env
3. **One agent per file** in `agents/` — keeps things clean
4. **Tools are separate from agents** — tools in `tools/`, agents in `agents/`
5. **Teams-specific code isolated** in `teams/` — keeps surface layer separate from AI logic
6. **`asyncio_mode = "auto"`** in pytest — all async tests work without decorators
7. **Use `pyproject.toml`** — no `setup.py` or `requirements.txt` needed
8. **Keep manifests in `manifests/`** — separate from code
