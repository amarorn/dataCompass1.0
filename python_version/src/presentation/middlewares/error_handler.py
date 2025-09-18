"""
Error Handler Middleware
"""

import logging
import traceback
from fastapi import Request, Response
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def error_handler(request: Request, call_next):
    """
    Global error handler middleware
    """
    try:
        response = await call_next(request)
        return response
        
    except Exception as exc:
        # Log the error
        logger.error(f"Unhandled error: {exc}")
        logger.error(traceback.format_exc())
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "path": str(request.url.path)
            }
        )