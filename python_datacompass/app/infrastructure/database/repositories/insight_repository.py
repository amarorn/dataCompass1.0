"""
MongoDB implementation of Insight repository.
"""

from datetime import datetime
from typing import List, Optional

from app.core.logging import LoggerMixin
from app.domain.entities.insight import Insight, InsightType, InsightPriority
from app.domain.repositories.insight_repository import IInsightRepository
from app.infrastructure.database.models.insight_model import InsightModel


class MongoDBInsightRepository(IInsightRepository, LoggerMixin):
    """MongoDB implementation of Insight repository."""
    
    async def create(self, insight: Insight) -> Insight:
        """Create a new insight."""
        try:
            model = InsightModel.from_entity(insight)
            await model.insert()
            self.logger.info(f"Insight {insight.id} created successfully")
            return model.to_entity()
        except Exception as e:
            self.logger.error(f"Error creating insight: {e}")
            raise
    
    async def get_by_id(self, insight_id: str) -> Optional[Insight]:
        """Get insight by ID."""
        try:
            model = await InsightModel.get(insight_id)
            return model.to_entity() if model else None
        except Exception as e:
            self.logger.error(f"Error getting insight by ID {insight_id}: {e}")
            return None
    
    async def get_by_client_id(
        self, 
        client_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Insight]:
        """Get insights by client ID."""
        try:
            models = await InsightModel.find(
                InsightModel.client_id == client_id
            ).sort("-created_at").skip(skip).limit(limit).to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting insights for client {client_id}: {e}")
            return []
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        insight_type: Optional[InsightType] = None,
        priority: Optional[InsightPriority] = None,
        is_expired: Optional[bool] = None
    ) -> List[Insight]:
        """Get all insights with optional filtering."""
        try:
            query = {}
            if insight_type:
                query["type"] = insight_type
            if priority:
                query["priority"] = priority
            if is_expired is not None:
                now = datetime.utcnow()
                if is_expired:
                    query["expires_at"] = {"$lt": now}
                else:
                    query["$or"] = [
                        {"expires_at": {"$gte": now}},
                        {"expires_at": None}
                    ]
            
            models = await InsightModel.find(
                query
            ).sort("-created_at").skip(skip).limit(limit).to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting insights: {e}")
            return []
    
    async def update(self, insight: Insight) -> Insight:
        """Update an existing insight."""
        try:
            model = await InsightModel.get(insight.id)
            if not model:
                raise ValueError(f"Insight {insight.id} not found")
            
            # Update fields
            model.client_id = insight.client_id
            model.type = insight.type
            model.title = insight.title
            model.description = insight.description
            model.priority = insight.priority
            model.confidence = insight.confidence
            model.data = insight.data
            model.recommendations = insight.recommendations
            model.tags = insight.tags
            model.expires_at = insight.expires_at
            
            await model.save()
            self.logger.info(f"Insight {insight.id} updated successfully")
            return model.to_entity()
        except Exception as e:
            self.logger.error(f"Error updating insight {insight.id}: {e}")
            raise
    
    async def delete(self, insight_id: str) -> bool:
        """Delete an insight."""
        try:
            model = await InsightModel.get(insight_id)
            if not model:
                return False
            
            await model.delete()
            self.logger.info(f"Insight {insight_id} deleted successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting insight {insight_id}: {e}")
            return False
    
    async def get_by_type(self, insight_type: InsightType) -> List[Insight]:
        """Get insights by type."""
        try:
            models = await InsightModel.find(
                InsightModel.type == insight_type
            ).sort("-created_at").to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting insights by type {insight_type}: {e}")
            return []
    
    async def get_by_priority(self, priority: InsightPriority) -> List[Insight]:
        """Get insights by priority."""
        try:
            models = await InsightModel.find(
                InsightModel.priority == priority
            ).sort("-created_at").to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting insights by priority {priority}: {e}")
            return []
    
    async def get_high_priority_insights(self) -> List[Insight]:
        """Get high priority insights."""
        try:
            models = await InsightModel.find(
                InsightModel.priority.in_([InsightPriority.HIGH, InsightPriority.CRITICAL])
            ).sort("-created_at").to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting high priority insights: {e}")
            return []
    
    async def get_expired_insights(self) -> List[Insight]:
        """Get expired insights."""
        try:
            now = datetime.utcnow()
            models = await InsightModel.find(
                InsightModel.expires_at < now
            ).sort("-created_at").to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting expired insights: {e}")
            return []
    
    async def get_recent_insights(
        self, 
        days: int = 7
    ) -> List[Insight]:
        """Get recent insights."""
        try:
            from datetime import timedelta
            start_date = datetime.utcnow() - timedelta(days=days)
            
            models = await InsightModel.find(
                InsightModel.created_at >= start_date
            ).sort("-created_at").to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting recent insights: {e}")
            return []
    
    async def get_by_tags(self, tags: List[str]) -> List[Insight]:
        """Get insights by tags."""
        try:
            models = await InsightModel.find(
                {"tags": {"$in": tags}}
            ).sort("-created_at").to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting insights by tags {tags}: {e}")
            return []
    
    async def count_by_client(self, client_id: str) -> int:
        """Count insights for a client."""
        try:
            return await InsightModel.count(
                InsightModel.client_id == client_id
            )
        except Exception as e:
            self.logger.error(f"Error counting insights for client {client_id}: {e}")
            return 0
    
    async def count_by_type(self, insight_type: InsightType) -> int:
        """Count insights by type."""
        try:
            return await InsightModel.count(
                InsightModel.type == insight_type
            )
        except Exception as e:
            self.logger.error(f"Error counting insights by type {insight_type}: {e}")
            return 0
    
    async def get_insight_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get insight statistics."""
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
            for insight_type in InsightType:
                count = await InsightModel.count(
                    {**query, "type": insight_type}
                )
                type_counts[insight_type.value] = count
            
            # Get counts by priority
            priority_counts = {}
            for priority in InsightPriority:
                count = await InsightModel.count(
                    {**query, "priority": priority}
                )
                priority_counts[priority.value] = count
            
            # Get total count
            total_count = await InsightModel.count(query)
            
            # Get expired count
            now = datetime.utcnow()
            expired_count = await InsightModel.count(
                {**query, "expires_at": {"$lt": now}}
            )
            
            return {
                "total_insights": total_count,
                "expired_insights": expired_count,
                "by_type": type_counts,
                "by_priority": priority_counts,
                "period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting insight stats: {e}")
            return {}
    
    async def cleanup_expired(self) -> int:
        """Clean up expired insights."""
        try:
            now = datetime.utcnow()
            expired_models = await InsightModel.find(
                InsightModel.expires_at < now
            ).to_list()
            
            count = len(expired_models)
            for model in expired_models:
                await model.delete()
            
            self.logger.info(f"Cleaned up {count} expired insights")
            return count
        except Exception as e:
            self.logger.error(f"Error cleaning up expired insights: {e}")
            return 0