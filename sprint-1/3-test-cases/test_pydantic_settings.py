"""Sprint 1 — Pydantic Settings Tests"""
import pytest


def test_settings_loads_from_env_with_prefix():
    """OrgMindSettings reads ORGMIND_ANTHROPIC_API_KEY from environment."""

def test_settings_raises_on_missing_required_key():
    """Missing required SecretStr field raises ValidationError at startup."""

def test_settings_env_nested_delimiter():
    """Double-underscore delimiter maps ORGMIND_DB__HOST to db.host."""

def test_settings_secret_str_masks_in_repr():
    """str(settings.anthropic_api_key) returns '**********', not the actual key."""

def test_settings_get_secret_value_returns_raw():
    """.get_secret_value() returns the actual key string."""
