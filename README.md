---
title: Syntra AI
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
short_description: An AI orchestration pipeline that transforms raw human intent into precision-engineered execution.
---

<div align="center">

# 🚀 Syntra AI 
### Cognitive AI Operating System & Orchestration Middleware

> **An advanced, enterprise-grade AI orchestration pipeline that transforms raw human intent into token-dense, precision-engineered prompts and multi-agent execution pipelines.**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

</div>

<br>

**Syntra AI** is a high-performance Developer Intelligence Platform that acts as a powerful middleware engine between humans and LLMs. Designed to solve the unpredictability of AI interactions, Syntra forces structure, evaluates complexity, and automatically orchestrates complex tasks across multiple specialized agents.

Instead of writing a basic prompt and hoping for the best, Syntra analyzes your intent, distills your context, and builds a complete **Execution Pipeline** before any code is generated.

---

## 🌟 Core Architecture & Engines

Syntra AI is broken down into four discrete, highly-optimized cognitive engines:

### 1. 🚦 The Intelligent Router (Orchestration Engine)
Stop guessing which AI tool you need. The Orchestrator acts as an enterprise project manager. It analyzes complex user requests and:
- Extracts **Primary & Secondary Intents**.
- Assembles a specialized team of **Primary and Supporting Agents**.
- Maps out a vertical **Execution Pipeline**.
- Calculates confidence scoring and formulates the single highest-impact **Clarification Question** if required data is missing.

### 2. 🗜️ Context Compressor (Distillation Engine)
A semantic noise-reduction engine. It aggressively optimizes massive payloads (like raw logs, articles, and verbose context) into high-density representations.
- Analyzes and measures original vs. compressed token size.
- Mathematically computes a **Meaning Preservation Score** to ensure zero context loss.

### 3. 🧠 Intent Intelligence Engine
Extracts hidden cognitive metadata from raw human thought. It categorizes the prompt's structural hierarchy:
- Detects **North Star Missions** and Long-Term Visions.
- Generates **Strategic Intelligence** (Business/Product roadmaps, MVPs, Value Propositions).
- Flags **Hidden Conflicts** and identifies missing information before execution.

### 4. 🎯 Prompt Refinement Engine
Transforms vague, messy inputs into structured, token-dense, precision-engineered prompts ready for enterprise execution. Evaluates the prompt's DNA, assigns risk classifications, and scores the prompt's structural improvement.

---

## 🛠️ Technical Stack & System Design

Syntra AI was engineered with a relentless focus on stability, performance, and UX.

- **Backend Logic (FastAPI):** Strictly typed with **Pydantic** schemas ensuring LLMs output deterministic JSON. Every engine runs through robust routing controllers.
- **Frontend Visualization (Streamlit):** A heavily customized, glassmorphic UI featuring real-time telemetry dashboards, interactive pipeline visualization, and progress metric cards.
- **LLM Fallback Architecture:** Engineered for 100% uptime. Syntra seamlessly attempts requests on a primary LLM (Gemini 2.0 Flash) and gracefully cascades to secondary fallback APIs (OpenRouter Llama 3, Groq) with sub-second switching.
- **Secure Error Handling:** Global frontend interceptors prevent raw JSON traces or technical stack errors from bleeding into the UI, dynamically translating HTTP 422/502s into user-friendly guidance.
- **Containerization:** fully Dockerized and structured to deploy instantaneously to Hugging Face Spaces or Render.

---

## 🚀 Deployment & Local Setup

Syntra AI is 100% Dockerized. Both the FastAPI backend and Streamlit frontend are spun up concurrently via a single shell script, making it incredibly lightweight to deploy.

### Running Locally (Docker)
Ensure Docker is installed on your machine.
```bash
# Build the image
docker build -t syntra-ai .

# Run the container (Maps to port 7860)
docker run -p 7860:7860 -e GEMINI_API_KEY=your_key -e GROQ_API_KEY=your_key syntra-ai
```
Access the UI at `http://localhost:7860`.

### Running Locally (Native)
1. Install Python 3.11+.
2. Install the requirements:
```bash
pip install -r syntra_backend/requirements.txt
```
3. Boot the backend server in one terminal:
```bash
cd syntra_backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
4. Boot the frontend in another terminal:
```bash
streamlit run streamlit_app.py
```

---

## 🧠 Philosophy

*“AI shouldn't just be a chat box. It should be a cognitive operating system.”*

Syntra AI was built to demonstrate that the true power of Large Language Models isn't in their raw text generation, but in structured **orchestration**. By forcing models to adhere to strict Pydantic schemas and pipeline designs, Syntra elevates AI from a basic tool into an autonomous enterprise engine.
