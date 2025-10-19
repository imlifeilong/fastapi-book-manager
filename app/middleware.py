from fastapi import Request
import time


async def simple_logger(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    process_time = time.time() - start
    print(f"{request.method} {request.url.path} completed_in={process_time:.3f}s status={response.status_code}")
    return response
