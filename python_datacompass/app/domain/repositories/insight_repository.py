"""
Insight repository interface.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from app.domain.entities.insight import Insight, InsightType, InsightPriority


class IInsightRepository(ABC):
    """Insight repository interface."""
    
    @abstractmethod
    async def create(self, insight: Insight) -> Insight:
        """Create a new insight."""
        pass
    
    @abstractmethod
    async def get_by_id(self, insight_id: str) -> Optional[Insight]:
        """Get insight by ID."""
        pass
    
    @abstractmethod
    async def get_by_client_id(
        self, 
        client_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Insight]:
        """Get insights by client ID."""
        pass
    
    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        insight_type: Optional[InsightType] = None,
        priority: Optional[InsightPriority] = None,
        is_expired: Optional[bool] = None
    ) -> List[Insight]:
        """Get all insights with optional filtering."""
        pass
    
    @abstractmethod
    async def update(self, insight: Insight) -> Insight:
        """Update an existing insight."""
        pass
    
    @abstractmethod
    async def delete(self, insight_id: str) -> bool:
        """Delete an insight."""
        pass
    
    @abstractmethod
    async def get_by_type(self, insight_type: InsightType) -> List[Insight]:
        """Get insights by type."""
        pass
    
    @abstractmethod
    async def get_by_priority(self, priority: InsightPriority) -> List[Insight]:
        """Get insights by priority."""
        pass
    
    @abstractmethod
    async def get_high_priority_insights(self) -> List[Insight]:
        """Get high priority insights."""
        pass
    
    @abstractmethod
    async def get_expired_insights(self) -> List[Insight]:
        """Get expired insights."""
        pass
    
    @abstractmethod
    async def get_recent_insights(
        self, 
        days: int = 7
    ) -> List[Insight]:
        """Get recent insights."""
        pass
    
    @abstractmethod
    async def get_by_tags(self, tags: List[str]) -> List[Insight]:
        """Get insights by tags."""
        pass
    
    @abstractmethod
    async def count_by_client(self, client_id: str) -> int:
        """Count insights for a client."""
        pass
    
    @abstractmethod
    async def count_by_type(self, insight_type: InsightType) -> int:
        """Count insights by type."""
        pass
    
    @abstractmethod
    async def get_insight_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get insight statistics."""
        pass
    
    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Clean up expired insights."""
        pass