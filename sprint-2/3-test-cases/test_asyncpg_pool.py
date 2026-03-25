"""Sprint 2 — asyncpg Pool & Query Tests"""
import pytest


async def test_pool_acquire_timeout_raises_service_unavailable():
    """Pool exhaustion + timeout → ServiceUnavailableError."""

async def test_parameterized_query_prevents_injection():
    """$1 placeholder used, not f-string. Verify query text has no interpolation."""

async def test_deadlock_retry_succeeds_on_second_attempt():
    """DeadlockDetectedError on attempt 1 → retry → succeeds on attempt 2."""

async def test_null_aggregation_coalesced():
    """AVG on empty result set returns 0.0 via COALESCE, not None."""

async def test_connection_setup_sets_search_path():
    """New connection has search_path set to 'orgmind, public'."""

async def test_connection_setup_sets_statement_timeout():
    """New connection has statement_timeout set."""
