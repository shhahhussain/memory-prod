# Sprint 5 — Testing & Deployment Research

**Milestone:** M5 — Testing & Deployment (12-16h)
**Focus:** Evaluation framework, CI/CD, Azure deployment, end-to-end testing

---

## What to Research

### 1. CI/CD Pipeline

**GitHub Actions for Azure App Service:**
```yaml
name: Deploy to Azure
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      - uses: azure/webapps-deploy@v3
        with:
          app-name: orgmind-bot
          package: .
```

**Search queries:**
- "GitHub Actions deploy Azure App Service Python"
- "Azure CLI deploy webapp zip Python"
- "GitHub Actions pytest Azure"

---

### 2. Azure App Service Deployment

```bash
# Create resources
az group create --name orgmind-rg --location eastus
az appservice plan create --name orgmind-plan --resource-group orgmind-rg --sku B1 --is-linux
az webapp create --name orgmind-bot --resource-group orgmind-rg --plan orgmind-plan --runtime "PYTHON:3.11"

# Set env vars
az webapp config appsettings set --name orgmind-bot --resource-group orgmind-rg \
  --settings MicrosoftAppId="<id>" MicrosoftAppPassword="<secret>" \
  SUPERMEMORY_API_KEY="<key>" ANTHROPIC_API_KEY="<key>"

# Deploy
zip -r deploy.zip . -x ".git/*" "__pycache__/*" ".env"
az webapp deploy --name orgmind-bot --resource-group orgmind-rg --src-path deploy.zip --type zip
```

**Search queries:**
- "Azure App Service Python deploy best practices"
- "Azure App Service startup command Python FastAPI"
- "Azure App Service health check endpoint"

---

### 3. Testing Strategy

**Unit tests:**
- Each agent function in isolation
- Guardrails/dedupe validators
- Conflict resolver scoring
- Intent router keyword matching

**Integration tests:**
- Supermemory search/write round-trip
- PostgreSQL queries
- Asana/GDocs API calls (with mocks)

**End-to-end tests:**
- Full conversation flows (message → MINDY → agents → response)
- Draft review flow (write → review → approve)
- Conflict detection + override flow

**Search queries:**
- "pytest async Python asyncio"
- "pytest mock httpx async"
- "pytest fixtures async database"
- "Teams bot testing framework Python"

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_findr_returns_citations():
    mock_supermemory = AsyncMock()
    mock_supermemory.search.memories.return_value = MockSearchResponse(results=[...])

    findr = FindrAgent(memory_client=mock_supermemory)
    result = await findr.research("What is Acme's Q1 budget?")

    assert result.citations
    assert result.confidence > 0.5
```

---

### 4. POC Regression Packs to Port

These exist in POC and should become automated tests:
- `tests/single-agent-chat-demo-regression-pack.json`
- `tests/sprint-4-email-regression-pack.json`
- `tests/sprint-5-post-action-regression-pack.json`

**Each test case has:**
- Input text
- Expected mode
- Expected behavior (writes, no-writes, citations, etc.)

Port these to pytest parametrize:
```python
@pytest.mark.parametrize("test_case", load_regression_pack("chat-regression.json"))
@pytest.mark.asyncio
async def test_regression(test_case):
    result = await mindy.handle(test_case["input"])
    assert result.mode == test_case["expected_mode"]
```

---

### 5. Health Check & Monitoring

```python
@app.get("/health")
async def health():
    checks = {
        "supermemory": await check_supermemory(),
        "postgres": await check_postgres(),
    }
    all_ok = all(v["ok"] for v in checks.values())
    return {"status": "healthy" if all_ok else "degraded", "checks": checks}
```

**Search queries:**
- "FastAPI health check endpoint pattern"
- "Azure App Service health check configuration"
- "liveness readiness probe Python"

---

### 6. Post-Action Review (PAR) System

POC had:
- `PAR - Action Logging Service` → writes to `agent_action_log`
- `PAR - Feedback Loop Integration` → thumbs up/down → memory confidence update
- `PAR - Memory Consolidation Job` → nightly summarize stale facts

**Search queries:**
- "scheduled job Python Azure" (for nightly consolidation)
- "Azure Functions timer trigger Python"
- "APScheduler async Python"

---

## Checklist
- [ ] Write pytest suite for each agent
- [ ] Write integration tests for Supermemory + PG
- [ ] Set up GitHub Actions CI pipeline
- [ ] Deploy to Azure App Service (staging)
- [ ] Configure health check endpoint
- [ ] Sideload Teams app in test tenant
- [ ] Run full end-to-end conversation test in Teams
- [ ] Port PAR action logging
- [ ] Set up nightly consolidation job
