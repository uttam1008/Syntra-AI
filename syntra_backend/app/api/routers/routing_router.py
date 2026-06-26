import time, json
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends

from app.models.schemas import RoutingRequest, RoutingResponse
from app.services.routing_service import routing_service
from app.services.analytics_repo import log_request_async
from app.core.rate_limiter import rate_limit

router = APIRouter(prefix="/v1", tags=["Routing & Execution"])


@router.post("/chat", response_model=RoutingResponse)
async def chat(request: RoutingRequest, background_tasks: BackgroundTasks, _rl: None = Depends(rate_limit)):
    """
    The unified developer intelligence endpoint.

    Accepts a raw developer prompt with optional code context and language.
    Automatically classifies the intent, routes to the appropriate specialized
    agent, and returns both the classification metadata and the execution result.
    """
    try:
        start_time = time.time()
        # Delegate all work to the Routing Orchestrator service
        response = await routing_service(
            prompt=request.prompt,
            code_context=request.code_context,
            language=request.language
        )
        
        processing_time_ms = (time.time() - start_time) * 1000


        background_tasks.add_task(
            log_request_async,
            endpoint="/v1/chat",
            payload=request.model_dump(),
            response_status=200,
            processing_time_ms=processing_time_ms
        )
        
        return response

    except HTTPException as http_exc:
        # Pass through expected HTTP exceptions (e.g., 502 from LLM failure)
        raise http_exc

    except Exception as e:
        # Catch any unexpected errors and return a safe 500
        print(f"Unexpected error in routing router: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error in the Routing & Execution System."
        )
