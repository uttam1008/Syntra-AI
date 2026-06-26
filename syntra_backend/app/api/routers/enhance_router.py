import time, json
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Request
from app.services.analytics_repo import log_request_async
from app.models.schemas import EnhanceRequest, EnhanceResponse, IntentIntelligence
from app.services.enhancer import generate_enhanced_prompt
from app.core.rate_limiter import rate_limit

router = APIRouter(prefix='/v1', tags=["Enhancement"])

@router.post("/enhance", response_model=EnhanceResponse)
async def handle_enhance_prompt_request(request: EnhanceRequest, background_tasks: BackgroundTasks, _rl: None = Depends(rate_limit)):
    """
    Takes a weak prompt in the JSON body and returns an enhanced prompt.
    """
    try:
        start_time = time.time()
        # Pass request.prompt (extracting the string from the Pydantic model)
        enhancement_result_data = await generate_enhanced_prompt(request.prompt)

        # Helper to calculate mathematical score based on the 7 DNA attributes
        def calc_score(dna: dict) -> int:
            intent = dna.get("intent_clarity", 0)
            context = dna.get("context_completeness", 0)
            constraints = dna.get("constraint_coverage", 0)
            reasoning = dna.get("reasoning_depth", 0)
            structure = dna.get("output_structure", 0)
            specificity = dna.get("specificity", 0)
            ambiguity = dna.get("ambiguity_risk", 100) # Default to 100% risk if missing
            
            score = (intent * 0.20) + (context * 0.20) + (constraints * 0.15) + \
                    (reasoning * 0.15) + (structure * 0.15) + (specificity * 0.10) + \
                    ((100 - ambiguity) * 0.05)
            
            return min(100, max(0, int(round(score))))
        
        orig_dna = enhancement_result_data.get("original_dna", {})
        enh_dna = enhancement_result_data.get("enhanced_dna", {})
        
        orig_score = calc_score(orig_dna)
        enh_score = calc_score(enh_dna)
        
        # Determine Risk Classification from original prompt
        risk_class = "🟢 Strong Prompt"
        if orig_score < 40 or orig_dna.get("ambiguity_risk", 0) > 70:
            risk_class = "🔴 High Ambiguity"
        elif orig_dna.get("constraint_coverage", 0) < 40 or orig_dna.get("specificity", 0) < 40:
            risk_class = "🟠 Weakly Defined"
        elif orig_dna.get("context_completeness", 0) < 50:
            risk_class = "🟡 Missing Context"
            
        # Build IntentIntelligence from LLM response, with safe defaults
        raw_intent = enhancement_result_data.get("intent_intelligence", {})
        intent_intel = IntentIntelligence(
            primary_goal=raw_intent.get("primary_goal", "Not detected"),
            secondary_goals=raw_intent.get("secondary_goals", []),
            domains=raw_intent.get("domains", []),
            complexity=raw_intent.get("complexity", "unknown"),
            ambiguity=raw_intent.get("ambiguity", "unknown"),
            execution_types=raw_intent.get("execution_types", []),
            confidence_scores=raw_intent.get("confidence_scores", {})
        )
        
        # Return data matching the EnhanceResponse structure
        response = EnhanceResponse(
            original_prompt=request.prompt,
            enhanced_prompt=enhancement_result_data.get("enhanced_prompt", ""),
            reasoning=enhancement_result_data.get("reasoning", "No reasoning provided."),
            intent_intelligence=intent_intel,
            output_mode=enhancement_result_data.get("output_mode", "BLUEPRINT"),
            original_dna=orig_dna,
            enhanced_dna=enh_dna,
            original_score=orig_score,
            enhanced_score=enh_score,
            improvement_score=(enh_score - orig_score),
            risk_classification=risk_class,
            missing_information=enhancement_result_data.get("missing_information", []),
            enhancement_strategy_used=enhancement_result_data.get("enhancement_strategy_used", "General"),
            recommended_routes=enhancement_result_data.get("recommended_routes", []),
            improvement_summary=enhancement_result_data.get("improvement_summary", [])
        )
        
        processing_time_ms = (time.time() - start_time) * 1000
        processing_time_ms = (time.time() - start_time) * 1000
        background_tasks.add_task(
            log_request_async,
            endpoint="/v1/enhance",
            payload=request.model_dump(),
            response_status=200,
            processing_time_ms=processing_time_ms
        )
        
        return response
    except HTTPException:
        # If the LLM client raised an HTTPException, re-raise it so FastAPI handles it
        raise
    except Exception as e:
         # If our own code broke (e.g., variable typo), catch it here as a 500
        print(f"Service Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Our AI brain encountered an unexpected hiccup. Please try your request again.")
