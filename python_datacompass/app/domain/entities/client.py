"""
Client entity - represents a WhatsApp user/customer.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field, validator


class ClientSegment(str, Enum):
    """Client segmentation categories."""
    VIP = "VIP"
    FREQUENT = "FREQUENT"
    OCCASIONAL = "OCCASIONAL"
    INACTIVE = "INACTIVE"


class ChurnRisk(str, Enum):
    """Churn risk levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Client(BaseModel):
    """Client entity representing a WhatsApp user."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    whatsapp_number: str = Field(..., description="WhatsApp phone number")
    name: Optional[str] = Field(None, description="Client name")
    email: Optional[str] = Field(None, description="Client email")
    age: Optional[int] = Field(None, ge=0, le=150, description="Client age")
    city: Optional[str] = Field(None, description="Client city")
    profession: Optional[str] = Field(None, description="Client profession")
    income: Optional[float] = Field(None, ge=0, description="Client income")
    segment: ClientSegment = Field(default=ClientSegment.OCCASIONAL)
    engagement_score: float = Field(default=0.0, ge=0.0, le=100.0)
    churn_risk: ChurnRisk = Field(default=ChurnRisk.LOW)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('whatsapp_number')
    def validate_whatsapp_number(cls, v: str) -> str:
        """Validate WhatsApp number format."""
        clean_number = ''.join(filter(str.isdigit, v))
        if len(clean_number) < 10 or len(clean_number) > 15:
            raise ValueError('Invalid WhatsApp number format')
        return clean_number
    
    def update_profile(self, **kwargs) -> None:
        """Update client profile information."""
        allowed_fields = {
            'name', 'email', 'age', 'city', 'profession', 'income'
        }
        
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)
        
        self.updated_at = datetime.utcnow()
    
    def update_segment(self, segment: ClientSegment) -> None:
        """Update client segment."""
        self.segment = segment
        self.updated_at = datetime.utcnow()
    
    def update_engagement_score(self, score: float) -> None:
        """Update engagement score."""
        if not 0.0 <= score <= 100.0:
            raise ValueError('Engagement score must be between 0 and 100')
        self.engagement_score = score
        self.updated_at = datetime.utcnow()
    
    def update_churn_risk(self, risk: ChurnRisk) -> None:
        """Update churn risk."""
        self.churn_risk = risk
        self.updated_at = datetime.utcnow()
    
    def is_vip(self) -> bool:
        """Check if client is VIP."""
        return self.segment == ClientSegment.VIP
    
    def is_high_risk(self) -> bool:
        """Check if client has high churn risk."""
        return self.churn_risk in [ChurnRisk.HIGH, ChurnRisk.CRITICAL]
    
    def has_complete_profile(self) -> bool:
        """Check if client has complete profile information."""
        return all([
            self.name,
            self.email,
            self.age,
            self.city,
            self.profession
        ])
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }