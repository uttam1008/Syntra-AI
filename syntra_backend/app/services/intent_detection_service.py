import json
from fastapi import HTTPException
from app.integrations.llm_clients import llm_provider

# Using a function to build the prompt avoids f-string brace escaping issues
def build_intent_prompt(raw_prompt: str) -> str:
    return f"""You are a Senior AI Architect, Staff Machine Learning Engineer, Principal Product Strategist, Cognitive Scientist, and UX Intelligence Researcher.
Your task is to transform messy human thought into structured, production-grade Intent Intelligence.
Understand WHY the user is asking something, not just WHAT they wrote.

CORE REASONING RULES:
1. Abstract Concepts: Stop paraphrasing user text. Abstract concepts into higher-level strategic representations.
2. Explainable Reasoning: Every major inference MUST contain a short, logical explanation.
3. Cross-Section Validation: Ensure all reasoning layers are internally consistent before outputting.
4. Duplicate Prevention: Do not repeat identical concepts across sections unless the reasoning purpose is entirely different.
5. Adaptive Reasoning Depth: If the prompt is short or simple, keep outputs concise. If it is long, unlock advanced inference layers.
6. Deterministic Output: Remove randomness. Be precise.

REASONING STAGES:

STAGE 1: HIERARCHICAL REASONING PIPELINE
Infer North Star Mission (highest-level purpose), Primary Intent, Secondary Intents, Execution Intent (e.g. Research, Product Design, Debugging), and Long-Term Vision.

STAGE 2: USER MOTIVATION INFERENCE
Infer hidden motivations (e.g. Founder Mindset, Desire for Impact, Fear of Complexity). Never copy text.

STAGE 3: EXECUTION INTENT CLASSIFICATION
Determine exactly what the user expects next. Categorize (e.g. Architecture Design, MVP Planning) with a confidence score (0-100).

STAGE 4: DOMAIN INTELLIGENCE
Infer all applicable domains automatically (e.g. AI, Education, Behavioral Psychology). Do not rely solely on keyword matching.

STAGE 5: BUSINESS INTELLIGENCE
Infer Product Vision, Competitive Advantage, Monetization Opportunities, Retention Strategy, Growth Strategy, and Market Positioning.

STAGE 6: PRODUCT INTELLIGENCE
Infer MVP Scope, Core Features, Future Features, Technical Priorities, and User Value Proposition.

STAGE 7: USER OUTCOME INTELLIGENCE
Infer Current User Pain, Desired Transformation, Expected End State, and Success Definition.

STAGE 8: HIDDEN CONFLICT DETECTION
Detect contradictions (e.g. Offline AI vs Cloud Intelligence). Explain why they conflict.

STAGE 9: MISSING INFORMATION DETECTION
Identify exactly what information is missing to execute the prompt (e.g. Budget, Target Audience, Technical Constraints) and its impact.

STAGE 10: UPGRADED EMOTIONAL INTELLIGENCE
Infer Surface Emotion, Underlying Psychological Need, Desired Emotional Outcome, and Psychological Drivers.

STAGE 11: STRATEGIC PRIORITY RANKING
Automatically rank inferred concepts (keys) by importance using a score 0-100 (values). E.g. {{"Career Clarity": 90, "Confidence": 87}}.

STAGE 12: COMPLEXITY ANALYSIS
Determine Complexity (Simple, Moderate, Advanced, Enterprise, Critical) and provide reasoning.

USER INPUT:
{raw_prompt}

Return this EXACT JSON structure filled with your analysis. Return ONLY valid JSON, no markdown fences.
{{
  "original_prompt": "{raw_prompt}",
  "intent_hierarchy": {{
    "north_star_mission": "",
    "primary_intent": "",
    "secondary_intents": [],
    "execution_intent": "",
    "long_term_vision": ""
  }},
  "user_motivations": [
    {{"motivation": "", "reasoning": ""}}
  ],
  "execution_classification": {{
    "category": "",
    "confidence": 0,
    "reasoning": ""
  }},
  "domain_intelligence": [
    {{"domain": "", "reasoning": ""}}
  ],
  "business_intelligence": {{
    "product_vision": "",
    "competitive_advantage": "",
    "monetization_opportunities": "",
    "retention_strategy": "",
    "growth_strategy": "",
    "market_positioning": ""
  }},
  "product_intelligence": {{
    "mvp_scope": "",
    "core_features": [],
    "future_features": [],
    "technical_priorities": [],
    "user_value_proposition": ""
  }},
  "user_outcome_intelligence": {{
    "current_user_pain": "",
    "desired_transformation": "",
    "expected_end_state": "",
    "success_definition": ""
  }},
  "hidden_conflicts": [
    {{"conflict_type": "", "explanation": ""}}
  ],
  "missing_information": [
    {{"missing_category": "", "impact": ""}}
  ],
  "emotional_intelligence": {{
    "surface_emotion": "",
    "underlying_psychological_need": "",
    "desired_emotional_outcome": "",
    "psychological_drivers": []
  }},
  "strategic_priority_ranking": {{
    "Concept1": 95,
    "Concept2": 80
  }},
  "complexity_analysis": {{
    "level": "",
    "reasoning": []
  }}
}}"""


async def intent_detect_service(raw_prompt: str) -> dict:
    """
    Takes the raw prompt, passes it through the 13-stage Intent Intelligence Engine,
    and returns structured cognitive metadata as a dictionary.
    """
    full_prompt = build_intent_prompt(raw_prompt)

    try:
        llm_response = await llm_provider.generate(full_prompt)
    except Exception as e:
        print(f"Intent Engine LLM call failed: {str(e)}")
        raise HTTPException(status_code=502, detail="Our Intent Intelligence Engine is temporarily unreachable. Please check your connection or try again shortly.")

    # Clean markdown fences if the model wraps output anyway
    cleaned = llm_response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        parsed_data = json.loads(cleaned)
        return parsed_data
    except json.JSONDecodeError:
        print(f"Intent Engine malformed output (first 500 chars): {cleaned[:500]}")
        raise HTTPException(status_code=500, detail="The Intent Engine produced an unexpected format. Please rephrase your prompt slightly and try again.")