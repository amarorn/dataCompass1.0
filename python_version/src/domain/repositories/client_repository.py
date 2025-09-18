"""
Client Repository Interface
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..entities.client import Client, ClientSegment, ChurnRisk


class IClientRepository(ABC):
    """Interface for client repository"""
    
    @abstractmethod
    async def create(self, client: Client) -> Client:
        """Create a new client"""
        pass
    
    @abstractmethod
    async def get_by_id(self, client_id: str) -> Optional[Client]:
        """Get client by ID"""
        pass
    
    @abstractmethod
    async def get_by_whatsapp_number(self, whatsapp_number: str) -> Optional[Client]:
        """Get client by WhatsApp number"""
        pass
    
    @abstractmethod
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Client]:
        """Get all clients with pagination and filters"""
        pass
    
    @abstractmethod
    async def update(self, client_id: str, client: Client) -> Optional[Client]:
        """Update client information"""
        pass
    
    @abstractmethod
    async def delete(self, client_id: str) -> bool:
        """Delete a client"""
        pass
    
    @abstractmethod
    async def get_by_segment(
        self, 
        segment: ClientSegment,
        skip: int = 0,
        limit: int = 100
    ) -> List[Client]:
        """Get clients by segment"""
        pass
    
    @abstractmethod
    async def get_by_churn_risk(
        self, 
        risk: ChurnRisk,
        skip: int = 0,
        limit: int = 100
    ) -> List[Client]:
        """Get clients by churn risk level"""
        pass
    
    @abstractmethod
    async def get_vip_clients(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Client]:
        """Get VIP clients"""
        pass
    
    @abstractmethod
    async def get_inactive_clients(
        self,
        days_inactive: int = 30,
        skip: int = 0,
        limit: int = 100
    ) -> List[Client]:
        """Get clients inactive for specified days"""
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        fields: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Client]:
        """Search clients by query in specified fields"""
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count clients with optional filters"""
        pass
    
    @abstractmethod
    async def get_statistics(self) -> Dict[str, Any]:
        """Get client statistics"""
        pass
    
    @abstractmethod
    async def bulk_update_segment(
        self,
        client_ids: List[str],
        segment: ClientSegment
    ) -> int:
        """Bulk update client segments"""
        pass
    
    @abstractmethod
    async def bulk_update_churn_risk(
        self,
        client_ids: List[str],
        risk: ChurnRisk
    ) -> int:
        """Bulk update churn risk"""
        pass
    
    @abstractmethod
    async def get_engagement_distribution(self) -> Dict[str, int]:
        """Get distribution of engagement scores"""
        pass
    
    @abstractmethod
    async def get_top_clients(
        self,
        metric: str = "purchase_value",
        limit: int = 10
    ) -> List[Client]:
        """Get top clients by specified metric"""
        pass
    
    @abstractmethod
    async def exists(self, whatsapp_number: str) -> bool:
        """Check if client exists by WhatsApp number"""
        pass