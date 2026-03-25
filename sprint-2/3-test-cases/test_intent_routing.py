"""Sprint 2 — Intent Routing (3-Tier) Tests"""
import pytest


# --- Tier 1: Keyword Regex ---

def test_keyword_route_search_prefix():
    """'search for Q4 budget' matches SEARCH_MEMORY intent."""

def test_keyword_route_find_prefix():
    """'find me the latest report' matches SEARCH_MEMORY intent."""

def test_keyword_route_task_prefix():
    """'create a task for follow-up' matches CREATE_TASK intent."""

def test_keyword_route_campaign_prefix():
    """'draft a campaign for launch' matches DRAFT_CAMPAIGN intent."""

def test_keyword_route_ambiguous_returns_none():
    """'search for tasks about campaign' matches multiple — returns None."""

def test_keyword_route_no_match_returns_none():
    """'hello how are you' matches nothing — returns None."""


# --- Tier 2: LLM Classifier ---

async def test_llm_classifier_returns_valid_intent():
    """LLM returns valid IntentEnum with confidence above threshold."""

async def test_llm_classifier_normalizes_aliases():
    """'search_memories' normalized to 'search_memory' via alias map."""

async def test_llm_classifier_handles_unknown_label():
    """Unknown label 'research_stuff' falls back to alias or raises."""

async def test_llm_classifier_low_confidence_triggers_clarification():
    """Confidence 0.3 (below 0.6 threshold) returns clarification_needed."""


# --- Tier 3: Context-Dependent ---

async def test_yes_routes_to_confirm_when_pending():
    """'yes' with pending_confirmation='save_draft' returns CONFIRM intent."""

async def test_no_routes_to_cancel_when_pending():
    """'no' with pending_confirmation='save_draft' returns CANCEL intent."""

async def test_yes_without_pending_falls_through():
    """'yes' with no pending_confirmation goes to LLM classifier."""


# --- Multi-Intent ---

async def test_multi_intent_detection():
    """'search X and create task Y' returns 2 RoutedIntent objects."""

async def test_single_intent_returns_one():
    """'search for Q4 budget' returns exactly 1 RoutedIntent."""
