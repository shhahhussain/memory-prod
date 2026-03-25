"""Sprint 4 — Retry & Circuit Breaker Tests"""
import pytest


# --- Retry ---

async def test_retry_on_429_succeeds_after_backoff():
    """429 on attempt 1 → backoff → attempt 2 succeeds."""

async def test_retry_exhausted_raises():
    """3 consecutive failures → raises after max_retries."""

async def test_no_retry_on_400():
    """400 Bad Request → immediate raise, no retry."""


# --- Circuit Breaker ---

async def test_circuit_opens_after_threshold_failures():
    """5 consecutive failures → circuit state = OPEN."""

async def test_open_circuit_skips_call():
    """OPEN circuit → raises CircuitBreakerOpen without calling provider."""

async def test_circuit_half_open_after_recovery_timeout():
    """After recovery_timeout → state = HALF_OPEN, allows one probe request."""

async def test_successful_probe_closes_circuit():
    """HALF_OPEN + successful call → state = CLOSED."""

async def test_401_does_not_count_as_circuit_failure():
    """4xx client errors do NOT increment circuit breaker failure count."""
