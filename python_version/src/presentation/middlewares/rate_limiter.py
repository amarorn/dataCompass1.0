"""
Rate Limiter Middleware
"""

import time
from collections import defaultdict
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from ...config import settings

# Store request counts
request_counts = defaultdict(lambda: {"count": 0, "reset_time": time.time()})


async def rate_limiter(request: Request, call_next):
    """
    Rate limiting middleware
    """
    # Get client IP
    client_ip = request.client.host
    
    # Get current time
    current_time = time.time()
    
    # Get or create rate limit data
    rate_data = request_counts[client_ip]
    
    # Reset counter if period has passed
    if current_time - rate_data["reset_time"] > settings.rate_limit_period:
        rate_data["count"] = 0
        rate_data["reset_time"] = current_time
    
    # Check rate limit
    if rate_data["count"] >= settings.rate_limit_requests:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "message": f"Rate limit exceeded. Try again in {settings.rate_limit_period} seconds"
            }
        )
    
    # Increment counter
    rate_data["count"] += 1
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_requests)
    response.headers["X-RateLimit-Remaining"] = str(
        settings.rate_limit_requests - rate_data["count"]
    )
    response.headers["X-RateLimit-Reset"] = str(int(rate_data["reset_time"] + settings.rate_limit_period))
    
    return response
