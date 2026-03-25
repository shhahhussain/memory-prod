"""Sprint 1 — M365 Agents SDK Echo Bot Tests"""
import pytest


async def test_echo_bot_responds_to_message_activity():
    """Bot echoes back user message text on message activity."""

async def test_echo_bot_ignores_non_message_activities():
    """Bot does not respond to typing or conversationUpdate activities."""

async def test_bot_returns_200_on_valid_activity():
    """HTTP handler returns 200 status for valid Bot Framework activity."""
