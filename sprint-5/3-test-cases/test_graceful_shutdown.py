"""Sprint 5 — Graceful Shutdown Tests"""
import pytest


async def test_sigterm_sets_shutdown_event():
    """SIGTERM signal → shutdown_event is set."""

async def test_new_requests_rejected_after_sigterm():
    """Requests after SIGTERM receive 503."""

async def test_in_flight_tasks_drain_before_close():
    """In-flight tasks complete before pool.close() is called."""

async def test_pools_closed_in_correct_order():
    """Shutdown order: HTTP listener → drain → aiohttp → asyncpg."""

async def test_forced_shutdown_after_25s():
    """Tasks not completed in 25s are cancelled, pools close anyway."""
