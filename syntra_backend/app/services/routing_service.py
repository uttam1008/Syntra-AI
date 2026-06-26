# app/services/routing_service.py
# The Routing Orchestrator — coordinates intent detection, prompt resolution,
# and LLM execution to produce the final RoutingResponse.

import json
import re
from fastapi import HTTPException
from app.integrations.llm_clients import llm_provider
from app.prompts.routing_prompts import ORCHESTRATOR_PROMPT
from app.models.schemas import OrchestrationResponse, RoutingResponse


def _extract_json(raw: str) -> dict:
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        raise HTTPException(status_code=500, detail="The Orchestrator got a bit confused while mapping out your pipeline. A quick retry usually fixes this!")


async def routing_service(
    prompt: str,
    code_context: str | None,
    language: str | None
) -> RoutingResponse:
    """
    The Orchestration Engine pipeline:
    Analyzes the request, identifies multiple intents, assigns primary/supporting agents,
    and builds an execution pipeline.
    """

    # ── STEP A: Build Orchestrator Prompt ──
    execution_input = f"Developer Request:\n{prompt}"

    if code_context:
        execution_input += f"\n\nCode Context:\n```\n{code_context}\n```"

    if language:
        execution_input += f"\n\nTarget Language: {language}"

    full_prompt = f"{ORCHESTRATOR_PROMPT}\n\n{execution_input}"

    # ── STEP B: Execute Orchestrator LLM ──
    try:
        raw_orchestration = await llm_provider.generate(full_prompt)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail="The Orchestrator couldn't complete the planning phase due to a temporary AI provider timeout. Please try again."
        )

    # ── STEP C: Parse and Validate ──
    parsed_json = _extract_json(raw_orchestration)
    orchestration = OrchestrationResponse(**parsed_json)

    # ── STEP D: Return Orchestration Plan (Execution paused for visualization) ──
    return RoutingResponse(
        orchestration=orchestration,
        execution_result="Execution paused. Orchestration pipeline ready."
    )
