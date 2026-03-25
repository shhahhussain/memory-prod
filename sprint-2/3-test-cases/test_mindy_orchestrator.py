"""Sprint 2 — MINDY Orchestrator Tests"""
import pytest


async def test_fan_out_dispatches_to_correct_agents():
    """SEARCH intent dispatches to FINDR only. MULTI dispatches to multiple."""

async def test_fan_out_collects_partial_on_timeout():
    """1 agent times out → other 2 results collected, timeout agent marked failed."""

async def test_fan_out_all_fail_returns_graceful_error():
    """All agents fail → returns user-friendly error, no 500."""

async def test_synthesizer_excludes_failed_agents():
    """LLM prompt includes only successful agent data + 'MISSING DATA' for failed."""

async def test_synthesizer_tells_llm_not_to_fabricate():
    """Prompt contains 'Do NOT fabricate' when agents are missing."""

async def test_per_user_lock_serializes_messages():
    """Two concurrent messages from same user_id process sequentially."""

async def test_different_users_run_concurrently():
    """Messages from user_A and user_B run in parallel, not serialized."""

async def test_agents_receive_immutable_context():
    """Agent modifying its context dict does NOT affect other agents' copies."""
