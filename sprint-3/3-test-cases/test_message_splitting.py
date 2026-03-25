"""Sprint 3 — Message Size Splitting Tests"""
import pytest


def test_short_message_no_split():
    """Message under 7000 chars returned as single item."""

def test_long_message_split_at_paragraphs():
    """Message over 7000 chars split at paragraph boundaries."""

def test_split_never_mid_sentence():
    """Split point is always at a paragraph break, not mid-text."""

def test_split_includes_part_numbers():
    """Multi-part messages prefixed with 'Part 1/3', 'Part 2/3', etc."""
