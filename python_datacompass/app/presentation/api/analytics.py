"""
Analytics API routes.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.core.logging import get_logger
from app.domain.entities.client import Client, ClientSegment, ChurnRisk
from app.domain.entities.interaction import Interaction, InteractionType, SentimentType
from app.domain.entities.insight import Insight, InsightType, InsightPriority
from app.domain.repositories.client_repository import IClientRepository
from app.domain.repositories.interaction_repository import IInteractionRepository
from app.domain.repositories.insight_repository import IInsightRepository
from app.domain.services.client_analysis_service import ClientAnalysisService

logger = get_logger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


# Dependency injection
async def get_client_repository() -> IClientRepository:
    """Get client repository dependency."""
    pass


async def get_interaction_repository() -> IInteractionRepository:
    """Get interaction repository dependency."""
    pass


async def get_insight_repository() -> IInsightRepository:
    """Get insight repository dependency."""
    pass


# Response models
class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_clients: int
    total_interactions: int
    total_insights: int
    clients_by_segment: dict
    interactions_by_type: dict
    interactions_by_sentiment: dict
    recent_activity: dict


class ClientAnalytics(BaseModel):
    """Client analytics data."""
    client: Client
    engagement_metrics: dict
    recent_interactions: List[Interaction]
    insights: List[Insight]


class InteractionStats(BaseModel):
    """Interaction statistics."""
    total_interactions: int
    by_type: dict
    by_sentiment: dict
    by_period: dict
    trends: dict


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    client_repo: IClientRepository = Depends(get_client_repository),
    interaction_repo: IInteractionRepository = Depends(get_interaction_repository),
    insight_repo: IInsightRepository = Depends(get_insight_repository)
):
    """Get dashboard statistics."""
    try:
        # Get basic counts
        total_clients = await client_repo.count()
        total_interactions = await interaction_repo.count()
        total_insights = await insight_repo.count()
        
        # Get clients by segment
        clients_by_segment = {}
        for segment in ClientSegment:
            clients = await client_repo.get_by_segment(segment)
            clients_by_segment[segment.value] = len(clients)
        
        # Get interactions by type
        interactions_by_type = {}
        for interaction_type in InteractionType:
            count = await interaction_repo.count_by_type(interaction_type)
            interactions_by_type[interaction_type.value] = count
        
        # Get interactions by sentiment
        interactions_by_sentiment = {}
        for sentiment in SentimentType:
            interactions = await interaction_repo.get_by_sentiment(sentiment)
            interactions_by_sentiment[sentiment.value] = len(interactions)
        
        # Get recent activity (last 7 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        recent_interactions = await interaction_repo.get_all(
            start_date=start_date,
            end_date=end_date
        )
        
        recent_insights = await insight_repo.get_recent_insights(days=7)
        
        recent_activity = {
            "interactions_last_7_days": len(recent_interactions),
            "insights_last_7_days": len(recent_insights),
            "avg_interactions_per_day": len(recent_interactions) / 7
        }
        
        return DashboardStats(
            total_clients=total_clients,
            total_interactions=total_interactions,
            total_insights=total_insights,
            clients_by_segment=clients_by_segment,
            interactions_by_type=interactions_by_type,
            interactions_by_sentiment=interactions_by_sentiment,
            recent_activity=recent_activity
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard statistics"
        )


@router.get("/clients", response_model=List[Client])
async def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    segment: Optional[ClientSegment] = None,
    churn_risk: Optional[ChurnRisk] = None,
    client_repo: IClientRepository = Depends(get_client_repository)
):
    """Get clients with optional filtering."""
    try:
        clients = await client_repo.get_all(
            skip=skip,
            limit=limit,
            segment=segment,
            churn_risk=churn_risk
        )
        
        return clients
        
    except Exception as e:
        logger.error(f"Error getting clients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get clients"
        )


@router.get("/clients/{client_id}", response_model=ClientAnalytics)
async def get_client_analytics(
    client_id: str,
    client_repo: IClientRepository = Depends(get_client_repository),
    interaction_repo: IInteractionRepository = Depends(get_interaction_repository),
    insight_repo: IInsightRepository = Depends(get_insight_repository)
):
    """Get detailed analytics for a specific client."""
    try:
        # Get client
        client = await client_repo.get_by_id(client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        # Get client analysis service
        analysis_service = ClientAnalysisService(client_repo, interaction_repo)
        
        # Get engagement metrics
        engagement_metrics = await analysis_service.analyze_client_engagement(client_id)
        
        # Get recent interactions
        recent_interactions = await interaction_repo.get_by_client_id(
            client_id, skip=0, limit=10
        )
        
        # Get insights
        insights = await insight_repo.get_by_client_id(
            client_id, skip=0, limit=10
        )
        
        return ClientAnalytics(
            client=client,
            engagement_metrics=engagement_metrics,
            recent_interactions=recent_interactions,
            insights=insights
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get client analytics"
        )


@router.get("/interactions", response_model=List[Interaction])
async def get_interactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    interaction_type: Optional[InteractionType] = None,
    sentiment: Optional[SentimentType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    interaction_repo: IInteractionRepository = Depends(get_interaction_repository)
):
    """Get interactions with optional filtering."""
    try:
        interactions = await interaction_repo.get_all(
            skip=skip,
            limit=limit,
            interaction_type=interaction_type,
            sentiment=sentiment,
            start_date=start_date,
            end_date=end_date
        )
        
        return interactions
        
    except Exception as e:
        logger.error(f"Error getting interactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get interactions"
        )


@router.get("/interactions/stats", response_model=InteractionStats)
async def get_interaction_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    interaction_repo: IInteractionRepository = Depends(get_interaction_repository)
):
    """Get interaction statistics."""
    try:
        stats = await interaction_repo.get_interaction_stats(start_date, end_date)
        
        # Get additional stats
        total_interactions = stats.get("total_interactions", 0)
        by_type = stats.get("by_type", {})
        by_sentiment = stats.get("by_sentiment", {})
        
        # Calculate trends (simplified)
        trends = {
            "growth_rate": 0.0,  # Would calculate based on historical data
            "peak_hours": ["14:00", "19:00"],  # Would analyze from data
            "most_active_day": "Tuesday"  # Would analyze from data
        }
        
        return InteractionStats(
            total_interactions=total_interactions,
            by_type=by_type,
            by_sentiment=by_sentiment,
            by_period={},  # Would implement period-based analysis
            trends=trends
        )
        
    except Exception as e:
        logger.error(f"Error getting interaction stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get interaction statistics"
        )


@router.get("/insights", response_model=List[Insight])
async def get_insights(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    insight_type: Optional[InsightType] = None,
    priority: Optional[InsightPriority] = None,
    client_id: Optional[str] = None,
    insight_repo: IInsightRepository = Depends(get_insight_repository)
):
    """Get insights with optional filtering."""
    try:
        if client_id:
            insights = await insight_repo.get_by_client_id(
                client_id, skip=skip, limit=limit
            )
        else:
            insights = await insight_repo.get_all(
                skip=skip,
                limit=limit,
                insight_type=insight_type,
                priority=priority
            )
        
        return insights
        
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get insights"
        )


@router.get("/insights/high-priority", response_model=List[Insight])
async def get_high_priority_insights(
    insight_repo: IInsightRepository = Depends(get_insight_repository)
):
    """Get high priority insights."""
    try:
        insights = await insight_repo.get_high_priority_insights()
        return insights
        
    except Exception as e:
        logger.error(f"Error getting high priority insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get high priority insights"
        )


@router.get("/insights/stats")
async def get_insight_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    insight_repo: IInsightRepository = Depends(get_insight_repository)
):
    """Get insight statistics."""
    try:
        stats = await insight_repo.get_insight_stats(start_date, end_date)
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting insight stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get insight statistics"
        )


@router.get("/clients/segments/{segment}", response_model=List[Client])
async def get_clients_by_segment(
    segment: ClientSegment,
    client_repo: IClientRepository = Depends(get_client_repository)
):
    """Get clients by segment."""
    try:
        clients = await client_repo.get_by_segment(segment)
        return clients
        
    except Exception as e:
        logger.error(f"Error getting clients by segment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get clients by segment"
        )


@router.get("/clients/high-risk", response_model=List[Client])
async def get_high_risk_clients(
    client_repo: IClientRepository = Depends(get_client_repository)
):
    """Get clients with high churn risk."""
    try:
        clients = await client_repo.get_high_risk_clients()
        return clients
        
    except Exception as e:
        logger.error(f"Error getting high risk clients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get high risk clients"
        )


@router.get("/clients/vip", response_model=List[Client])
async def get_vip_clients(
    client_repo: IClientRepository = Depends(get_client_repository)
):
    """Get VIP clients."""
    try:
        clients = await client_repo.get_vip_clients()
        return clients
        
    except Exception as e:
        logger.error(f"Error getting VIP clients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get VIP clients"
        )