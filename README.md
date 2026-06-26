---
title: Syntra AI
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
short_description: An AI orchestration pipeline that transforms raw human intent into precision-engineered prompts.
---

<div align="center">

# 🚀 Syntra AI 

> **An advanced AI orchestration pipeline that transforms raw human intent into token-dense, precision-engineered prompts in milliseconds.**

</div>

**Syntra AI** is a high-performance Developer Intelligence Platform built with a **FastAPI** backend and an interactive **Next.js** frontend. It acts as a middleware engine between humans and LLMs.

It accelerates software development by:
- **Prompt Refinement:** Programmatically analyzing and transforming raw thoughts into premium, structured prompts.
- **Intent Intelligence:** Extracting precise developer intent, target domain, urgency, and complexity to guide orchestration.
- **Intelligence Distillation Engine:** Aggressively optimizing semantic noise and thought structures from heavy payloads into high-density representations while mathematically preserving meaning, audience identity, and constraints.
- **Intelligent Router:** Evaluating inputs and dynamically dispatching tasks to specialized, fine-tuned agent workflows.

The system is completely **free forever** with no monetization or billing limits, designed for high performance and clean modularity.

## Project Structure
Syntra AI is structured as a monorepo containing two main directories:

- `/syntra_backend`: The AI routing logic, database models, and FastAPI application.
- `/syntra_frontend`: The interactive Next.js application containing the Workspace IDE.

## Documentation
We maintain modular documentation tailored to specific areas of the stack. Please refer to the following files for in-depth technical details:

1. **[DATABASE.md](./DATABASE.md)**
   Details our Supabase integration, manual SQL schema creation philosophy, 6 active tables, and relations.
2. **[FRONTEND.md](./FRONTEND.md)**
   Explains the "Cyber Graphite" design system, the App Router architecture, and the layout of the Split-Pane Workspace IDE.
3. **[BACKEND.md](./BACKEND.md)**
   Outlines our FastAPI router design, background task telemetry logging, Groq AI integrations, and strict Pydantic validation rules.
4. **[INTELLIGENCE_ENGINE.md](./INTELLIGENCE_ENGINE.md)**
   Provides a deep dive into the 11-step pipeline, the Zero LLM estimation deterministic scoring, and the 6-factor mathematical meaning calculations.

## Local Development
To run Syntra AI locally:

### Backend
1. Navigate to `/syntra_backend`.
2. Ensure dependencies are installed (`pip install -r requirements.txt`).
3. Run the development server: `uvicorn app.main:app --reload`
4. Access the API documentation at `http://127.0.0.1:8000/docs`

### Frontend
1. Navigate to `/syntra_frontend`.
2. Ensure dependencies are installed (`npm install`).
3. Run the development server: `npm run dev`
4. Access the application at `http://localhost:3000`
