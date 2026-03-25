"""Sprint 2 — TASKR Agent Tests"""
import pytest


async def test_taskr_create_calls_nocodb_post():
    """Create task sends POST to NocoDB with correct payload shape."""

async def test_taskr_list_filters_by_project_id():
    """List tasks sends GET with project_id filter parameter."""

async def test_taskr_idempotency_key_prevents_duplicate():
    """Same task data generates same idempotency key → NocoDB deduplicates."""

async def test_taskr_handles_nocodb_502_html_error():
    """NocoDB returning HTML 502 raises APIError, not JSONDecodeError."""

async def test_taskr_handles_nocodb_timeout():
    """NocoDB timeout raises descriptive error, not raw TimeoutError."""
