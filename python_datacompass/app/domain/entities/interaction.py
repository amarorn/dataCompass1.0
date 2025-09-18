"""
Interaction entity - represents a WhatsApp message/interaction.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, validator


class InteractionType(str, Enum):
    """Types of interactions."""
    PURCHASE = "PURCHASE"
    FEEDBACK = "FEEDBACK"
    QUESTION = "QUESTION"
    COMPLAINT = "COMPLAINT"
    PROFILE_UPDATE = "PROFILE_UPDATE"
    GENERAL = "GENERAL"


class SentimentType(str, Enum):
    """Sentiment analysis results."""
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"


class Interaction(BaseModel):
    """Interaction entity representing a WhatsApp message."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    client_id: str = Field(..., description="Client ID")
    type: InteractionType = Field(..., description="Interaction type")
    content: str = Field(..., description="Message content")
    value: Optional[float] = Field(None, ge=0, description="Monetary value if applicable")
    category: Optional[str] = Field(None, description="Interaction category")
    sentiment: SentimentType = Field(default=SentimentType.NEUTRAL)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('content')
    def validate_content(cls, v: str) -> str:
        """Validate message content."""
        if not v or not v.strip():
            raise ValueError('Interaction content cannot be empty')
        if len(v) > 1000:
            raise ValueError('Interaction content cannot exceed 1000 characters')
        return v.strip()
    
    def update_sentiment(self, sentiment: SentimentType) -> None:
        """Update sentiment analysis."""
        self.sentiment = sentiment
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the interaction."""
        self.metadata[key] = value
    
    def is_purchase(self) -> bool:
        """Check if interaction is a purchase."""
        return self.type == InteractionType.PURCHASE
    
    def is_complaint(self) -> bool:
        """Check if interaction is a complaint."""
        return self.type == InteractionType.COMPLAINT
    
    def is_positive(self) -> bool:
        """Check if sentiment is positive."""
        return self.sentiment == SentimentType.POSITIVE
    
    def is_negative(self) -> bool:
        """Check if sentiment is negative."""
        return self.sentiment == SentimentType.NEGATIVE
    
    def has_value(self) -> bool:
        """Check if interaction has monetary value."""
        return self.value is not None and self.value > 0
    
    def get_value_or_zero(self) -> float:
        """Get value or return 0."""
        return self.value or 0.0
    
    @classmethod
    def create_purchase(
        cls,
        client_id: str,
        content: str,
        value: float,
        category: Optional[str] = None
    ) -> "Interaction":
        """Create a purchase interaction."""
        return cls(
            client_id=client_id,
            type=InteractionType.PURCHASE,
            content=content,
            value=value,
            category=category,
            sentiment=SentimentType.POSITIVE
        )
    
    @classmethod
    def create_feedback(
        cls,
        client_id: str,
        content: str,
        sentiment: SentimentType
    ) -> "Interaction":
        """Create a feedback interaction."""
        return cls(
            client_id=client_id,
            type=InteractionType.FEEDBACK,
            content=content,
            sentiment=sentiment
        )
    
    @classmethod
    def create_complaint(
        cls,
        client_id: str,
        content: str
    ) -> "Interaction":
        """Create a complaint interaction."""
        return cls(
            client_id=client_id,
            type=InteractionType.COMPLAINT,
            content=content,
            sentiment=SentimentType.NEGATIVE
        )
    
    @classmethod
    def create_question(
        cls,
        client_id: str,
        content: str
    ) -> "Interaction":
        """Create a question interaction."""
        return cls(
            client_id=client_id,
            type=InteractionType.QUESTION,
            content=content,
            sentiment=SentimentType.NEUTRAL
        )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }