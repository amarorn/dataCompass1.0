"""
Client analysis service - business logic for client analytics.
"""

from typing import Any, Dict, List, Optional

from app.core.logging import LoggerMixin
from app.domain.entities.client import Client, ClientSegment, ChurnRisk
from app.domain.entities.interaction import Interaction, InteractionType, SentimentType
from app.domain.repositories.client_repository import IClientRepository
from app.domain.repositories.interaction_repository import IInteractionRepository


class ClientAnalysisService(LoggerMixin):
    """Service for client analysis and segmentation."""
    
    def __init__(
        self,
        client_repository: IClientRepository,
        interaction_repository: IInteractionRepository
    ):
        self.client_repository = client_repository
        self.interaction_repository = interaction_repository
    
    async def analyze_client_engagement(
        self, 
        client_id: str, 
        days: int = 30
    ) -> Dict[str, float]:
        """Analyze client engagement metrics."""
        client = await self.client_repository.get_by_id(client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")
        
        # Get recent interactions
        interactions = await self.interaction_repository.get_recent_interactions(
            client_id, days
        )
        
        if not interactions:
            return {
                "engagement_score": 0.0,
                "interaction_frequency": 0.0,
                "sentiment_score": 0.0,
                "purchase_ratio": 0.0
            }
        
        # Calculate engagement score based on various factors
        total_interactions = len(interactions)
        purchase_interactions = [i for i in interactions if i.is_purchase()]
        positive_interactions = [i for i in interactions if i.is_positive()]
        
        # Interaction frequency (interactions per day)
        interaction_frequency = total_interactions / days
        
        # Sentiment score
        sentiment_scores = {
            SentimentType.POSITIVE: 1.0,
            SentimentType.NEUTRAL: 0.5,
            SentimentType.NEGATIVE: 0.0
        }
        sentiment_score = sum(
            sentiment_scores.get(i.sentiment, 0.5) for i in interactions
        ) / total_interactions
        
        # Purchase ratio
        purchase_ratio = len(purchase_interactions) / total_interactions
        
        # Overall engagement score (weighted combination)
        engagement_score = (
            min(interaction_frequency * 10, 40) +  # Up to 40 points for frequency
            sentiment_score * 30 +  # Up to 30 points for sentiment
            purchase_ratio * 30  # Up to 30 points for purchases
        )
        
        return {
            "engagement_score": min(engagement_score, 100.0),
            "interaction_frequency": interaction_frequency,
            "sentiment_score": sentiment_score,
            "purchase_ratio": purchase_ratio
        }
    
    async def determine_client_segment(self, client_id: str) -> ClientSegment:
        """Determine client segment based on behavior."""
        client = await self.client_repository.get_by_id(client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")
        
        # Get engagement metrics
        engagement_metrics = await self.analyze_client_engagement(client_id)
        engagement_score = engagement_metrics["engagement_score"]
        purchase_ratio = engagement_metrics["purchase_ratio"]
        
        # Get total interactions
        total_interactions = await self.interaction_repository.count_by_client(client_id)
        
        # Determine segment based on metrics
        if engagement_score >= 80 and purchase_ratio >= 0.3:
            return ClientSegment.VIP
        elif engagement_score >= 60 and total_interactions >= 10:
            return ClientSegment.FREQUENT
        elif engagement_score >= 30 or total_interactions >= 3:
            return ClientSegment.OCCASIONAL
        else:
            return ClientSegment.INACTIVE
    
    async def calculate_churn_risk(self, client_id: str) -> ChurnRisk:
        """Calculate churn risk for a client."""
        client = await self.client_repository.get_by_id(client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")
        
        # Get recent interactions (last 30 days)
        recent_interactions = await self.interaction_repository.get_recent_interactions(
            client_id, days=30
        )
        
        # Get interactions from 30-60 days ago
        older_interactions = await self.interaction_repository.get_recent_interactions(
            client_id, days=60
        )
        older_interactions = [
            i for i in older_interactions 
            if i not in recent_interactions
        ]
        
        # Calculate risk factors
        recent_activity = len(recent_interactions)
        older_activity = len(older_interactions)
        
        # Activity decline
        if older_activity > 0:
            activity_decline = (older_activity - recent_activity) / older_activity
        else:
            activity_decline = 0
        
        # Negative sentiment ratio
        negative_interactions = [
            i for i in recent_interactions 
            if i.is_negative()
        ]
        negative_ratio = (
            len(negative_interactions) / len(recent_interactions)
            if recent_interactions else 0
        )
        
        # Complaints
        complaints = [
            i for i in recent_interactions 
            if i.is_complaint()
        ]
        complaint_count = len(complaints)
        
        # Calculate risk score
        risk_score = 0
        
        # Activity decline factor
        if activity_decline > 0.5:
            risk_score += 30
        elif activity_decline > 0.2:
            risk_score += 15
        
        # Negative sentiment factor
        if negative_ratio > 0.5:
            risk_score += 25
        elif negative_ratio > 0.2:
            risk_score += 10
        
        # Complaint factor
        risk_score += min(complaint_count * 10, 30)
        
        # Determine risk level
        if risk_score >= 70:
            return ChurnRisk.CRITICAL
        elif risk_score >= 50:
            return ChurnRisk.HIGH
        elif risk_score >= 25:
            return ChurnRisk.MEDIUM
        else:
            return ChurnRisk.LOW
    
    async def update_client_analytics(self, client_id: str) -> Client:
        """Update client analytics (segment and churn risk)."""
        client = await self.client_repository.get_by_id(client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")
        
        # Update engagement score
        engagement_metrics = await self.analyze_client_engagement(client_id)
        client.update_engagement_score(engagement_metrics["engagement_score"])
        
        # Update segment
        new_segment = await self.determine_client_segment(client_id)
        client.update_segment(new_segment)
        
        # Update churn risk
        new_churn_risk = await self.calculate_churn_risk(client_id)
        client.update_churn_risk(new_churn_risk)
        
        # Save updated client
        return await self.client_repository.update(client)
    
    async def get_client_insights(self, client_id: str) -> List[Dict[str, Any]]:
        """Get insights for a specific client."""
        client = await self.client_repository.get_by_id(client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")
        
        insights = []
        
        # Get engagement metrics
        engagement_metrics = await self.analyze_client_engagement(client_id)
        
        # Engagement insight
        if engagement_metrics["engagement_score"] >= 80:
            insights.append({
                "type": "positive",
                "title": "High Engagement",
                "description": f"Client has excellent engagement score of {engagement_metrics['engagement_score']:.1f}",
                "recommendation": "Consider offering premium services or loyalty rewards"
            })
        elif engagement_metrics["engagement_score"] <= 30:
            insights.append({
                "type": "warning",
                "title": "Low Engagement",
                "description": f"Client has low engagement score of {engagement_metrics['engagement_score']:.1f}",
                "recommendation": "Implement re-engagement campaign"
            })
        
        # Churn risk insight
        if client.is_high_risk():
            insights.append({
                "type": "critical",
                "title": "High Churn Risk",
                "description": f"Client is at {client.churn_risk.value} churn risk",
                "recommendation": "Immediate intervention required - contact client personally"
            })
        
        # Purchase behavior insight
        if engagement_metrics["purchase_ratio"] >= 0.5:
            insights.append({
                "type": "positive",
                "title": "Frequent Purchaser",
                "description": f"Client makes purchases in {engagement_metrics['purchase_ratio']*100:.1f}% of interactions",
                "recommendation": "Offer exclusive deals and early access to new products"
            })
        
        return insights