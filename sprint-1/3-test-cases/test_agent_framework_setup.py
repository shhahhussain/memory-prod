"""Sprint 1 — Agent Framework Setup Tests"""
import pytest


# --- AnthropicClient Init ---

async def test_anthropic_client_initializes_with_valid_api_key():
    """AnthropicClient creates successfully with a valid SecretStr key."""

async def test_anthropic_client_raises_on_empty_api_key():
    """Empty API key raises ConfigurationError at init, not at first call."""

async def test_anthropic_client_rejects_invalid_model_id():
    """Unknown model_id raises ConfigurationError with list of valid models."""


# --- Agent Creation ---

async def test_agent_created_with_name_and_instructions():
    """AnthropicClient.as_agent() returns agent with correct name and instructions."""

async def test_agent_tool_decorator_registers_tool():
    """@tool decorator registers function as callable tool on the agent."""
