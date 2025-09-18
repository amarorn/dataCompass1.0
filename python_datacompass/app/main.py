"""
DataCompass Python - FastAPI application entry point.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_database, close_database
from app.core.logging import setup_logging, get_logger
from app.presentation.api import analytics, clients, whatsapp, ml


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting DataCompass Python application...")
    
    try:
        # Initialize database
        await init_database()
        logger.info("Database initialized successfully")
        
        # Initialize services
        # This is where you would initialize repositories and services
        logger.info("Services initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down DataCompass Python application...")
        
        try:
            # Close database connections
            await close_database()
            logger.info("Database connections closed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    # Setup logging
    setup_logging()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="DataCompass - WhatsApp Analytics Platform in Python",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
    
    # Add trusted host middleware
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure appropriately for production
        )
    
    # Add request logging middleware
    @app.middleware("http")
    async def log_requests(request, call_next):
        """Log all requests."""
        start_time = asyncio.get_event_loop().time()
        
        response = await call_next(request)
        
        process_time = asyncio.get_event_loop().time() - start_time
        
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        return response
    
    # Include routers
    app.include_router(whatsapp.router)
    app.include_router(analytics.router)
    app.include_router(clients.router)
    app.include_router(ml.router)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        try:
            from app.core.database import db_manager
            db_health = await db_manager.health_check()
            
            return {
                "status": "healthy",
                "service": settings.app_name,
                "version": settings.app_version,
                "environment": settings.environment,
                "database": db_health,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "service": settings.app_name,
                    "version": settings.app_version,
                    "error": str(e),
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            )
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "environment": settings.environment,
            "docs": "/docs" if settings.debug else "Documentation not available in production",
            "health": "/health"
        }
    
    # Exception handlers
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        """Handle 404 errors."""
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "message": "The requested resource was not found",
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(500)
    async def internal_error_handler(request, exc):
        """Handle 500 errors."""
        logger.error(f"Internal server error: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )