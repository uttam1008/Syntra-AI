# Syntra AI — Architecture Decision Records (ADR)

> [!NOTE]
> This document is the canonical log of all significant architectural and engineering decisions made during the development of Syntra AI. Each record captures the date, context, decision, rationale, and measurable impact to serve as a reference for current and future engineers.

---

## ADR-001: Backend Framework Selection

| Field | Detail |
|---|---|
| **Date** | 2026-05-21 |
| **Status** | ✅ Accepted |
| **Decision** | FastAPI (Python 3.11+) over Flask or Django |

### Context
Syntra's core pipeline involves multiple sequential, I/O-bound LLM API calls. A synchronous framework would introduce significant blocking latency, particularly during multi-step intent classification and routing operations.

### Decision
Adopt **FastAPI** as the sole web framework.

### Rationale
- Native `async/await` support eliminates blocking I/O across the entire pipeline
- Automatic OpenAPI documentation generation from Pydantic schemas
- First-class Pydantic integration enforces strict input/output contracts at zero additional overhead
- Significantly lower boilerplate than Django for a pure-API service

### Impact
- All route handlers and service functions must be implemented as `async def`
- All data contracts must be expressed as Pydantic models — no raw dict handling permitted in the service layer

---

## ADR-002: Strategy Pattern for LLM Provider Abstraction

| Field | Detail |
|---|---|
| **Date** | 2026-05-21 |
| **Status** | ✅ Accepted |
| **Decision** | Abstract all LLM providers behind a `BaseLLMProvider` interface using Python's Abstract Base Class (`ABC`) |

### Context
The AI vendor ecosystem is highly volatile. Model pricing changes, capability gaps emerge, and service outages occur. Hard-coding Gemini SDK calls directly into service layer functions would make any provider migration a high-risk, project-wide refactor.

### Decision
Implement the **Strategy Pattern** — define a `BaseLLMProvider(ABC)` with an `@abstractmethod generate()` contract. All providers inherit from this interface.

### Rationale
- Isolates vendor-specific code to a single integration file
- Service layer logic depends only on the abstract interface, not the concrete implementation
- Enables unit testing with mock providers without requiring live API credentials
- Satisfies the Open/Closed Principle — new providers can be added without modifying existing code

### Impact
- No `import google.generativeai` or equivalent may appear in any file outside `app/integrations/`
- Switching LLM providers requires only one initialization change in `app/core/config.py`

---

## ADR-003: Docs-First Engineering Workflow

| Field | Detail |
|---|---|
| **Date** | 2026-05-22 |
| **Status** | ✅ Accepted |
| **Decision** | Mandatory documentation gate before any feature implementation |

### Context
Without a formal documentation requirement, architectural intent is fragmented across code comments, informal conversations, and undocumented assumptions. This creates knowledge loss, misaligned implementations, and a system that cannot be safely extended.

### Decision
Enforce a **Docs-First Engineering Workflow**:

```
Specification Written → Review & Approval → Implementation → Verification → ADR Updated
```

All new features require a specification document in `docs/specs/` before a single line of implementation code is written.

### Rationale
- Creates a single source of truth that outlives any single development session
- Forces architectural thinking before tactical coding
- Produces an enterprise-grade knowledge base that enables safe onboarding of future contributors

### Impact
- Development velocity is intentionally reduced in favor of architectural clarity
- All implementation plans are stored in `docs/Implementation plans/`
- This ADR log must be updated with every significant architectural decision

---

## ADR-004: Lightweight Model for Classification, High-Capability Model for Execution

| Field | Detail |
|---|---|
| **Date** | 2026-05-22 |
| **Status** | ✅ Accepted |
| **Decision** | Use Gemini Flash for intent classification; reserve Gemini Pro for execution-stage generation |

### Context
Running all pipeline stages through a single high-capability model (e.g., Gemini Pro) is cost-inefficient. Intent classification is a lightweight, structured-output task that does not require the full reasoning capacity of a frontier model.

### Decision
Adopt a **tiered model strategy**: lightweight model for classification, high-capability model for generation.

### Rationale
- Gemini Flash provides sub-second classification with > 95% accuracy on structured intent tasks
- Cost reduction of approximately 70% on classification-stage token usage
- Gemini Pro's full capability is preserved for the tasks that genuinely require it (code generation, debugging analysis)

### Impact
- Intent Engine and Routing Orchestrator use `GeminiFlashProvider`
- Execution-stage agents use `GeminiProProvider`
- Both are injected via the `BaseLLMProvider` interface — the service layer is unaware of the distinction

---

## ADR-005: Registry Pattern for the Routing & Execution System

| Field | Detail |
|---|---|
| **Date** | 2026-05-24 |
| **Status** | ✅ Accepted |
| **Decision** | Use a plain Python dictionary as a centralized Prompt Registry instead of conditional branching in the routing service |

### Context
The Routing System must map each classified intent to a specialized system prompt and dispatch the request to the correct execution agent. The naive approach — a long `if-elif` chain in the routing service — is tightly coupled, hard to extend, and violates the Open/Closed Principle. Every new intent would require modifying the core routing logic.

### Decision
Implement the **Registry Pattern** using a centralized `PROMPT_REGISTRY` dictionary in a dedicated `app/prompts/routing_prompts.py` module. The routing service performs a single O(1) dictionary lookup to resolve the correct system prompt.

```python
# The entire routing decision — one line
system_prompt = PROMPT_REGISTRY.get(detected_intent, PROMPT_REGISTRY["GENERAL_CHAT"])
```

### Rationale
- O(1) lookup performance regardless of how many intents exist
- Adding a new intent requires only one new entry in `PROMPT_REGISTRY` — the router, orchestrator, and all other components require zero modification
- Satisfies the Open/Closed Principle — the system is open for extension but closed for modification
- Complete separation of prompt data from orchestration logic

### Impact
- `app/prompts/routing_prompts.py` is the single source of truth for all agent personalities
- `GENERAL_CHAT` serves as the mandatory fallback for any unrecognized intent — the system never crashes on an unknown classification
- Future intents (e.g., `TEST_GENERATION`, `SECURITY_AUDIT`) can be added by any contributor without touching service layer code

---

## ADR-006: Automated Test Suite with Mocked LLM Providers

| Field | Detail |
|---|---|
| **Date** | 2026-05-24 |
| **Status** | ✅ Accepted |
| **Decision** | Use `pytest` with `AsyncMock` to test all service and API layers without calling real LLM APIs |

### Context
As the Syntra pipeline grew across three phases (Enhancer, Intent Engine, Routing System), the codebase required a formal quality gate. Manual testing via Swagger UI is non-repeatable, non-systematic, and does not catch regressions introduced by future changes. A real bug was discovered during test development: the `system_prompt.py` file used Python's `.format()` with JSON examples containing literal curly braces, causing `KeyError` in production-equivalent conditions.

### Decision
Implement a **full automated test suite** using `pytest`, `pytest-asyncio`, and `httpx`. All external LLM API calls are replaced with `AsyncMock` via `unittest.mock.patch`. Tests are organized into four files covering schemas, the Enhancer Engine, the Intent Engine, and the Routing System.

### Rationale
- Tests run in under 1 second with zero API cost and zero network dependency
- `AsyncMock` provides deterministic, controlled LLM responses per test scenario
- `conftest.py` centralizes the `TestClient` fixture, eliminating setup boilerplate from every test file
- The test suite discovered a real production defect (curly brace escaping bug) on its first run

### Impact
- 28 tests across 4 files — 100% pass rate required before any merge
- `side_effect` list pattern is the established convention for mocking the shared `llm_provider` singleton in multi-call flows
- All new services must include corresponding test files before implementation is considered complete
- See `docs/specs/testing-guide.md` for full conventions and patterns
