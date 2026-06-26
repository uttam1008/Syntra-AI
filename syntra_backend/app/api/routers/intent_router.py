import time, json
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from app.models.schemas import IntentRequest, IntentResponse
from app.services.intent_detection_service import intent_detect_service
from app.services.analytics_repo import log_request_async
from app.core.rate_limiter import rate_limit

router = APIRouter(prefix="/v1", tags=["Intent Intelligence"])

@router.post("/intent", response_model=IntentResponse)
async def detect_intent(request: IntentRequest, background_tasks: BackgroundTasks, _rl: None = Depends(rate_limit)):
    """
    13-Stage Intent Intelligence Engine.
    Transforms raw human thought into structured cognitive metadata.
    """
    try:
        start_time = time.time()
        data = await intent_detect_service(request.prompt)

        # The Intent Intelligence prompt now generates structured JSON that perfectly
        # matches the massive nested IntentResponse Pydantic schema.
        response = IntentResponse(**data)

        processing_time_ms = (time.time() - start_time) * 1000


        background_tasks.add_task(
            log_request_async,
            endpoint="/v1/intent",
            payload=request.model_dump(),
            response_status=200,
            processing_time_ms=processing_time_ms
        )

        return response
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Unexpected error in intent router: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error processing intent.")
