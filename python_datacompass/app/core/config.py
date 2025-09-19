"""
Application configuration settings.
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = Field(default="DataCompass Python", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment")
    
    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # Database
    mongodb_uri: str = Field(
        default="mongodb://localhost:27017/datacompass",
        description="MongoDB connection URI"
    )
    database_name: str = Field(default="datacompass", description="Database name")
    
    # WhatsApp Business API
    whatsapp_token: Optional[str] = Field(default=None, description="WhatsApp access token")
    whatsapp_phone_number_id: Optional[str] = Field(
        default=None, 
        description="WhatsApp phone number ID"
    )
    whatsapp_webhook_verify_token: str = Field(
        default="datacompass_webhook_2025",
        description="WhatsApp webhook verification token"
    )
    whatsapp_webhook_secret: Optional[str] = Field(
        default=None,
        description="WhatsApp webhook secret"
    )
    
    # Security
    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT secret key"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expire_minutes: int = Field(default=30, description="JWT expiration in minutes")
    
    # CORS
    cors_origins: list[str] = Field(default=["*"], description="CORS allowed origins")
    cors_methods: list[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "PATCH"],
        description="CORS allowed methods"
    )
    cors_headers: list[str] = Field(
        default=["Content-Type", "Authorization"],
        description="CORS allowed headers"
    )
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per minute")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    # File Upload
    max_file_size: int = Field(default=10 * 1024 * 1024, description="Max file size in bytes (10MB)")
    allowed_file_types: list[str] = Field(
        default=["text/csv", "application/csv"],
        description="Allowed file types"
    )
    
    # Analytics
    enable_ml_processing: bool = Field(default=True, description="Enable ML processing")
    chart_generation_timeout: int = Field(default=300, description="Chart generation timeout in seconds")
    
    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()