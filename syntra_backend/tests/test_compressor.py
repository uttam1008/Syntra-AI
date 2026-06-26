import pytest
from unittest.mock import patch, AsyncMock

# Fake LLM response for our tests (Sharma Ji's dummy ingredients!)
FAKE_COMPRESSED_TEXT = "This is the clean, compressed version of the text."

def test_compressor_returns_200_with_valid_payload(client):
    """
    Happy path test. Verifies that the endpoint successfully returns 
    the mathematically calculated compression ratio and text.
    """
    with patch(
        "app.services.compressor.llm_provider.generate",
        new=AsyncMock(return_value=FAKE_COMPRESSED_TEXT)
    ):
        long_text = "This is a very long text " * 10
        response = client.post(
            "/v1/compress",
            json={"input_text": long_text, "preserve_code": True}
        )

    assert response.status_code == 200
    data = response.json()
    
    # Verify the structure matches our schema
    assert "original_length" in data
    assert "compressed_length" in data
    assert "compression_ratio" in data
    assert "compressed_text" in data
    
    # Verify the ratio math is correct
    assert data["original_length"] == len(long_text)
    assert data["compressed_length"] == len(FAKE_COMPRESSED_TEXT)
    expected_ratio = round(len(FAKE_COMPRESSED_TEXT) / len(long_text), 2)
    assert data["compression_ratio"] == expected_ratio

def test_compressor_rejects_short_payloads(client):
    """
    Verifies that Pydantic rejects payloads under 10 characters (Darwaan is working).
    """
    response = client.post(
        "/v1/compress",
        json={"input_text": "Too short"}
    )
    assert response.status_code == 422

def test_compressor_handles_llm_failure(client):
    """
    Verifies that if the LLM crashes, the API returns a graceful 502 error (Fire Alarm).
    """
    with patch(
        "app.services.compressor.llm_provider.generate",
        new=AsyncMock(side_effect=Exception("API Timeout"))
    ):
        response = client.post(
            "/v1/compress",
            json={"input_text": "This is a valid long text string to trigger the mock."}
        )
        
    assert response.status_code == 502
    assert "API Timeout" in response.json()["detail"]
