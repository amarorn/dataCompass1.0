"""
Application Configuration
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "DataCompass 2.0"
    app_version: str = "2.0.0"
    debug: bool = Field(default=False, alias="DEBUG")
    port: int = Field(default=3000, alias="PORT")
    host: str = Field(default="0.0.0.0", alias="HOST")
    environment: str = Field(default="development", alias="NODE_ENV")
    
    # JWT
    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440  # 24 hours
    
    # WhatsApp Business API
    whatsapp_token: str = Field(alias="WHATSAPP_TOKEN")
    whatsapp_phone_number_id: str = Field(alias="WHATSAPP_PHONE_NUMBER_ID")
    whatsapp_webhook_verify_token: str = Field(
        default="datacompass_webhook_2025", 
        alias="WHATSAPP_WEBHOOK_VERIFY_TOKEN"
    )
    whatsapp_webhook_secret: str = Field(alias="WHATSAPP_WEBHOOK_SECRET")
    whatsapp_business_id: Optional[str] = Field(default=None, alias="WHATSAPP_BUSINESS_ID")
    whatsapp_app_id: Optional[str] = Field(default=None, alias="WHATSAPP_APP_ID")
    whatsapp_app_secret: Optional[str] = Field(default=None, alias="WHATSAPP_APP_SECRET")
    
    # PyWA Specific
    pywa_server_url: str = Field(
        default="https://graph.facebook.com/v21.0", 
        alias="PYWA_SERVER_URL"
    )
    pywa_webhook_endpoint: str = Field(
        default="/api/whatsapp/webhook", 
        alias="PYWA_WEBHOOK_ENDPOINT"
    )
    pywa_callback_url: Optional[str] = Field(default=None, alias="PYWA_CALLBACK_URL")
    
    # MongoDB
    mongodb_host: str = Field(default="localhost", alias="MONGODB_HOST")
    mongodb_port: int = Field(default=27017, alias="MONGODB_PORT")
    mongodb_database: str = Field(default="whatsapp_analytics", alias="MONGODB_DATABASE")
    mongodb_username: Optional[str] = Field(default=None, alias="MONGODB_USERNAME")
    mongodb_password: Optional[str] = Field(default=None, alias="MONGODB_PASSWORD")
    
    @property
    def mongodb_url(self) -> str:
        """Generate MongoDB connection URL"""
        if self.mongodb_username and self.mongodb_password:
            return f"mongodb://{self.mongodb_username}:{self.mongodb_password}@{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_database}"
        return f"mongodb://{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_database}"
    
    # Redis (optional)
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    
    # CORS
    cors_origins: List[str] = Field(default=["*"], alias="CORS_ORIGINS")
    cors_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "PATCH"], 
        alias="CORS_METHODS"
    )
    cors_headers: List[str] = Field(
        default=["Content-Type", "Authorization"], 
        alias="CORS_HEADERS"
    )
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=60, alias="RATE_LIMIT_PERIOD")
    
    # Analytics
    enable_ml_features: bool = Field(default=True, alias="ENABLE_ML_FEATURES")
    enable_auto_responses: bool = Field(default=True, alias="ENABLE_AUTO_RESPONSES")
    enable_sentiment_analysis: bool = Field(default=True, alias="ENABLE_SENTIMENT_ANALYSIS")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment.lower() == "development"


# Create global settings instance
settings = Settings()
