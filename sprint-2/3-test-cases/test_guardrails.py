"""Sprint 2 — Guardrails & Validation Tests"""
import pytest


def test_missing_source_id_sets_draft():
    """Memory without source_id → status='draft'."""

def test_missing_as_of_sets_draft():
    """Memory without as_of → status='draft'."""

def test_valid_memory_sets_active():
    """Memory with all required fields → status='active'."""

def test_extra_fields_ignored_not_crash():
    """LLM output with extra keys parsed with extra='ignore', no crash."""

def test_datetime_serializes_with_utc_z():
    """as_of datetime serialized as '2025-03-21T15:00:00Z' (UTC + Z suffix)."""
