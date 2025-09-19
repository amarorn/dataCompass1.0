"""
Insight entity - represents analytics insights and recommendations.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class InsightType(str, Enum):
    """Types of insights."""
    TREND = "TREND"
    ANOMALY = "ANOMALY"
    RECOMMENDATION = "RECOMMENDATION"
    PREDICTION = "PREDICTION"
    SEGMENTATION = "SEGMENTATION"
    PERFORMANCE = "PERFORMANCE"


class InsightPriority(str, Enum):
    """Insight priority levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Insight(BaseModel):
    """Insight entity representing analytics insights."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    client_id: Optional[str] = Field(None, description="Related client ID")
    type: InsightType = Field(..., description="Insight type")
    title: str = Field(..., max_length=200, description="Insight title")
    description: str = Field(..., description="Detailed description")
    priority: InsightPriority = Field(default=InsightPriority.MEDIUM)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score")
    data: Dict[str, Any] = Field(default_factory=dict, description="Supporting data")
    recommendations: List[str] = Field(default_factory=list, description="Action recommendations")
    tags: List[str] = Field(default_factory=list, description="Insight tags")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Insight expiration")
    
    def add_recommendation(self, recommendation: str) -> None:
        """Add a recommendation to the insight."""
        if recommendation not in self.recommendations:
            self.recommendations.append(recommendation)
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the insight."""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def update_confidence(self, confidence: float) -> None:
        """Update confidence score."""
        if not 0.0 <= confidence <= 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        self.confidence = confidence
    
    def set_expiration(self, days: int) -> None:
        """Set insight expiration."""
        self.expires_at = datetime.utcnow().replace(
            day=datetime.utcnow().day + days
        )
    
    def is_expired(self) -> bool:
        """Check if insight has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def is_high_priority(self) -> bool:
        """Check if insight is high priority."""
        return self.priority in [InsightPriority.HIGH, InsightPriority.CRITICAL]
    
    def is_high_confidence(self) -> bool:
        """Check if insight has high confidence."""
        return self.confidence >= 0.8
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class InsightCreate(BaseModel):
    """Schema for creating a new insight."""
    client_id: Optional[str] = None
    type: InsightType
    title: str = Field(..., max_length=200)
    description: str
    priority: InsightPriority = InsightPriority.MEDIUM
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    data: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class InsightUpdate(BaseModel):
    """Schema for updating an insight."""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    priority: Optional[InsightPriority] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    data: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    tags: Optional[List[str]] = None