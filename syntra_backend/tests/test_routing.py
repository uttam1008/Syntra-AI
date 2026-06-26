# tests/test_routing.py
# Integration tests for the Routing & Execution System (POST /v1/chat)
# This is the most complex test — it mocks TWO separate LLM calls simultaneously.

import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException


# ── Shared fake responses ──────────────────────────────────────────────────────
# Defined at module level so all tests can reuse them without repetition

FAKE_INTENT_JSON = '''{
    "primary_intent": "DEBUGGING",
    "urgency": "high",
    "complexity": "simple",
    "target_domain": "backend",
    "reasoning": "The user is reporting a function that returns None."
}'''

FAKE_EXECUTION_RESULT = "## Root Cause Analysis\n\nThe function returns None because there is no return statement."


# ─────────────────────────────────────────
# Happy Path Tests
# ─────────────────────────────────────────

def test_routing_returns_200_with_valid_prompt(client):
    mock_generate = AsyncMock(side_effect=[FAKE_INTENT_JSON, FAKE_EXECUTION_RESULT])

    with patch(
        "app.services.intent_detection_service.llm_provider.generate",
        new=mock_generate
    ):
        response = client.post(
            "/v1/chat",
            json={"prompt": "My function returns None but I expected a list"}
        )

    assert response.status_code == 200
    data = response.json()
    assert "intent_metadata" in data
    assert "execution_result" in data
    assert data["intent_metadata"]["primary_intent"] == "DEBUGGING"
    assert data["intent_metadata"]["urgency"] == "high"
    assert data["intent_metadata"]["original_prompt"] == "My function returns None but I expected a list"
    assert "Root Cause Analysis" in data["execution_result"]


def test_routing_with_code_context_and_language(client):
    mock_generate = AsyncMock(side_effect=[FAKE_INTENT_JSON, FAKE_EXECUTION_RESULT])

    with patch(
        "app.services.intent_detection_service.llm_provider.generate",
        new=mock_generate
    ):
        response = client.post(
            "/v1/chat",
            json={
                "prompt": "Why is this slow?",
                "code_context": "for i in range(1000000): db.query(i)",
                "language": "python"
            }
        )

    assert response.status_code == 200
    assert "intent_metadata" in response.json()
    assert "execution_result" in response.json()


def test_routing_with_prompt_only(client):
    mock_generate = AsyncMock(side_effect=[FAKE_INTENT_JSON, FAKE_EXECUTION_RESULT])

    with patch(
        "app.services.intent_detection_service.llm_provider.generate",
        new=mock_generate
    ):
        response = client.post(
            "/v1/chat",
            json={"prompt": "Explain what a closure is"}
        )

    assert response.status_code == 200



# ─────────────────────────────────────────
# Validation / Rejection Tests
# ─────────────────────────────────────────

def test_routing_rejects_empty_prompt(client):
    """Pydantic rejects empty prompt before any service is called."""
    response = client.post("/v1/chat", json={"prompt": ""})
    assert response.status_code == 422


def test_routing_rejects_missing_body(client):
    """Missing prompt field entirely — must be rejected."""
    response = client.post("/v1/chat", json={})
    assert response.status_code == 422


# ─────────────────────────────────────────
# Error Handling Tests
# ─────────────────────────────────────────

def test_routing_handles_intent_engine_failure(client):
    """
    If the FIRST LLM call (intent detection) fails,
    the entire pipeline must fail with 502 — not crash silently.
    """
    with patch(
        "app.services.intent_detection_service.llm_provider.generate",
        new=AsyncMock(side_effect=HTTPException(
            status_code=502,
            detail="Failed to reach the Intent Engine model."
        ))
    ):
        response = client.post(
            "/v1/chat",
            json={"prompt": "fix my code"}
        )

    assert response.status_code == 502


def test_routing_handles_execution_engine_failure(client):
    """
    Intent detection succeeds but the SECOND LLM call (execution) fails.
    The pipeline must return 502 — not 200 with empty result.
    """
    with patch(
        "app.services.intent_detection_service.llm_provider.generate",
        new=AsyncMock(return_value=FAKE_INTENT_JSON)
    ), patch(
        "app.services.routing_service.llm_provider.generate",
        new=AsyncMock(side_effect=HTTPException(
            status_code=502,
            detail="Execution Engine failed to generate a response."
        ))
    ):
        response = client.post(
            "/v1/chat",
            json={"prompt": "optimize my database queries"}
        )

    assert response.status_code == 502
