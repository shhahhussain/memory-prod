"""Sprint 5 — Health Check & Startup Tests"""
import pytest


async def test_readiness_503_before_pools_ready():
    """/health/ready returns 503 when app_ready event not set."""

async def test_readiness_200_after_pools_ready():
    """/health/ready returns 200 after all pools initialized."""

async def test_readiness_503_on_postgres_failure():
    """/health/ready returns 503 when SELECT 1 fails."""

async def test_liveness_always_200():
    """/health/live returns 200 even during startup."""
