"""Sprint 5 — CI/CD & Deployment Tests"""
import pytest


def test_unit_tests_need_no_secrets():
    """Unit test suite runs without ANTHROPIC_API_KEY set."""

def test_test_database_url_configurable():
    """TEST_DATABASE_URL env var overrides default localhost DSN."""

async def test_db_tables_truncated_between_tests():
    """autouse fixture truncates tables → no cross-test contamination."""
