"""
Main FastAPI Application
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config import settings
from presentation.api import (
    health_router,
    whatsapp_router,
    client_router,
    analytics_router,
    user_router
)
from presentation.middlewares import (
    error_handler,
    rate_limiter,
    request_logger
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    
    # Initialize services
    # await initialize_database()
    # await initialize_whatsapp()
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    # await cleanup_resources()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="WhatsApp Analytics Platform with PyWA",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production() else None,
    redoc_url="/redoc" if not settings.is_production() else None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers
)

# Add custom middlewares
app.middleware("http")(error_handler)
app.middleware("http")(request_logger)

if settings.rate_limit_enabled:
    app.middleware("http")(rate_limiter)

# Include routers
app.include_router(health_router, prefix="/api/health", tags=["Health"])
app.include_router(whatsapp_router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(client_router, prefix="/api/clients", tags=["Clients"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(user_router, prefix="/api/users", tags=["Users"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment
    }

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }

# Custom exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested URL {request.url.path} was not found",
            "path": request.url.path
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An internal server error occurred"
        }
    )


def run_server():
    """Run the FastAPI server"""
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development(),
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    run_server()