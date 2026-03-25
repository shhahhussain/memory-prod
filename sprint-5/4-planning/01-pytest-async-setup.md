# Topic: pytest — Async Test Setup

**Time:** 15 min
**Goal:** Set up pytest for testing async agent code

---

## What to Search
- "pytest asyncio Python setup"
- "pytest async fixtures"
- "pytest-asyncio auto mode"

## Install
```bash
pip install pytest pytest-asyncio
```

## Config (pyproject.toml)
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # All async tests auto-detected
```

## Basic Async Test
```python
import pytest
from unittest.mock import AsyncMock

async def test_findr_returns_citations():
    mock_memory = AsyncMock()
    mock_memory.search.documents.return_value = MockResponse(results=[
        MockResult(chunk="Acme Q1 budget is $50K", similarity=0.92),
    ])

    findr = FindrAgent(memory_client=mock_memory, llm_client=AsyncMock())
    result = await findr.research("Acme budget")

    assert result.citations
    assert result.confidence > 0.5
    mock_memory.search.documents.assert_called_once()

async def test_guardrails_demotes_to_draft():
    metadata = MemoryMetadata(
        memory_type=MemoryType.FACT,
        source_type=SourceType.CHAT,
        # Missing source_id and as_of!
    )
    assert metadata.status == "draft"
    assert metadata.guardrail_reason == "missing_source_id_or_as_of"
```

## Fixtures
```python
@pytest.fixture
async def db():
    database = Database()
    await database.connect("postgresql://test:test@localhost:5432/orgmind_test")
    yield database
    await database.close()

@pytest.fixture
def mock_supermemory():
    return AsyncMock(spec=AsyncSupermemory)
```

## What to Understand
- [ ] `asyncio_mode = "auto"` means no need for `@pytest.mark.asyncio` decorator
- [ ] `AsyncMock` mocks async functions automatically
- [ ] Test Pydantic models directly (guardrails, validation)
- [ ] Use fixtures for shared setup (db connection, mock clients)
