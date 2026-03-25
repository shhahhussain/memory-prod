"""Sprint 1 — Supermemory SDK Smoke Tests"""
import pytest


async def test_supermemory_client_initializes_with_api_key():
    """AsyncSupermemory client creates without error."""

async def test_supermemory_search_returns_list():
    """search() returns a list (possibly empty) without error."""

async def test_supermemory_write_and_read_roundtrip():
    """Write a memory, search for it, verify content matches."""

async def test_supermemory_client_timeout_raises():
    """Client with 0.001s timeout raises TimeoutError, not hang."""
