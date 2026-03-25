"""Sprint 4 — Security Tests"""
import pytest


# --- Prompt Injection ---

def test_injection_pattern_detected():
    """'ignore previous instructions' triggers PromptInjectionError."""

def test_normal_message_passes():
    """'search for Q4 budget' does not trigger injection detection."""

def test_input_truncated_at_max_length():
    """Message over 8000 chars truncated, not passed to LLM in full."""


# --- SSRF ---

def test_ssrf_blocks_link_local():
    """http://169.254.169.254/... raises SSRFBlockedError."""

def test_ssrf_blocks_private_10():
    """http://10.0.0.1/... raises SSRFBlockedError."""

def test_ssrf_blocks_loopback():
    """http://127.0.0.1/... raises SSRFBlockedError."""

def test_ssrf_allows_public_url():
    """https://api.example.com passes validation."""


# --- Prompt Leak ---

def test_system_prompt_leak_detected():
    """Response containing 'you are MINDY' flagged as leak."""

def test_normal_response_not_flagged():
    """Normal response without system prompt markers passes."""


# --- Card Action Validation ---

def test_card_id_valid_uuid_passes():
    """UUID-format memory_id passes validation."""

def test_card_id_with_injection_rejected():
    """memory_id containing newlines/special chars raises ValueError."""
