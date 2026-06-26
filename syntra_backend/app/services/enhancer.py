from app.prompts.system_prompt import ENHANCER_SYSTEM_PROMPT
from app.integrations.llm_clients import llm_provider
import json
from fastapi import HTTPException

async def generate_enhanced_prompt(raw_prompt: str) -> dict:
    # 1. Inject the user's weak prompt into our powerful template
    injected_system_prompt = ENHANCER_SYSTEM_PROMPT.replace("{raw_prompt}", raw_prompt)
    
    # 2. Send the massive, formatted prompt to Gemini
    raw_llm_response = await llm_provider.generate(injected_system_prompt)
    
    # Strip markdown logic
    clean_llm_response = raw_llm_response.strip()
    if clean_llm_response.startswith("```json"):
        clean_llm_response = clean_llm_response[7:]
    if clean_llm_response.startswith("```"):
        clean_llm_response = clean_llm_response[3:]
    if clean_llm_response.endswith("```"):
        clean_llm_response = clean_llm_response[:-3]
    clean_llm_response = clean_llm_response.strip()

    try:
        # Attempt to parse the LLM's text into a Python dictionary
        structured_response = json.loads(clean_llm_response)
        return structured_response
    except json.JSONDecodeError as e:
        # If the LLM disobeyed and gave us bad JSON, we fail gracefully
        print(f"Failed to parse LLM output: {raw_llm_response}")
        raise HTTPException(status_code=500, detail="The Enhancement AI returned an unreadable format. Trying your request one more time usually resolves this.")
