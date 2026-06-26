# Syntra AI — Engineering Philosophy

> **योगः कर्मसु कौशलम्**
> *"Excellence in Action"* — Bhagavad Gita, II.50

---

## Overview

Syntra AI is not built for speed of delivery. It is built for **depth of mastery**. Every architectural decision, every abstraction layer, and every documented trade-off is a deliberate investment in engineering rigor over expedience.

This document defines the foundational principles that govern all technical and process decisions on this platform.

---

## Core Principles

### 1. Docs-First Engineering

> *Code is transient. Architecture is permanent.*

No feature is implemented without a prior, complete architectural specification. Documentation is the **single source of truth** for the system's design intent. If a decision is not documented, it does not officially exist, and code implementing it may not be merged.

This principle ensures:
- Zero knowledge loss across sessions and team members
- A reviewable audit trail of all architectural decisions
- Clear alignment between intent, specification, and implementation

---

### 2. Abstraction & Vendor Decoupling

> *Protect the core from the vendors.*

No core business logic may have a direct dependency on a third-party SDK. All external integrations — LLM providers, databases, vector stores — must be abstracted behind clean, internal interfaces (implemented via the **Strategy Pattern** using Abstract Base Classes).

This principle ensures:
- **Zero vendor lock-in.** Any provider can be hot-swapped without modifying business logic.
- **Testability.** Core services can be unit-tested against mock implementations.
- **Resilience.** Provider outages are isolated at the integration boundary, not propagated into the core.

---

### 3. Prompts as Software Artifacts

> *Never trust the LLM. Enforce the output.*

In Syntra, system prompts are first-class software artifacts. They are:
- **Versioned** — tracked in source control alongside application code
- **Modular** — separated by concern into domain-specific prompt registries
- **Deterministic** — enforced via strict JSON output schemas and programmatic sanitization layers
- **Validated** — outputs are parsed and validated by Pydantic before being passed to any downstream consumer

Relying solely on prompt engineering is insufficient for production systems. Programmatic output enforcement is mandatory.

---

### 4. Mastery Over Velocity

> *Understanding why is more valuable than knowing how.*

When a trade-off arises between the fastest path to a working feature and the path that teaches correct system design, this project will always choose the latter.

Every line of code in Syntra is an opportunity to practice the principles that distinguish senior engineers from junior ones: abstraction, separation of concerns, resilience, observability, and scalability.

---

## Non-Negotiable Engineering Standards

| Standard | Requirement |
|---|---|
| **Input Validation** | All API inputs must be validated via Pydantic schemas before reaching the service layer |
| **Error Handling** | All external API calls must be wrapped in `try/except` blocks with structured HTTP exceptions |
| **LLM Abstraction** | No service layer file may import a vendor SDK directly |
| **Output Parsing** | All LLM responses must pass through a sanitization and validation layer before use |
| **Documentation** | All new features require a specification document before implementation begins |
