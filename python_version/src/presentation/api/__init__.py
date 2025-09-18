"""
API Routes
"""

from .health import router as health_router
from .whatsapp import router as whatsapp_router
from .clients import router as client_router
from .analytics import router as analytics_router
from .users import router as user_router

__all__ = [
    "health_router",
    "whatsapp_router",
    "client_router",
    "analytics_router",
    "user_router"
]