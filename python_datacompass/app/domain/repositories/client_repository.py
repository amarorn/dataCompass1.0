"""
Client repository interface.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.client import Client, ClientSegment, ChurnRisk


class IClientRepository(ABC):
    """Client repository interface."""
    
    @abstractmethod
    async def create(self, client: Client) -> Client:
        """Create a new client."""
        pass
    
    @abstractmethod
    async def get_by_id(self, client_id: str) -> Optional[Client]:
        """Get client by ID."""
        pass
    
    @abstractmethod
    async def get_by_whatsapp_number(self, whatsapp_number: str) -> Optional[Client]:
        """Get client by WhatsApp number."""
        pass
    
    @abstractmethod
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        segment: Optional[ClientSegment] = None,
        churn_risk: Optional[ChurnRisk] = None
    ) -> List[Client]:
        """Get all clients with optional filtering."""
        pass
    
    @abstractmethod
    async def update(self, client: Client) -> Client:
        """Update an existing client."""
        pass
    
    @abstractmethod
    async def delete(self, client_id: str) -> bool:
        """Delete a client."""
        pass
    
    @abstractmethod
    async def get_by_segment(self, segment: ClientSegment) -> List[Client]:
        """Get clients by segment."""
        pass
    
    @abstractmethod
    async def get_high_risk_clients(self) -> List[Client]:
        """Get clients with high churn risk."""
        pass
    
    @abstractmethod
    async def get_vip_clients(self) -> List[Client]:
        """Get VIP clients."""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Get total number of clients."""
        pass
    
    @abstractmethod
    async def search(self, query: str) -> List[Client]:
        """Search clients by name, email, or WhatsApp number."""
        pass