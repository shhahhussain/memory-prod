# pytest Async Setup (Code-Ready Reference)

> For Claude Code: Testing setup for async OrgMind code.

## Installation

```bash
pip install pytest pytest-asyncio pytest-cov
```

## pyproject.toml

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

## Fixtures

```python
# tests/conftest.py
import pytest
from supermemory import AsyncSupermemory
from unittest.mock import AsyncMock

@pytest.fixture
def mock_supermemory():
    client = AsyncMock(spec=AsyncSupermemory)
    client.search.execute = AsyncMock(return_value=MockSearchResult([]))
    client.documents.add = AsyncMock(return_value=MockAddResult("doc-123", "queued"))
    return client

@pytest.fixture
def settings():
    from orgmind.settings import OrgMindSettings
    return OrgMindSettings(
        anthropic_api_key="test-key",
        supermemory_api_key="sm_test",
    )
```

## Test Example

```python
# tests/test_routing/test_classifier.py
async def test_keyword_route_search():
    from orgmind.routing.classifier import keyword_route, Intent
    result = keyword_route("search: Nike budget")
    assert result is not None
    assert result.intent == Intent.SEARCH
    assert result.tier == "keyword"

async def test_keyword_route_ambiguous():
    result = keyword_route("hey there")
    assert result is None  # Falls through to LLM
```

## IMPORTANT NOTES
1. `asyncio_mode = "auto"` — no need for `@pytest.mark.asyncio` on every test
2. Mock external services (Supermemory, LLM) — don't call real APIs in tests
3. Test routing logic extensively — it's the critical path
