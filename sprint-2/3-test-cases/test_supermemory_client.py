"""Sprint 2 — Supermemory Client Tests"""
import pytest


async def test_write_idempotent_on_timeout_retry():
    """Timeout on write → retry with same customId → no duplicate (upsert)."""

async def test_search_results_sorted_by_score():
    """Returned results ordered by score descending."""

async def test_filter_rejects_unknown_keys():
    """Filter with extra key raises ValidationError (extra='forbid')."""

async def test_rate_limit_429_retries_with_retry_after():
    """429 response → waits Retry-After seconds → retries successfully."""

async def test_search_zero_results_returns_empty_list():
    """No matches → returns [] not None."""
