"""Sprint 3 — Proactive Messages Tests"""
import pytest


async def test_proactive_message_sends_successfully():
    """Valid ConversationReference → message delivered."""

async def test_stale_ref_invalidated_on_403():
    """403 error → conversation ref marked valid=false in DB."""

async def test_stale_ref_invalidated_on_404():
    """404 error → conversation ref marked valid=false in DB."""

async def test_proactive_does_not_retry_on_stale():
    """Stale ref error does not trigger retry loop."""
