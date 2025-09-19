"""
Interaction Entity
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field


class InteractionType(str, Enum):
    """Types of customer interactions"""
    PURCHASE = "PURCHASE"
    COMPLAINT = "COMPLAINT"
    FEEDBACK = "FEEDBACK"
    QUESTION = "QUESTION"
    GENERAL = "GENERAL"
    PROFILE_UPDATE = "PROFILE_UPDATE"
    REGISTRATION = "REGISTRATION"


class SentimentType(str, Enum):
    """Sentiment analysis results"""
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"


class MessageType(str, Enum):
    """WhatsApp message types"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    LOCATION = "location"
    STICKER = "sticker"
    REACTION = "reaction"


class Interaction(BaseModel):
    """Interaction entity representing a customer interaction via WhatsApp"""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    client_id: str
    message_id: str
    whatsapp_number: str
    timestamp: datetime
    message_type: MessageType
    message_content: Optional[str] = None
    interaction_type: InteractionType = InteractionType.GENERAL
    sentiment: SentimentType = SentimentType.NEUTRAL
    confidence_score: float = Field(default=0, ge=0, le=1)
    
    # Extracted data
    extracted_value: Optional[float] = None
    extracted_category: Optional[str] = None
    extracted_intent: Optional[str] = None
    extracted_entities: Dict[str, Any] = Field(default_factory=dict)
    
    # Response information
    response_sent: bool = False
    response_content: Optional[str] = None
    response_timestamp: Optional[datetime] = None
    response_type: Optional[str] = None
    
    # Analytics data
    processing_time_ms: Optional[int] = None
    keywords: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Media information (for non-text messages)
    media_id: Optional[str] = None
    media_url: Optional[str] = None
    media_mime_type: Optional[str] = None
    media_sha256: Optional[str] = None
    media_filename: Optional[str] = None
    
    # Location data (for location messages)
    location_latitude: Optional[float] = None
    location_longitude: Optional[float] = None
    location_name: Optional[str] = None
    location_address: Optional[str] = None
    
    def is_purchase(self) -> bool:
        """Check if interaction is a purchase"""
        return self.interaction_type == InteractionType.PURCHASE
    
    def is_complaint(self) -> bool:
        """Check if interaction is a complaint"""
        return self.interaction_type == InteractionType.COMPLAINT
    
    def is_positive(self) -> bool:
        """Check if sentiment is positive"""
        return self.sentiment == SentimentType.POSITIVE
    
    def is_negative(self) -> bool:
        """Check if sentiment is negative"""
        return self.sentiment == SentimentType.NEGATIVE
    
    def requires_response(self) -> bool:
        """Check if interaction requires a response"""
        # Questions and complaints typically require responses
        return self.interaction_type in [
            InteractionType.QUESTION,
            InteractionType.COMPLAINT,
            InteractionType.REGISTRATION
        ]
    
    def set_response(self, content: str, response_type: str = "text") -> None:
        """Set response information"""
        self.response_sent = True
        self.response_content = content
        self.response_timestamp = datetime.utcnow()
        self.response_type = response_type
        self.updated_at = datetime.utcnow()
    
    def add_keyword(self, keyword: str) -> None:
        """Add a keyword to the interaction"""
        if keyword and keyword not in self.keywords:
            self.keywords.append(keyword)
            self.updated_at = datetime.utcnow()
    
    def add_topic(self, topic: str) -> None:
        """Add a topic to the interaction"""
        if topic and topic not in self.topics:
            self.topics.append(topic)
            self.updated_at = datetime.utcnow()
    
    def calculate_priority(self) -> int:
        """Calculate interaction priority (0-10)"""
        priority = 5  # Base priority
        
        # Adjust based on interaction type
        type_priorities = {
            InteractionType.COMPLAINT: 3,
            InteractionType.QUESTION: 2,
            InteractionType.PURCHASE: 1,
            InteractionType.FEEDBACK: 0,
            InteractionType.GENERAL: -1,
            InteractionType.PROFILE_UPDATE: -1,
            InteractionType.REGISTRATION: 2
        }
        priority += type_priorities.get(self.interaction_type, 0)
        
        # Adjust based on sentiment
        if self.sentiment == SentimentType.NEGATIVE:
            priority += 2
        elif self.sentiment == SentimentType.POSITIVE:
            priority -= 1
        
        # Ensure priority is within bounds
        return max(0, min(10, priority))
    
    def get_response_time(self) -> Optional[float]:
        """Calculate response time in seconds"""
        if self.response_timestamp:
            delta = self.response_timestamp - self.timestamp
            return delta.total_seconds()
        return None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "client_id": self.client_id,
            "message_id": self.message_id,
            "whatsapp_number": self.whatsapp_number,
            "timestamp": self.timestamp.isoformat(),
            "message_type": self.message_type.value,
            "message_content": self.message_content,
            "interaction_type": self.interaction_type.value,
            "sentiment": self.sentiment.value,
            "confidence_score": self.confidence_score,
            "extracted_value": self.extracted_value,
            "extracted_category": self.extracted_category,
            "extracted_intent": self.extracted_intent,
            "extracted_entities": self.extracted_entities,
            "response_sent": self.response_sent,
            "response_content": self.response_content,
            "response_timestamp": self.response_timestamp.isoformat() if self.response_timestamp else None,
            "response_type": self.response_type,
            "response_time_seconds": self.get_response_time(),
            "priority": self.calculate_priority(),
            "processing_time_ms": self.processing_time_ms,
            "keywords": self.keywords,
            "topics": self.topics,
            "media_id": self.media_id,
            "media_url": self.media_url,
            "location_latitude": self.location_latitude,
            "location_longitude": self.location_longitude,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    class Config:
        use_enum_values = False
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
