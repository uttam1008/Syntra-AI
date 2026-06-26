# tests/test_enhance.py
# Integration tests for the Enhancer Engine (POST /v1/enhance)
# Uses mocking to replace the real LLM with a controlled fake response.

import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException


# ─────────────────────────────────────────
# Happy Path Tests
# ─────────────────────────────────────────

def test_enhance_returns_200_with_valid_prompt(client):
    """
    Full happy-path test.
    The LLM is mocked to return a valid JSON string.
    We verify the endpoint returns HTTP 200 and the correct response shape.
    """
    # This is the fake JSON the "LLM" will return
    fake_llm_response = '{"enhanced_prompt": "Refactor the login function to use JWT authentication with proper error handling.", "reasoning": "Added specificity and technical context."}'

    with patch(
        "app.services.enhancer.llm_provider.generate",
        new=AsyncMock(return_value=fake_llm_response)
    ):
        response = client.post("/v1/enhance", json={"prompt": "fix my login"})

    # Verify HTTP status
    assert response.status_code == 200

    # Verify response structure
    data = response.json()
    assert "original_prompt" in data
    assert "enhanced_prompt" in data
    assert "reasoning" in data

    # Verify the values are correct
    assert data["original_prompt"] == "fix my login"
    assert "JWT" in data["enhanced_prompt"]  # our fake response contained "JWT"


# ─────────────────────────────────────────
# Validation / Rejection Tests
# ─────────────────────────────────────────

def test_enhance_rejects_empty_prompt(client):
    """
    No mock needed — Pydantic rejects this before the service is ever called.
    FastAPI returns 422 Unprocessable Entity for schema violations.
    """
    response = client.post("/v1/enhance", json={"prompt": ""})
    assert response.status_code == 422


def test_enhance_rejects_missing_prompt_field(client):
    """Sending an empty body — prompt field is missing entirely."""
    response = client.post("/v1/enhance", json={})
    assert response.status_code == 422


def test_enhance_rejects_one_char_prompt(client):
    """Prompt of 1 character is below min_length=2."""
    response = client.post("/v1/enhance", json={"prompt": "x"})
    assert response.status_code == 422


# ─────────────────────────────────────────
# Error Handling Tests
# ─────────────────────────────────────────

def test_enhance_handles_llm_api_failure(client):
    """
    The LLM is mocked to raise an HTTPException (simulating a Gemini API failure).
    We verify the endpoint correctly returns HTTP 502 Bad Gateway.
    """
    with patch(
        "app.services.enhancer.llm_provider.generate",
        new=AsyncMock(side_effect=HTTPException(status_code=502, detail="Upstream AI provider failed."))
    ):
        response = client.post("/v1/enhance", json={"prompt": "fix my broken code"})

    assert response.status_code == 502


def test_enhance_handles_malformed_llm_output(client):
    """
    The LLM is mocked to return a non-JSON string (simulating hallucination).
    We verify the endpoint returns HTTP 500 instead of crashing.
    """
    with patch(
        "app.services.enhancer.llm_provider.generate",
        new=AsyncMock(return_value="This is not JSON at all!")
    ):
        response = client.post("/v1/enhance", json={"prompt": "fix my broken code"})

    assert response.status_code == 500
