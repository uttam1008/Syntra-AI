# Syntra AI — Testing Guide

| Field | Detail |
|---|---|
| **Document Type** | Engineering Reference |
| **Status** | ✅ Active |
| **Version** | 1.0.0 |
| **Coverage** | Schemas · Enhancer · Intent Engine · Routing System |
| **Last Updated** | 2026-05-24 |

---

## Overview

This document defines the automated testing strategy, toolchain, and conventions for the Syntra AI backend. The test suite ensures correctness across all three pipeline phases and protects against regressions as the platform scales.

> [!IMPORTANT]
> All tests must pass before any feature branch is merged. The test suite is the primary quality gate.

---

## Toolchain

| Tool | Version | Purpose |
|---|---|---|
| `pytest` | 9.x | Test runner and test discovery |
| `pytest-asyncio` | 1.x | Async function support in tests |
| `httpx` | latest | Async HTTP client (required by FastAPI TestClient) |
| `unittest.mock` | stdlib | `AsyncMock` and `patch` for LLM mocking |

### Installation

```bash
pip install pytest pytest-asyncio httpx
```

---

## Configuration

### `pytest.ini` (project root)

```ini
[pytest]
testpaths = tests
asyncio_mode = auto
```

- `testpaths = tests` — restricts test discovery to the `tests/` directory
- `asyncio_mode = auto` — all async test functions run without explicit decorators

---

## Test Architecture

### Directory Structure

```text
tests/
├── __init__.py          # Package marker — required for pytest discovery
├── conftest.py          # Shared fixtures (TestClient setup)
├── test_schemas.py      # Pydantic schema validation tests
├── test_enhance.py      # Enhancer Engine endpoint tests
├── test_intent.py       # Intent Engine endpoint tests
└── test_routing.py      # Routing & Execution System endpoint tests
```

### Test Types

| Type | Description | Tools Used |
|---|---|---|
| **Unit** | Tests a single function/class in isolation | `pytest`, Pydantic direct instantiation |
| **Integration** | Tests the full HTTP request/response cycle | `TestClient`, `AsyncMock`, `patch` |

---

## Core Testing Concepts

### The Mocking Principle

> [!NOTE]
> Tests must **never** call the real Gemini API. Doing so introduces cost, non-determinism, and network dependency into the test suite.

All LLM calls are replaced with `AsyncMock` — a synchronous-compatible fake that returns controlled, predictable strings instantly.

```python
from unittest.mock import patch, AsyncMock

with patch(
    "app.services.enhancer.llm_provider.generate",
    new=AsyncMock(return_value='{"enhanced_prompt": "...", "reasoning": "..."}')
):
    response = client.post("/v1/enhance", json={"prompt": "fix my bug"})
```

### The Patching Rule

**Always patch WHERE the function is used, not where it is defined.**

```python
# ✅ Correct — patches the reference in the service that uses it
patch("app.services.enhancer.llm_provider.generate", ...)

# ❌ Wrong — patches the source, which the service has already imported
patch("app.integrations.llm_clients.llm_provider.generate", ...)
```

### The Singleton Problem

`llm_provider` is a module-level singleton shared across all services. When two services both call `llm_provider.generate()` in sequence (as in the Routing System), patching the same object from two different paths results in the second patch overwriting the first.

**Solution:** Use `side_effect` with a list to return different values on successive calls.

```python
# Returns FAKE_INTENT_JSON on first call, FAKE_EXECUTION_RESULT on second
mock_generate = AsyncMock(side_effect=[FAKE_INTENT_JSON, FAKE_EXECUTION_RESULT])

with patch(
    "app.services.intent_detection_service.llm_provider.generate",
    new=mock_generate
):
    response = client.post("/v1/chat", json={"prompt": "..."})
```

---

## Shared Fixtures — `conftest.py`

```python
@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
```

The `client` fixture is available to every test function automatically — no import required. Any test function that declares `client` as a parameter receives the TestClient instance.

---

## Test Coverage Summary

| File | Tests | Covers |
|---|---|---|
| `test_schemas.py` | 8 | Pydantic validation — valid data, invalid data, optional fields, nested models |
| `test_enhance.py` | 6 | HTTP 200 happy path, 422 rejections, 500 malformed JSON, 502 LLM failure |
| `test_intent.py` | 7 | HTTP 200 with classification, 422 rejections, 500 hallucination, 502 failure |
| `test_routing.py` | 7 | HTTP 200 full pipeline, optional fields, 422 rejections, 502 intent failure, 502 execution failure |
| **Total** | **28** | **All three pipeline phases + schemas** |

---

## Running Tests

### Full Suite

```bash
pytest tests/ -v
```

### Single File

```bash
pytest tests/test_routing.py -v
```

### With Full Error Tracebacks (debugging)

```bash
pytest tests/ -v --tb=long
```

### Expected Output (Passing)

```
tests/test_schemas.py::... PASSED
tests/test_enhance.py::... PASSED
tests/test_intent.py::...  PASSED
tests/test_routing.py::... PASSED

====== 28 passed, 1 warning in 0.26s ======
```

---

## Known Warnings

```
FutureWarning: All support for the `google.generativeai` package has ended.
Please switch to the `google.genai` package as soon as possible.
```

**Status:** Tracked. Migration to `google-genai` is scheduled as a separate infrastructure task. This warning does not affect test correctness.

---

## Test Writing Conventions

1. **Name tests descriptively** — `test_enhance_handles_malformed_llm_output` not `test_3`
2. **One behaviour per test** — each test validates exactly one scenario
3. **Always include a docstring** — explain what the test validates and why
4. **Test both happy path AND failure cases** — every service needs at least one negative test
5. **Never use real API credentials in tests** — mock everything external
