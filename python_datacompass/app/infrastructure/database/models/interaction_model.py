"""
Interaction MongoDB model using Beanie.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from beanie import Document, Indexed
from pydantic import Field

from app.domain.entities.interaction import InteractionType, SentimentType


class InteractionModel(Document):
    """MongoDB model for Interaction entity."""
    
    client_id: Indexed(str)
    type: InteractionType
    content: str
    value: Optional[float] = None
    category: Optional[str] = None
    sentiment: SentimentType = SentimentType.NEUTRAL
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "interactions"
        indexes = [
            "client_id",
            "type",
            "sentiment",
            "created_at",
            [("client_id", 1), ("created_at", -1)]  # Compound index
        ]
    
    @classmethod
    def from_entity(cls, interaction) -> "InteractionModel":
        """Create model from entity."""
        return cls(
            id=interaction.id,
            client_id=interaction.client_id,
            type=interaction.type,
            content=interaction.content,
            value=interaction.value,
            category=interaction.category,
            sentiment=interaction.sentiment,
            metadata=interaction.metadata,
            created_at=interaction.created_at
        )
    
    def to_entity(self):
        """Convert model to entity."""
        from app.domain.entities.interaction import Interaction
        
        return Interaction(
            id=str(self.id),
            client_id=self.client_id,
            type=self.type,
            content=self.content,
            value=self.value,
            category=self.category,
            sentiment=self.sentiment,
            metadata=self.metadata,
            created_at=self.created_at
        )