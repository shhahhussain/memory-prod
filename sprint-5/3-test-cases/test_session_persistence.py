"""Sprint 5 — Multi-Instance Session Tests"""
import pytest


async def test_session_stored_in_persistent_storage():
    """ConversationState saved to persistent storage (BlobStorage/CosmosDB), not local dict."""

async def test_session_readable_from_different_instance():
    """State written by instance A readable by instance B (via shared storage)."""

async def test_session_expires_after_ttl():
    """Session has TTL, not permanent."""

async def test_session_roundtrip_preserves_data():
    """Save → load → data matches (Pydantic serialization roundtrip)."""
