# tests/conftest.py
# Shared fixtures available to ALL test files automatically.
# pytest discovers this file and makes its fixtures globally available.

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """
    Creates a synchronous TestClient for the FastAPI app.
    This fixture is available to every test file without any imports.
    
    Usage in any test:
        def test_something(client):
            response = client.post("/v1/intent", json={"prompt": "hello"})
    """
    with TestClient(app) as test_client:
        yield test_client
