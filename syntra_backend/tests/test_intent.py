# tests/test_intent.py
# Integration tests for the Intent Classification Engine (POST /v1/intent)
# Validates classification, validation, and error handling using mocks.

import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException


# ─────────────────────────────────────────
# Happy Path Tests
# ─────────────────────────────────────────

def test_intent_returns_200_with_valid_prompt(client):
    """
    Full happy-path test.
    The LLM is mocked to return a valid intent classification JSON.
    We verify all 5 intent fields are present and correct.
    """
    fake_intent_response = '''{
        "primary_intent": "DEBUGGING",
        "urgency": "high",
        "complexity": "simple",
        "target_domain": "backend",
        "reasoning": "The user is describing a bug in their code."
    }'''

    with patch(
        "app.services.intent_detection_service.llm_provider.generate",
        new=AsyncMock(return_value=fake_intent_response)
    ):
        response = client.post("/v1/intent", json={"prompt": "My API is returning 500 errors"})

    assert response.status_code == 200

    data = response.json()

    # Verify all required fields are present
    assert "original_prompt" in data
    assert "primary_intent" in data
    assert "urgency" in data
    assert "complexity" in data
    assert "target_domain" in data
    assert "reasoning" in data

    # Verify specific values from our mock
    assert data["primary_intent"] == "DEBUGGING"
    assert data["urgency"] == "high"
    assert data["original_prompt"] == "My API is returning 500 errors"


def test_intent_classifies_optimization(client):
    """
    Verifies the intent engine correctly returns OPTIMIZATION intent.
    Tests that the primary_intent field reflects the mock's classification.
    """
    fake_intent_response = '''{
        "primary_intent": "OPTIMIZATION",
        "urgency": "low",
        "complexity": "complex",
        "target_domain": "performance",
        "reasoning": "The user wants to improve code performance."
    }'''

    with patch(
        "app.services.intent_detection_service.llm_provider.generate",
        new=AsyncMock(return_value=fake_intent_response)
    ):
        response = client.post(
            "/v1/intent",
            json={"prompt": "My database queries are taking 10 seconds each"}
        )

    assert response.status_code == 200
    assert response.json()["primary_intent"] == "OPTIMIZATION"


# ─────────────────────────────────────────
# Validation / Rejection Tests
# ─────────────────────────────────────────

def test_intent_rejects_empty_prompt(client):
    """Pydantic rejects empty prompt before service is called."""
    response = client.post("/v1/intent", json={"prompt": ""})
    assert response.status_code == 422


def test_intent_rejects_one_char_prompt(client):
    """Prompt of 1 character is below min_length=2."""
    response = client.post("/v1/intent", json={"prompt": "x"})
    assert response.status_code == 422


def test_intent_rejects_missing_body(client):
    """Empty body — prompt field is missing entirely."""
    response = client.post("/v1/intent", json={})
    assert response.status_code == 422


# ─────────────────────────────────────────
# Error Handling Tests
# ─────────────────────────────────────────

def test_intent_handles_malformed_llm_output(client):
    """
    The LLM returns a non-JSON string (hallucination).
    The service must return HTTP 500 instead of crashing.
    """
    with patch(
        "app.services.intent_detection_service.llm_provider.generate",
        new=AsyncMock(return_value="I cannot classify this request.")
    ):
        response = client.post(
            "/v1/intent",
            json={"prompt": "help me with my code"}
        )

    assert response.status_code == 500


def test_intent_handles_llm_failure(client):
    """
    The LLM raises an HTTPException 502 (Gemini API down).
    The service must propagate the 502 correctly.
    """
    with patch(
        "app.services.intent_detection_service.llm_provider.generate",
        new=AsyncMock(side_effect=HTTPException(
            status_code=502,
            detail="Failed to reach the Intent Engine model."
        ))
    ):
        response = client.post(
            "/v1/intent",
            json={"prompt": "explain recursion to me"}
        )

    assert response.status_code == 502
