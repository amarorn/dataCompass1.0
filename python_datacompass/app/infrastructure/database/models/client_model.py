"""
Client MongoDB model using Beanie.
"""

from datetime import datetime
from typing import Optional

from beanie import Document, Indexed
from pydantic import Field

from app.domain.entities.client import ClientSegment, ChurnRisk


class ClientModel(Document):
    """MongoDB model for Client entity."""
    
    whatsapp_number: Indexed(str, unique=True)
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None
    profession: Optional[str] = None
    income: Optional[float] = None
    segment: ClientSegment = ClientSegment.OCCASIONAL
    engagement_score: float = Field(default=0.0, ge=0.0, le=100.0)
    churn_risk: ChurnRisk = ChurnRisk.LOW
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "clients"
        indexes = [
            "whatsapp_number",
            "segment",
            "churn_risk",
            "engagement_score",
            "created_at"
        ]
    
    @classmethod
    def from_entity(cls, client) -> "ClientModel":
        """Create model from entity."""
        return cls(
            id=client.id,
            whatsapp_number=client.whatsapp_number,
            name=client.name,
            email=client.email,
            age=client.age,
            city=client.city,
            profession=client.profession,
            income=client.income,
            segment=client.segment,
            engagement_score=client.engagement_score,
            churn_risk=client.churn_risk,
            created_at=client.created_at,
            updated_at=client.updated_at
        )
    
    def to_entity(self):
        """Convert model to entity."""
        from app.domain.entities.client import Client
        
        return Client(
            id=str(self.id),
            whatsapp_number=self.whatsapp_number,
            name=self.name,
            email=self.email,
            age=self.age,
            city=self.city,
            profession=self.profession,
            income=self.income,
            segment=self.segment,
            engagement_score=self.engagement_score,
            churn_risk=self.churn_risk,
            created_at=self.created_at,
            updated_at=self.updated_at
        )