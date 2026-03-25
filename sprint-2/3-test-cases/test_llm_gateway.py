"""Sprint 2 — LLM Gateway Tests"""
import pytest


# --- Claude Success ---

async def test_claude_success_returns_normalized_response():
    """Successful Claude call → LLMResponse with text, stop_reason, model."""

async def test_claude_empty_content_raises():
    """Claude returns content=[] → raises LLMEmptyResponseError."""

async def test_claude_max_tokens_raises_truncated():
    """stop_reason='max_tokens' → raises LLMTruncatedResponseError."""


# --- Fallback ---

async def test_claude_429_retries_then_succeeds():
    """RateLimitError on attempt 1 → retry → succeeds on attempt 2."""

async def test_claude_500_falls_back_to_gemini():
    """Claude APIStatusError 500 → Gemini called → returns Gemini response."""

async def test_claude_401_does_not_fallback():
    """Claude 401 raises FatalAgentError, does NOT trigger Gemini fallback."""

async def test_gemini_response_normalized_same_shape():
    """Gemini response normalized to same LLMResponse as Claude."""


# --- Output Parsing ---

async def test_strip_markdown_fences_from_json():
    """'```json\n{"key": "val"}\n```' parsed to {"key": "val"}."""

async def test_structured_output_repair_on_first_fail():
    """First parse fails → repair prompt sent → second attempt succeeds."""
