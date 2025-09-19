"""
Interaction repository interface.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from app.domain.entities.interaction import Interaction, InteractionType, SentimentType


class IInteractionRepository(ABC):
    """Interaction repository interface."""
    
    @abstractmethod
    async def create(self, interaction: Interaction) -> Interaction:
        """Create a new interaction."""
        pass
    
    @abstractmethod
    async def get_by_id(self, interaction_id: str) -> Optional[Interaction]:
        """Get interaction by ID."""
        pass
    
    @abstractmethod
    async def get_by_client_id(
        self, 
        client_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interaction]:
        """Get interactions by client ID."""
        pass
    
    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        interaction_type: Optional[InteractionType] = None,
        sentiment: Optional[SentimentType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Interaction]:
        """Get all interactions with optional filtering."""
        pass
    
    @abstractmethod
    async def update(self, interaction: Interaction) -> Interaction:
        """Update an existing interaction."""
        pass
    
    @abstractmethod
    async def delete(self, interaction_id: str) -> bool:
        """Delete an interaction."""
        pass
    
    @abstractmethod
    async def get_by_type(self, interaction_type: InteractionType) -> List[Interaction]:
        """Get interactions by type."""
        pass
    
    @abstractmethod
    async def get_by_sentiment(self, sentiment: SentimentType) -> List[Interaction]:
        """Get interactions by sentiment."""
        pass
    
    @abstractmethod
    async def get_purchases(self, client_id: Optional[str] = None) -> List[Interaction]:
        """Get purchase interactions."""
        pass
    
    @abstractmethod
    async def get_complaints(self) -> List[Interaction]:
        """Get complaint interactions."""
        pass
    
    @abstractmethod
    async def get_recent_interactions(
        self, 
        client_id: str, 
        days: int = 30
    ) -> List[Interaction]:
        """Get recent interactions for a client."""
        pass
    
    @abstractmethod
    async def count_by_client(self, client_id: str) -> int:
        """Count interactions for a client."""
        pass
    
    @abstractmethod
    async def count_by_type(self, interaction_type: InteractionType) -> int:
        """Count interactions by type."""
        pass
    
    @abstractmethod
    async def get_interaction_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get interaction statistics."""
        pass