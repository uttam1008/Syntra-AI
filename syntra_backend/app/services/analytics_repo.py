import json

async def log_request_async(endpoint: str, payload: dict, response_status: int, processing_time_ms: float):
    """
    Logs API requests to the console asynchronously (Database removed).
    """
    try:
        payload_str = json.dumps(payload) if isinstance(payload, dict) else str(payload)
        print(f"[API Log] {endpoint} | Status: {response_status} | Time: {processing_time_ms:.2f}ms")
    except Exception as e:
        print(f"Failed to log request: {str(e)}")
