"""
MongoDB implementation of Client repository.
"""

from typing import List, Optional

from app.core.logging import LoggerMixin
from app.domain.entities.client import Client, ClientSegment, ChurnRisk
from app.domain.repositories.client_repository import IClientRepository
from app.infrastructure.database.models.client_model import ClientModel


class MongoDBClientRepository(IClientRepository, LoggerMixin):
    """MongoDB implementation of Client repository."""
    
    async def create(self, client: Client) -> Client:
        """Create a new client."""
        try:
            model = ClientModel.from_entity(client)
            await model.insert()
            self.logger.info(f"Client {client.id} created successfully")
            return model.to_entity()
        except Exception as e:
            self.logger.error(f"Error creating client: {e}")
            raise
    
    async def get_by_id(self, client_id: str) -> Optional[Client]:
        """Get client by ID."""
        try:
            model = await ClientModel.get(client_id)
            return model.to_entity() if model else None
        except Exception as e:
            self.logger.error(f"Error getting client by ID {client_id}: {e}")
            return None
    
    async def get_by_whatsapp_number(self, whatsapp_number: str) -> Optional[Client]:
        """Get client by WhatsApp number."""
        try:
            clean_number = ''.join(filter(str.isdigit, whatsapp_number))
            model = await ClientModel.find_one(
                ClientModel.whatsapp_number == clean_number
            )
            return model.to_entity() if model else None
        except Exception as e:
            self.logger.error(f"Error getting client by WhatsApp number {whatsapp_number}: {e}")
            return None
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        segment: Optional[ClientSegment] = None,
        churn_risk: Optional[ChurnRisk] = None
    ) -> List[Client]:
        """Get all clients with optional filtering."""
        try:
            query = {}
            if segment:
                query["segment"] = segment
            if churn_risk:
                query["churn_risk"] = churn_risk
            
            models = await ClientModel.find(
                query
            ).skip(skip).limit(limit).to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting clients: {e}")
            return []
    
    async def update(self, client: Client) -> Client:
        """Update an existing client."""
        try:
            model = await ClientModel.get(client.id)
            if not model:
                raise ValueError(f"Client {client.id} not found")
            
            # Update fields
            model.whatsapp_number = client.whatsapp_number
            model.name = client.name
            model.email = client.email
            model.age = client.age
            model.city = client.city
            model.profession = client.profession
            model.income = client.income
            model.segment = client.segment
            model.engagement_score = client.engagement_score
            model.churn_risk = client.churn_risk
            model.updated_at = client.updated_at
            
            await model.save()
            self.logger.info(f"Client {client.id} updated successfully")
            return model.to_entity()
        except Exception as e:
            self.logger.error(f"Error updating client {client.id}: {e}")
            raise
    
    async def delete(self, client_id: str) -> bool:
        """Delete a client."""
        try:
            model = await ClientModel.get(client_id)
            if not model:
                return False
            
            await model.delete()
            self.logger.info(f"Client {client_id} deleted successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting client {client_id}: {e}")
            return False
    
    async def get_by_segment(self, segment: ClientSegment) -> List[Client]:
        """Get clients by segment."""
        try:
            models = await ClientModel.find(
                ClientModel.segment == segment
            ).to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting clients by segment {segment}: {e}")
            return []
    
    async def get_high_risk_clients(self) -> List[Client]:
        """Get clients with high churn risk."""
        try:
            models = await ClientModel.find(
                ClientModel.churn_risk.in_([ChurnRisk.HIGH, ChurnRisk.CRITICAL])
            ).to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting high risk clients: {e}")
            return []
    
    async def get_vip_clients(self) -> List[Client]:
        """Get VIP clients."""
        try:
            models = await ClientModel.find(
                ClientModel.segment == ClientSegment.VIP
            ).to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting VIP clients: {e}")
            return []
    
    async def count(self) -> int:
        """Get total number of clients."""
        try:
            return await ClientModel.count()
        except Exception as e:
            self.logger.error(f"Error counting clients: {e}")
            return 0
    
    async def search(self, query: str) -> List[Client]:
        """Search clients by name, email, or WhatsApp number."""
        try:
            # MongoDB text search
            models = await ClientModel.find(
                {
                    "$or": [
                        {"name": {"$regex": query, "$options": "i"}},
                        {"email": {"$regex": query, "$options": "i"}},
                        {"whatsapp_number": {"$regex": query, "$options": "i"}}
                    ]
                }
            ).to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error searching clients with query '{query}': {e}")
            return []