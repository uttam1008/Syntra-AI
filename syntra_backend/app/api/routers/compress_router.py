import time, json
from fastapi import APIRouter, BackgroundTasks, Depends

from app.services.analytics_repo import log_request_async
from app.models.schemas import CompressRequest, CompressResponse
from app.services.compressor import compress_text
from app.core.rate_limiter import rate_limit

router = APIRouter(prefix="/v1", tags=["Compressor Engine"])

@router.post("/compress", response_model=CompressResponse)
async def compress_endpoint(request: CompressRequest, background_tasks: BackgroundTasks, _rl: None = Depends(rate_limit)):
    """
    Semantic Compression Engine — transforms noisy verbose input into
    high-density semantic representations using a 9-stage pipeline.
    
    Supports 3 compression modes:
    - LIGHT: 20-40% reduction, 95-98% meaning preservation
    - BALANCED: 50-70% reduction, 90-95% meaning preservation (default)
    - AGGRESSIVE: 70-85% reduction, 80-90% meaning preservation
    """
    start_time = time.time()
    
    # Run the full 9-stage semantic compression pipeline
    response = await compress_text(request)
    
    processing_time_ms = (time.time() - start_time) * 1000


    
    background_tasks.add_task(
        log_request_async,
        endpoint="/v1/compress",
        payload=request.model_dump(),
        response_status=200,
        processing_time_ms=processing_time_ms
    )
    
    return response
