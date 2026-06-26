# tests/test_schemas.py
# Unit tests for all Pydantic schemas in app/models/schemas.py
# These tests validate that schemas correctly accept valid data
# and reject invalid data — with zero HTTP or LLM involvement.

import pytest
from pydantic import ValidationError
from app.models.schemas import (
    EnhanceRequest,
    EnhanceResponse,
    IntentRequest,
    IntentResponse,
    RoutingRequest,
    RoutingResponse,
)


# ─────────────────────────────────────────
# EnhanceRequest Tests
# ─────────────────────────────────────────

def test_enhance_request_valid():
    """A valid prompt should create the model without errors."""
    req = EnhanceRequest(prompt="Fix my broken login function")
    assert req.prompt == "Fix my broken login function"


def test_enhance_request_too_short():
    """A prompt with 1 character is below min_length=2 — must be rejected."""
    with pytest.raises(ValidationError):
        EnhanceRequest(prompt="x")


def test_enhance_request_empty_string():
    """An empty string prompt must be rejected."""
    with pytest.raises(ValidationError):
        EnhanceRequest(prompt="")


# ─────────────────────────────────────────
# RoutingRequest Tests
# ─────────────────────────────────────────

def test_routing_request_valid_prompt_only():
    """Only prompt is required — optional fields must default to None."""
    req = RoutingRequest(prompt="How do I write a unit test?")
    assert req.prompt == "How do I write a unit test?"
    assert req.code_context is None   # optional field → must default to None
    assert req.language is None       # optional field → must default to None


def test_routing_request_valid_all_fields():
    """All three fields provided — all must be stored correctly."""
    req = RoutingRequest(
        prompt="Why is this function slow?",
        code_context="def slow(): time.sleep(10)",
        language="python"
    )
    assert req.prompt == "Why is this function slow?"
    assert req.code_context == "def slow(): time.sleep(10)"
    assert req.language == "python"


def test_routing_request_empty_prompt():
    """Empty prompt must be rejected — prompt is mandatory."""
    with pytest.raises(ValidationError):
        RoutingRequest(prompt="")


def test_routing_request_missing_prompt():
    """Missing prompt field entirely must be rejected."""
    with pytest.raises(ValidationError):
        RoutingRequest()


# ─────────────────────────────────────────
# RoutingResponse Tests (Nested Schema)
# ─────────────────────────────────────────

def test_routing_response_nested_schema():
    """
    RoutingResponse embeds IntentResponse as a nested object.
    This test validates that Pydantic correctly validates nested models.
    """
    intent = IntentResponse(
        original_prompt="Fix my bug",
        primary_intent="DEBUGGING",
        urgency="high",
        complexity="simple",
        target_domain="backend",
        reasoning="The prompt describes a bug fix task."
    )
    response = RoutingResponse(
        intent_metadata=intent,
        execution_result="Here is the fix: ..."
    )
    assert response.intent_metadata.primary_intent == "DEBUGGING"
    assert response.execution_result == "Here is the fix: ..."
