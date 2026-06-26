# Syntra AI — Backend Architecture

## Overview

Syntra's backend is built on a **Backend-First, API-Driven** architecture. All platform intelligence — prompt refinement, intent intelligence, dynamic routing, compression, and output parsing — is encapsulated within a clean, versioned REST API. No business logic resides in the transport layer.

---

## Technology Stack

| Component | Technology | Rationale |
|---|---|---|
| **Framework** | FastAPI (Python 3.11+) | Native `async/await` support, automatic OpenAPI schema generation, and tight Pydantic integration. |
| **Input Validation** | Pydantic v2 | Strict type coercion, schema enforcement, and early request rejection at the transport boundary. |
| **Concurrency Model** | `asyncio` | Non-blocking I/O for all LLM and database calls — critical for multi-step pipeline performance. |
| **LLM Integration** | Google Gemini & Groq SDKs | Primary AI providers; abstracted via the Strategy Pattern to allow vendor-agnostic hot-swapping. |
| **Persistence** | Supabase (PostgreSQL) | ✅ Live. Async request logging, session management, feature history, and usage/token telemetry. |
| **Vector Storage** | pgvector / Pinecone | *(Planned)* RAG-based context retrieval for user-specific prompt injection. |

---

## Directory Structure

```text
syntra_backend/
├── app/
│   ├── api/
│   │   └── routers/            # Transport layer — FastAPI endpoints only
│   │       ├── auth_router.py       # User sign up and login
│   │       ├── enhance_router.py    # Prompt Refinement endpoint
│   │       ├── intent_router.py     # Intent Intelligence endpoint
│   │       ├── compress_router.py   # Context Compressor endpoint
│   │       ├── routing_router.py    # Intelligent Router endpoint
│   │       ├── history_router.py    # Categorized history lookup
│   │       └── workspace_router.py  # Workspaces and sessions management
│   ├── core/
│   │   └── config.py           # Environment variable management (Pydantic Settings)
│   ├── db/
│   │   ├── models.py           # SQLAlchemy declarative ORM models
│   │   └── session.py          # Database engines and sessionmakers (AsyncSession)
│   ├── integrations/
│   │   └── llm_clients.py      # Vendor-abstracted LLM provider implementations
│   ├── models/
│   │   └── schemas.py          # All Pydantic request/response contracts
│   ├── prompts/
│   │   ├── enhance_prompts.py  # System prompts for Prompt Refinement
│   │   └── routing_prompts.py  # Domain-specific prompt registry for Intelligent Router
│   ├── services/
│   │   ├── enhancer.py                  # Prompt Refinement business logic
│   │   ├── intent_detection_service.py  # Intent Intelligence business logic
│   │   ├── compressor.py                # Context Compressor business logic
│   │   └── routing_service.py           # Intelligent Router business logic
│   └── main.py                 # FastAPI application factory, session setup, and startup tasks
├── docs/                       # Enterprise Knowledge Base
│   ├── specs/                  # Technical specifications (per-feature)
│   │   ├── compressor-engine.md
│   │   ├── intent-engine.md
│   │   ├── routing-system.md
│   │   └── testing-guide.md    # Test strategy, mocking conventions, coverage map
│   ├── uttam_explanations/     # Plain-language learning documents
│   └── *.md                    # Core architecture and vision documents
├── tests/                      # Automated test suite
│   ├── __init__.py             # Package marker
│   ├── conftest.py             # Shared fixtures (TestClient)
│   ├── test_schemas.py         # Pydantic validation tests
│   ├── test_enhance.py         # Prompt Refinement tests
│   ├── test_intent.py          # Intent Intelligence tests
│   └── test_routing.py         # Intelligent Router tests
├── pytest.ini                  # Pytest configuration
├── .env                        # Environment variables (not committed)
└── requirements.txt            # Production dependencies
```

---

## Core Design Patterns

### 1. Controller–Service–Repository (CSR) Pattern

All platform logic is strictly separated into three independent layers:

| Layer | Location | Responsibility |
|---|---|---|
| **Controller** | `app/api/routers/` | HTTP status codes, request parsing, response serialization. Zero business logic. |
| **Service** | `app/services/` | Core business logic — orchestrating LLM calls, parsing outputs, and database interaction. |
| **Repository** | `app/integrations/` | All external I/O — LLM SDKs, database connections. Completely isolated. |

### 2. Strategy Pattern — Vendor Agnosticism

The service layer has **no direct dependency** on any LLM vendor SDK. All providers implement the `BaseLLMProvider` abstract interface.

```python
# app/integrations/llm_clients.py
from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str) -> str:
        """All providers must implement this single contract."""
        ...
```

### 3. Session Safety Pattern

To prevent connection closures in background tasks, asynchronous writes to `FeatureHistory` and `UsageMetric` are isolated within local `async with AsyncSessionLocal() as session:` blocks, ensuring database sessions remain safe and active during non-blocking tasks.

---

## API Versioning & Endpoints

All endpoints are versioned to support non-breaking future API evolution.

| Route | Method | Status | Service |
|---|---|---|---|
| `/v1/enhance` | `POST` | ✅ Live | Prompt Refinement |
| `/v1/intent` | `POST` | ✅ Live | Intent Intelligence |
| `/v1/compress` | `POST` | ✅ Live | Context Compressor |
| `/v1/chat` | `POST` | ✅ Live | Intelligent Router |
| `/v1/history` | `GET` | ✅ Live | Session History Retrieval |
| `/v1/workspace` | `GET`/`POST`| ✅ Live | Workspaces and Sessions |
