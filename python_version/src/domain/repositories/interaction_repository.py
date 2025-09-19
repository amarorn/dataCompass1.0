"""
Interaction Repository Interface
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..entities.interaction import Interaction, InteractionType, SentimentType


class IInteractionRepository(ABC):
    """Interface for interaction repository"""
    
    @abstractmethod
    async def create(self, interaction: Interaction) -> Interaction:
        """Create a new interaction"""
        pass
    
    @abstractmethod
    async def get_by_id(self, interaction_id: str) -> Optional[Interaction]:
        """Get interaction by ID"""
        pass
    
    @abstractmethod
    async def get_by_message_id(self, message_id: str) -> Optional[Interaction]:
        """Get interaction by WhatsApp message ID"""
        pass
    
    @abstractmethod
    async def get_by_client_id(
        self,
        client_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interaction]:
        """Get interactions by client ID"""
        pass
    
    @abstractmethod
    async def get_by_whatsapp_number(
        self,
        whatsapp_number: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interaction]:
        """Get interactions by WhatsApp number"""
        pass
    
    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Interaction]:
        """Get all interactions with pagination and filters"""
        pass
    
    @abstractmethod
    async def update(self, interaction_id: str, interaction: Interaction) -> Optional[Interaction]:
        """Update interaction"""
        pass
    
    @abstractmethod
    async def delete(self, interaction_id: str) -> bool:
        """Delete an interaction"""
        pass
    
    @abstractmethod
    async def get_by_type(
        self,
        interaction_type: InteractionType,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interaction]:
        """Get interactions by type"""
        pass
    
    @abstractmethod
    async def get_by_sentiment(
        self,
        sentiment: SentimentType,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interaction]:
        """Get interactions by sentiment"""
        pass
    
    @abstractmethod
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interaction]:
        """Get interactions within date range"""
        pass
    
    @abstractmethod
    async def get_unanswered(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interaction]:
        """Get interactions that haven't been responded to"""
        pass
    
    @abstractmethod
    async def get_recent(
        self,
        hours: int = 24,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interaction]:
        """Get recent interactions within specified hours"""
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count interactions with optional filters"""
        pass
    
    @abstractmethod
    async def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get interaction statistics"""
        pass
    
    @abstractmethod
    async def get_sentiment_distribution(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Get sentiment distribution"""
        pass
    
    @abstractmethod
    async def get_type_distribution(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Get interaction type distribution"""
        pass
    
    @abstractmethod
    async def get_response_time_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """Get response time statistics"""
        pass
    
    @abstractmethod
    async def get_trending_topics(
        self,
        limit: int = 10,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get trending topics from interactions"""
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        fields: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interaction]:
        """Search interactions by query"""
        pass
    
    @abstractmethod
    async def mark_as_responded(
        self,
        interaction_id: str,
        response_content: str,
        response_type: str = "text"
    ) -> bool:
        """Mark interaction as responded"""
        pass
