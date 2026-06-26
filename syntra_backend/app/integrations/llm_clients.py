from google import genai
from google.api_core.exceptions import GoogleAPIError
from fastapi import HTTPException
from app.core.config import settings
from abc import ABC, abstractmethod

# 1. The Interface (The Contract)
class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """All LLM providers must implement this method."""
        pass

import httpx

# 2. The Concrete Implementation (Gemini)
class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        self.model_name = 'gemini-2.0-flash'
        
    async def generate(self, prompt: str) -> str:
        if not self.client:
            raise HTTPException(status_code=500, detail="The AI engine is currently resting because its Gemini API key is missing.")
        try:
            # We use .aio for asynchronous calls in the new SDK
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except genai.errors.APIError as e:
            print(f"Gemini API Error: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected LLM Error: {str(e)}")
            raise

class OpenRouterProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model_name = "meta-llama/llama-3.3-70b-instruct:free"  # Stable high-quality free model via OpenRouter
        
    async def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise HTTPException(status_code=500, detail="The AI engine is currently resting because its API key is missing. Please ask an administrator to plug it in.")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:3000", # Required by OpenRouter
            "X-Title": "Syntra AI", # Required by OpenRouter
        }
        
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as e:
                print(f"OpenRouter HTTP Error: {e.response.text}")
                raise HTTPException(status_code=502, detail="Our AI brain is currently experiencing high traffic and couldn't process your request right away. Please try again in a few seconds!")
            except Exception as e:
                print(f"OpenRouter Unexpected Error: {str(e)}")
                raise HTTPException(status_code=500, detail="Our AI brain encountered an unexpected hiccup. Please try your request again.")

class GroqProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model_name = "llama-3.3-70b-versatile"  # Groq's high quality fast model
        
    async def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise HTTPException(status_code=500, detail="The backup AI engine is currently resting because its API key is missing. Please ask an administrator to plug it in.")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as e:
                print(f"Groq HTTP Error: {e.response.text}")
                raise HTTPException(status_code=502, detail="Our AI servers are a bit overloaded right now. Give it a few seconds and try again.")
            except Exception as e:
                print(f"Groq Unexpected Error: {str(e)}")
                raise HTTPException(status_code=500, detail="Our AI backup servers hit a temporary snag. Please try again.")

class HybridLLMProvider(BaseLLMProvider):
    def __init__(self):
        self.primary = GeminiProvider()
        self.fallback_1 = OpenRouterProvider()
        self.fallback_2 = GroqProvider()

    async def generate(self, prompt: str) -> str:
        try:
            # 1. Try Primary (Gemini native)
            return await self.primary.generate(prompt)
        except Exception as e:
            print(f"[HybridLLM] Primary (Gemini) failed — {type(e).__name__}: {str(e)}")
            
            try:
                # 2. Fallback to OpenRouter
                print(f"[HybridLLM] Switching to 1st Fallback (OpenRouter)...")
                return await self.fallback_1.generate(prompt)
            except Exception as e2:
                print(f"[HybridLLM] 1st Fallback (OpenRouter) failed — {type(e2).__name__}: {str(e2)}")
                
                # 3. Final Fallback to Groq
                print(f"[HybridLLM] Switching to 2nd Fallback (Groq)...")
                return await self.fallback_2.generate(prompt)

# 3. Dependency Injection Setup
llm_provider = HybridLLMProvider()
