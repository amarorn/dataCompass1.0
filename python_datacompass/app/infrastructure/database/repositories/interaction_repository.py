"""
MongoDB implementation of Interaction repository.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from app.core.logging import LoggerMixin
from app.domain.entities.interaction import Interaction, InteractionType, SentimentType
from app.domain.repositories.interaction_repository import IInteractionRepository
from app.infrastructure.database.models.interaction_model import InteractionModel


class MongoDBInteractionRepository(IInteractionRepository, LoggerMixin):
    """MongoDB implementation of Interaction repository."""
    
    async def create(self, interaction: Interaction) -> Interaction:
        """Create a new interaction."""
        try:
            model = InteractionModel.from_entity(interaction)
            await model.insert()
            self.logger.info(f"Interaction {interaction.id} created successfully")
            return model.to_entity()
        except Exception as e:
            self.logger.error(f"Error creating interaction: {e}")
            raise
    
    async def get_by_id(self, interaction_id: str) -> Optional[Interaction]:
        """Get interaction by ID."""
        try:
            model = await InteractionModel.get(interaction_id)
            return model.to_entity() if model else None
        except Exception as e:
            self.logger.error(f"Error getting interaction by ID {interaction_id}: {e}")
            return None
    
    async def get_by_client_id(
        self, 
        client_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interaction]:
        """Get interactions by client ID."""
        try:
            models = await InteractionModel.find(
                InteractionModel.client_id == client_id
            ).sort("-created_at").skip(skip).limit(limit).to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting interactions for client {client_id}: {e}")
            return []
    
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
        try:
            query = {}
            if interaction_type:
                query["type"] = interaction_type
            if sentiment:
                query["sentiment"] = sentiment
            if start_date or end_date:
                date_query = {}
                if start_date:
                    date_query["$gte"] = start_date
                if end_date:
                    date_query["$lte"] = end_date
                query["created_at"] = date_query
            
            models = await InteractionModel.find(
                query
            ).sort("-created_at").skip(skip).limit(limit).to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting interactions: {e}")
            return []
    
    async def update(self, interaction: Interaction) -> Interaction:
        """Update an existing interaction."""
        try:
            model = await InteractionModel.get(interaction.id)
            if not model:
                raise ValueError(f"Interaction {interaction.id} not found")
            
            # Update fields
            model.client_id = interaction.client_id
            model.type = interaction.type
            model.content = interaction.content
            model.value = interaction.value
            model.category = interaction.category
            model.sentiment = interaction.sentiment
            model.metadata = interaction.metadata
            
            await model.save()
            self.logger.info(f"Interaction {interaction.id} updated successfully")
            return model.to_entity()
        except Exception as e:
            self.logger.error(f"Error updating interaction {interaction.id}: {e}")
            raise
    
    async def delete(self, interaction_id: str) -> bool:
        """Delete an interaction."""
        try:
            model = await InteractionModel.get(interaction_id)
            if not model:
                return False
            
            await model.delete()
            self.logger.info(f"Interaction {interaction_id} deleted successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting interaction {interaction_id}: {e}")
            return False
    
    async def get_by_type(self, interaction_type: InteractionType) -> List[Interaction]:
        """Get interactions by type."""
        try:
            models = await InteractionModel.find(
                InteractionModel.type == interaction_type
            ).sort("-created_at").to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting interactions by type {interaction_type}: {e}")
            return []
    
    async def get_by_sentiment(self, sentiment: SentimentType) -> List[Interaction]:
        """Get interactions by sentiment."""
        try:
            models = await InteractionModel.find(
                InteractionModel.sentiment == sentiment
            ).sort("-created_at").to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting interactions by sentiment {sentiment}: {e}")
            return []
    
    async def get_purchases(self, client_id: Optional[str] = None) -> List[Interaction]:
        """Get purchase interactions."""
        try:
            query = {"type": InteractionType.PURCHASE}
            if client_id:
                query["client_id"] = client_id
            
            models = await InteractionModel.find(query).sort("-created_at").to_list()
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting purchases: {e}")
            return []
    
    async def get_complaints(self) -> List[Interaction]:
        """Get complaint interactions."""
        try:
            models = await InteractionModel.find(
                InteractionModel.type == InteractionType.COMPLAINT
            ).sort("-created_at").to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting complaints: {e}")
            return []
    
    async def get_recent_interactions(
        self, 
        client_id: str, 
        days: int = 30
    ) -> List[Interaction]:
        """Get recent interactions for a client."""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            models = await InteractionModel.find(
                InteractionModel.client_id == client_id,
                InteractionModel.created_at >= start_date
            ).sort("-created_at").to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting recent interactions for client {client_id}: {e}")
            return []
    
    async def count_by_client(self, client_id: str) -> int:
        """Count interactions for a client."""
        try:
            return await InteractionModel.count(
                InteractionModel.client_id == client_id
            )
        except Exception as e:
            self.logger.error(f"Error counting interactions for client {client_id}: {e}")
            return 0
    
    async def count_by_type(self, interaction_type: InteractionType) -> int:
        """Count interactions by type."""
        try:
            return await InteractionModel.count(
                InteractionModel.type == interaction_type
            )
        except Exception as e:
            self.logger.error(f"Error counting interactions by type {interaction_type}: {e}")
            return 0
    
    async def get_interaction_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get interaction statistics."""
        try:
            query = {}
            if start_date or end_date:
                date_query = {}
                if start_date:
                    date_query["$gte"] = start_date
                if end_date:
                    date_query["$lte"] = end_date
                query["created_at"] = date_query
            
            # Get counts by type
            type_counts = {}
            for interaction_type in InteractionType:
                count = await InteractionModel.count(
                    {**query, "type": interaction_type}
                )
                type_counts[interaction_type.value] = count
            
            # Get counts by sentiment
            sentiment_counts = {}
            for sentiment in SentimentType:
                count = await InteractionModel.count(
                    {**query, "sentiment": sentiment}
                )
                sentiment_counts[sentiment.value] = count
            
            # Get total count
            total_count = await InteractionModel.count(query)
            
            return {
                "total_interactions": total_count,
                "by_type": type_counts,
                "by_sentiment": sentiment_counts,
                "period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting interaction stats: {e}")
            return {}