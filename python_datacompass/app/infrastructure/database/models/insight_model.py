"""
Insight MongoDB model using Beanie.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from beanie import Document, Indexed
from pydantic import Field

from app.domain.entities.insight import InsightPriority, InsightType


class InsightModel(Document):
    """MongoDB model for Insight entity."""
    
    client_id: Optional[Indexed(str)] = None
    type: InsightType
    title: str
    description: str
    priority: InsightPriority = InsightPriority.MEDIUM
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    data: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    class Settings:
        name = "insights"
        indexes = [
            "client_id",
            "type",
            "priority",
            "created_at",
            "expires_at",
            "tags"
        ]
    
    @classmethod
    def from_entity(cls, insight) -> "InsightModel":
        """Create model from entity."""
        return cls(
            id=insight.id,
            client_id=insight.client_id,
            type=insight.type,
            title=insight.title,
            description=insight.description,
            priority=insight.priority,
            confidence=insight.confidence,
            data=insight.data,
            recommendations=insight.recommendations,
            tags=insight.tags,
            created_at=insight.created_at,
            expires_at=insight.expires_at
        )
    
    def to_entity(self):
        """Convert model to entity."""
        from app.domain.entities.insight import Insight
        
        return Insight(
            id=str(self.id),
            client_id=self.client_id,
            type=self.type,
            title=self.title,
            description=self.description,
            priority=self.priority,
            confidence=self.confidence,
            data=self.data,
            recommendations=self.recommendations,
            tags=self.tags,
            created_at=self.created_at,
            expires_at=self.expires_at
        )