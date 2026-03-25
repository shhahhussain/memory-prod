"""Sprint 3 — Adaptive Cards Tests"""
import pytest


# --- Invoke Activity ---

async def test_card_action_routed_to_invoke_handler():
    """Adaptive Card button click → on_invoke_activity, not on_message."""

async def test_invoke_returns_200_immediately():
    """Invoke handler returns InvokeResponse(status=200) within budget."""

async def test_card_action_payload_validated():
    """Card action data validated through Pydantic model."""

async def test_card_action_invalid_id_rejected():
    """memory_id with injection chars raises ValidationError."""


# --- Draft Review Card ---

def test_draft_review_card_has_approve_reject_buttons():
    """Draft review card JSON contains Approve and Reject actions."""

def test_draft_review_card_includes_memory_content():
    """Card body shows the memory content for review."""


# --- Conflict Picker Card ---

def test_conflict_card_shows_all_conflicting_memories():
    """Card lists all memories in the conflict group."""

def test_conflict_card_includes_version_in_action_data():
    """Action.Submit data includes version for optimistic locking."""
