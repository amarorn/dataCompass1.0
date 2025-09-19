"""
DataCompass Python - Versão sem dependência de MongoDB para testes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Importar as rotas
from app.presentation.api.whatsapp import router as whatsapp_router
from app.presentation.api.analytics import router as analytics_router
from app.presentation.api.clients import router as clients_router
from app.presentation.api.ml import router as ml_router

app = FastAPI(
    title="DataCompass Python - Test Version",
    description="WhatsApp Analytics Platform - Versão de Teste",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "DataCompass Python API - Test Version",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "features": [
            "WhatsApp Integration",
            "Analytics & Insights", 
            "Machine Learning",
            "Client Management"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": "disabled (test mode)",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Incluir as rotas
app.include_router(whatsapp_router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(clients_router, prefix="/api/clients", tags=["Clients"])
app.include_router(ml_router, prefix="/api/ml", tags=["Machine Learning"])

if __name__ == "__main__":
    uvicorn.run(
        "main_no_db:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
