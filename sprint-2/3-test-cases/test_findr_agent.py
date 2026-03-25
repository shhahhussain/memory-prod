"""Sprint 2 — FINDR Agent Tests"""
import pytest


async def test_findr_calls_supermemory_with_query():
    """FINDR passes user query to supermemory.search() with correct mode."""

async def test_findr_empty_results_returns_no_memories_message():
    """0 search results → response contains 'No relevant memories found'."""

async def test_findr_filters_by_min_score():
    """Results with score < 0.65 are excluded from context."""

async def test_findr_context_pack_respects_token_budget():
    """Packed context total tokens <= max_context_tokens."""

async def test_findr_filter_schema_rejects_unknown_keys():
    """Filter with extra keys raises ValidationError (extra='forbid')."""

async def test_findr_formats_results_with_score_and_metadata():
    """Each memory in context includes [score=X | as_of=Y] prefix."""
