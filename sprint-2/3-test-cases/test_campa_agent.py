"""Sprint 2 — CAMPA Agent Tests"""
import pytest


async def test_campa_draft_includes_context():
    """Draft prompt includes Supermemory search results as context."""

async def test_campa_empty_context_explicit_message():
    """No search results → prompt says 'no context available', not silent."""

async def test_campa_respects_token_budget():
    """Generated draft request stays within max_tokens limit."""
