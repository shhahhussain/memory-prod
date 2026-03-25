# Regression Test Pack Port (Code-Ready Reference)

> For Claude Code: Port the POC's test suite to pytest.

## POC Test Categories (from orgmind-test-suite.md)

1. **Search path**: query → SM search → conflict resolution → context pack → response
2. **Write path**: content → guardrails → dedupe → SM write
3. **Approve/reject**: customId lookup → status update → write
4. **Mode enforcement**: search=no write, write=force write, auto=LLM decides

## Key Test Cases

```python
class TestSearchPath:
    async def test_basic_search(self, mock_supermemory):
        # Setup mock results, call FINDR, verify response includes citations
        pass

    async def test_conflict_resolution(self):
        from orgmind.tools.conflict import resolve_conflicts, MemoryCandidate
        candidates = [
            MemoryCandidate(id="a", content="Budget $35K", similarity=0.9, metadata={"conflict_group": "budget", "as_of": "2026-01-28", "confidence": 0.88, "source_authority": 3}),
            MemoryCandidate(id="b", content="Budget $50K", similarity=0.9, metadata={"conflict_group": "budget", "as_of": "2026-01-30", "confidence": 0.95, "source_authority": 2}),
        ]
        result = resolve_conflicts(candidates)
        assert len(result) == 1
        assert result[0].id == "b"  # More recent wins

class TestWritePath:
    async def test_guardrails_draft_on_missing_source(self):
        from orgmind.tools.guardrails import apply_guardrails, WritePayload
        payload = WritePayload(content="Test fact", metadata={"memory_type": "fact"})
        result = apply_guardrails(payload)
        assert result.effective_status == "draft"
        assert "missing_source_id_or_as_of" in result.guardrail_flags

class TestModeEnforcement:
    async def test_search_mode_no_write(self):
        from orgmind.tools.extraction import extract_memories
        result = await extract_memories("query", "response", mode="search")
        assert result.should_write is False
```

## IMPORTANT NOTES
1. Port ALL test cases from POC's `orgmind-test-suite.md`
2. Conflict resolution tests should use the exact seed data scenarios
3. Mock Supermemory and LLM calls — test logic, not APIs
