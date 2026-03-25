"""Sprint 3 — Thread Context Persistence Tests"""
import pytest


async def test_context_keyed_by_user_id():
    """Same user in different channels shares user-level context."""

async def test_thread_context_separate_per_conversation():
    """Thread-level context is per conversation_id."""

async def test_context_persisted_to_storage():
    """Context stored in persistent storage (BlobStorage/CosmosDB), not instance-local dict."""

async def test_context_survives_instance_restart():
    """Context readable from storage after simulated restart."""
