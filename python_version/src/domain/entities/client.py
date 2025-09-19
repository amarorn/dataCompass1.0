"""
Client Entity
"""

from enum import Enum
from typing import Optional
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator
import re


class ClientSegment(str, Enum):
    """Client segmentation categories"""
    VIP = "VIP"
    FREQUENT = "FREQUENT"
    OCCASIONAL = "OCCASIONAL"
    INACTIVE = "INACTIVE"


class ChurnRisk(str, Enum):
    """Churn risk levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Client(BaseModel):
    """Client entity representing a WhatsApp user"""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    whatsapp_number: str
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    city: Optional[str] = None
    profession: Optional[str] = None
    income: Optional[float] = Field(None, ge=0)
    segment: ClientSegment = ClientSegment.OCCASIONAL
    engagement_score: float = Field(default=0, ge=0, le=100)
    churn_risk: ChurnRisk = ChurnRisk.LOW
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional fields for analytics
    total_interactions: int = 0
    last_interaction: Optional[datetime] = None
    total_purchase_value: float = 0
    average_response_time: Optional[float] = None
    preferred_contact_time: Optional[str] = None
    
    @field_validator('whatsapp_number')
    @classmethod
    def validate_whatsapp_number(cls, v: str) -> str:
        """Validate and clean WhatsApp number"""
        # Remove all non-numeric characters
        clean_number = re.sub(r'\D', '', v)
        
        # Validate length (10-15 digits)
        if len(clean_number) < 10 or len(clean_number) > 15:
            raise ValueError('Invalid WhatsApp number format')
        
        return clean_number
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format"""
        if v is None:
            return v
        
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        
        return v.lower()
    
    def update_profile(self, **kwargs) -> None:
        """Update client profile information"""
        updateable_fields = [
            'name', 'email', 'age', 'city', 'profession', 'income'
        ]
        
        for field, value in kwargs.items():
            if field in updateable_fields and value is not None:
                setattr(self, field, value)
        
        self.updated_at = datetime.utcnow()
    
    def update_segment(self, segment: ClientSegment) -> None:
        """Update client segment"""
        self.segment = segment
        self.updated_at = datetime.utcnow()
    
    def update_engagement_score(self, score: float) -> None:
        """Update engagement score"""
        if score < 0 or score > 100:
            raise ValueError('Engagement score must be between 0 and 100')
        
        self.engagement_score = score
        self.updated_at = datetime.utcnow()
    
    def update_churn_risk(self, risk: ChurnRisk) -> None:
        """Update churn risk level"""
        self.churn_risk = risk
        self.updated_at = datetime.utcnow()
    
    def record_interaction(self) -> None:
        """Record a new interaction"""
        self.total_interactions += 1
        self.last_interaction = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def add_purchase(self, value: float) -> None:
        """Add a purchase to client history"""
        if value < 0:
            raise ValueError('Purchase value cannot be negative')
        
        self.total_purchase_value += value
        self.updated_at = datetime.utcnow()
    
    def is_vip(self) -> bool:
        """Check if client is VIP"""
        return self.segment == ClientSegment.VIP
    
    def is_high_risk(self) -> bool:
        """Check if client has high churn risk"""
        return self.churn_risk in [ChurnRisk.HIGH, ChurnRisk.CRITICAL]
    
    def has_complete_profile(self) -> bool:
        """Check if client has complete profile information"""
        required_fields = ['name', 'email', 'age', 'city', 'profession']
        return all(getattr(self, field) is not None for field in required_fields)
    
    def calculate_lifetime_value(self) -> float:
        """Calculate estimated customer lifetime value"""
        # Simple LTV calculation - can be enhanced with ML models
        base_value = self.total_purchase_value
        
        # Apply multipliers based on segment
        segment_multipliers = {
            ClientSegment.VIP: 2.5,
            ClientSegment.FREQUENT: 1.8,
            ClientSegment.OCCASIONAL: 1.2,
            ClientSegment.INACTIVE: 0.5
        }
        
        # Apply risk adjustment
        risk_adjustments = {
            ChurnRisk.LOW: 1.0,
            ChurnRisk.MEDIUM: 0.8,
            ChurnRisk.HIGH: 0.5,
            ChurnRisk.CRITICAL: 0.2
        }
        
        ltv = base_value * segment_multipliers[self.segment] * risk_adjustments[self.churn_risk]
        
        # Engagement bonus
        if self.engagement_score > 80:
            ltv *= 1.3
        elif self.engagement_score > 60:
            ltv *= 1.1
        
        return round(ltv, 2)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "whatsapp_number": self.whatsapp_number,
            "name": self.name,
            "email": self.email,
            "age": self.age,
            "city": self.city,
            "profession": self.profession,
            "income": self.income,
            "segment": self.segment.value,
            "engagement_score": self.engagement_score,
            "churn_risk": self.churn_risk.value,
            "total_interactions": self.total_interactions,
            "last_interaction": self.last_interaction.isoformat() if self.last_interaction else None,
            "total_purchase_value": self.total_purchase_value,
            "lifetime_value": self.calculate_lifetime_value(),
            "has_complete_profile": self.has_complete_profile(),
            "is_vip": self.is_vip(),
            "is_high_risk": self.is_high_risk(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    class Config:
        use_enum_values = False
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
