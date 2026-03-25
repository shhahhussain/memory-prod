# Topic: Port POC Regression Packs to pytest

**Time:** 20 min
**Goal:** Turn POC's JSON test cases into automated Python tests

---

## What to Search
- "pytest parametrize JSON test data"
- "data-driven testing pytest"

## POC Regression Packs
- `tests/single-agent-chat-demo-regression-pack.json`
- `tests/sprint-4-email-regression-pack.json`
- `tests/sprint-5-post-action-regression-pack.json`

## Pattern
```python
import json
import pytest

def load_regression_pack(filename: str) -> list[dict]:
    with open(f"tests/regression/{filename}") as f:
        return json.load(f)["test_cases"]

@pytest.mark.parametrize("case", load_regression_pack("chat-regression.json"))
async def test_chat_regression(case, mock_supermemory, mock_llm):
    # Setup mocks based on test case
    mock_supermemory.search.documents.return_value = MockResponse(
        results=case.get("mock_search_results", [])
    )

    # Execute
    result = await mindy.handle(
        text=case["input"],
        context={"actor": "test", "container_tag": "orgmind-test"},
    )

    # Assert
    if "expected_mode" in case:
        assert result.mode == case["expected_mode"]
    if "expected_writes" in case:
        assert result.writes == case["expected_writes"]
    if "should_cite" in case:
        assert bool(result.citations) == case["should_cite"]
```

## Test Case Format
```json
{
  "test_cases": [
    {
      "name": "search_acme_budget",
      "input": "What is Acme's Q1 budget?",
      "expected_mode": "search",
      "expected_writes": 0,
      "should_cite": true
    },
    {
      "name": "write_new_fact",
      "input": "write: Nike Q2 spend is $3.1M",
      "expected_mode": "write",
      "expected_writes": 1
    }
  ]
}
```

## What to Understand
- [ ] `@pytest.mark.parametrize` runs the same test with different data
- [ ] Each POC test case becomes a parametrized test
- [ ] Mock external services (Supermemory, Claude, Asana)
- [ ] Test behavior, not implementation (mode, writes, citations)
