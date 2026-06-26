import os
import httpx
from fastapi import HTTPException
from abc import ABC, abstractmethod

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"

# ── Base Interface ─────────────────────────────────────────────────────────────
class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """All LLM providers must implement this method."""
        pass

# ── Groq Provider ──────────────────────────────────────────────────────────────
class GroqProvider(BaseLLMProvider):
    def __init__(self):
        # Key is read fresh per-request so it picks up HuggingFace Secrets at runtime
        self.model_name = GROQ_MODEL

    async def generate(self, prompt: str) -> str:
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="GROQ_API_KEY is not configured. Add it in Hugging Face Space Settings → Variables and Secrets."
            )
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    GROQ_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as e:
                print(f"Groq HTTP Error: {e.response.text}")
                raise HTTPException(
                    status_code=502,
                    detail="The AI engine is experiencing high load. Please try again in a few seconds."
                )
            except Exception as e:
                print(f"Groq Unexpected Error: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="The AI engine encountered an unexpected error. Please try again."
                )

# ── Singleton Instance ─────────────────────────────────────────────────────────
llm_provider = GroqProvider()
