"""
Client Analysis Service
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import statistics

from ..entities.client import Client, ClientSegment, ChurnRisk
from ..entities.interaction import Interaction, SentimentType


class ClientAnalysisService:
    """Service for analyzing client behavior and generating insights"""
    
    def calculate_engagement_score(
        self, 
        client: Client, 
        interactions: List[Interaction]
    ) -> float:
        """Calculate client engagement score based on interactions"""
        if not interactions:
            return 0.0
        
        score = 0.0
        
        # Frequency score (30%)
        days_since_first = (datetime.utcnow() - client.created_at).days or 1
        interaction_frequency = len(interactions) / days_since_first
        frequency_score = min(30, interaction_frequency * 10)
        
        # Recency score (25%)
        if client.last_interaction:
            days_since_last = (datetime.utcnow() - client.last_interaction).days
            if days_since_last <= 7:
                recency_score = 25
            elif days_since_last <= 30:
                recency_score = 15
            elif days_since_last <= 90:
                recency_score = 5
            else:
                recency_score = 0
        else:
            recency_score = 0
        
        # Sentiment score (20%)
        positive_interactions = sum(
            1 for i in interactions 
            if i.sentiment == SentimentType.POSITIVE
        )
        sentiment_ratio = positive_interactions / len(interactions)
        sentiment_score = sentiment_ratio * 20
        
        # Response rate score (15%)
        responded_interactions = sum(1 for i in interactions if i.response_sent)
        response_rate = responded_interactions / len(interactions)
        response_score = response_rate * 15
        
        # Profile completeness (10%)
        profile_score = 10 if client.has_complete_profile() else 0
        
        score = frequency_score + recency_score + sentiment_score + response_score + profile_score
        
        return min(100, round(score, 2))
    
    def determine_segment(
        self, 
        client: Client, 
        interactions: List[Interaction]
    ) -> ClientSegment:
        """Determine client segment based on behavior"""
        # VIP criteria
        if (client.total_purchase_value > 10000 or 
            client.total_interactions > 100 or
            client.engagement_score > 80):
            return ClientSegment.VIP
        
        # Frequent criteria
        if client.last_interaction:
            days_since_last = (datetime.utcnow() - client.last_interaction).days
            if days_since_last <= 30 and client.total_interactions > 10:
                return ClientSegment.FREQUENT
        
        # Inactive criteria
        if client.last_interaction:
            days_since_last = (datetime.utcnow() - client.last_interaction).days
            if days_since_last > 90:
                return ClientSegment.INACTIVE
        
        # Default to occasional
        return ClientSegment.OCCASIONAL
    
    def calculate_churn_risk(
        self, 
        client: Client, 
        interactions: List[Interaction]
    ) -> ChurnRisk:
        """Calculate churn risk based on client behavior"""
        risk_score = 0
        
        # Recency factor
        if client.last_interaction:
            days_since_last = (datetime.utcnow() - client.last_interaction).days
            if days_since_last > 90:
                risk_score += 40
            elif days_since_last > 60:
                risk_score += 30
            elif days_since_last > 30:
                risk_score += 20
        else:
            risk_score += 50
        
        # Engagement factor
        if client.engagement_score < 20:
            risk_score += 30
        elif client.engagement_score < 40:
            risk_score += 20
        elif client.engagement_score < 60:
            risk_score += 10
        
        # Sentiment factor
        if interactions:
            negative_count = sum(
                1 for i in interactions 
                if i.sentiment == SentimentType.NEGATIVE
            )
            negative_ratio = negative_count / len(interactions)
            if negative_ratio > 0.5:
                risk_score += 30
            elif negative_ratio > 0.3:
                risk_score += 20
            elif negative_ratio > 0.1:
                risk_score += 10
        
        # Determine risk level
        if risk_score >= 70:
            return ChurnRisk.CRITICAL
        elif risk_score >= 50:
            return ChurnRisk.HIGH
        elif risk_score >= 30:
            return ChurnRisk.MEDIUM
        else:
            return ChurnRisk.LOW
    
    def generate_insights(
        self, 
        client: Client, 
        interactions: List[Interaction]
    ) -> Dict[str, Any]:
        """Generate personalized insights for a client"""
        insights = {
            "client_id": client.id,
            "generated_at": datetime.utcnow().isoformat(),
            "key_metrics": {},
            "recommendations": [],
            "opportunities": [],
            "risks": []
        }
        
        # Key metrics
        insights["key_metrics"] = {
            "lifetime_value": client.calculate_lifetime_value(),
            "engagement_score": client.engagement_score,
            "total_interactions": client.total_interactions,
            "total_purchase_value": client.total_purchase_value,
            "segment": client.segment.value,
            "churn_risk": client.churn_risk.value
        }
        
        # Generate recommendations based on segment
        if client.segment == ClientSegment.VIP:
            insights["recommendations"].append(
                "Provide premium support and exclusive offers"
            )
            insights["recommendations"].append(
                "Assign dedicated account manager"
            )
        elif client.segment == ClientSegment.INACTIVE:
            insights["recommendations"].append(
                "Send re-engagement campaign"
            )
            insights["recommendations"].append(
                "Offer special comeback discount"
            )
        
        # Identify opportunities
        if client.engagement_score > 70 and client.segment != ClientSegment.VIP:
            insights["opportunities"].append(
                "High engagement - consider upgrading to VIP segment"
            )
        
        if not client.has_complete_profile():
            insights["opportunities"].append(
                "Encourage profile completion for better personalization"
            )
        
        # Identify risks
        if client.churn_risk in [ChurnRisk.HIGH, ChurnRisk.CRITICAL]:
            insights["risks"].append(
                f"High churn risk detected ({client.churn_risk.value})"
            )
            insights["recommendations"].append(
                "Immediate intervention required - personal outreach recommended"
            )
        
        # Sentiment analysis
        if interactions:
            negative_count = sum(
                1 for i in interactions 
                if i.sentiment == SentimentType.NEGATIVE
            )
            if negative_count > len(interactions) * 0.3:
                insights["risks"].append(
                    "High negative sentiment detected in recent interactions"
                )
                insights["recommendations"].append(
                    "Review recent complaints and address concerns"
                )
        
        return insights
    
    def calculate_cohort_metrics(
        self, 
        clients: List[Client]
    ) -> Dict[str, Any]:
        """Calculate metrics for a cohort of clients"""
        if not clients:
            return {}
        
        total_clients = len(clients)
        
        # Segment distribution
        segment_dist = {}
        for segment in ClientSegment:
            count = sum(1 for c in clients if c.segment == segment)
            segment_dist[segment.value] = {
                "count": count,
                "percentage": round((count / total_clients) * 100, 2)
            }
        
        # Churn risk distribution
        risk_dist = {}
        for risk in ChurnRisk:
            count = sum(1 for c in clients if c.churn_risk == risk)
            risk_dist[risk.value] = {
                "count": count,
                "percentage": round((count / total_clients) * 100, 2)
            }
        
        # Average metrics
        engagement_scores = [c.engagement_score for c in clients]
        purchase_values = [c.total_purchase_value for c in clients]
        
        return {
            "total_clients": total_clients,
            "segment_distribution": segment_dist,
            "churn_risk_distribution": risk_dist,
            "average_engagement_score": round(statistics.mean(engagement_scores), 2),
            "median_engagement_score": round(statistics.median(engagement_scores), 2),
            "total_purchase_value": sum(purchase_values),
            "average_purchase_value": round(statistics.mean(purchase_values), 2),
            "vip_count": sum(1 for c in clients if c.is_vip()),
            "high_risk_count": sum(1 for c in clients if c.is_high_risk()),
            "complete_profiles": sum(1 for c in clients if c.has_complete_profile())
        }
    
    def predict_next_interaction(
        self, 
        client: Client, 
        interactions: List[Interaction]
    ) -> Optional[Dict[str, Any]]:
        """Predict when the next interaction might occur"""
        if len(interactions) < 2:
            return None
        
        # Calculate average time between interactions
        sorted_interactions = sorted(interactions, key=lambda x: x.timestamp)
        time_deltas = []
        
        for i in range(1, len(sorted_interactions)):
            delta = sorted_interactions[i].timestamp - sorted_interactions[i-1].timestamp
            time_deltas.append(delta.total_seconds())
        
        if not time_deltas:
            return None
        
        avg_seconds = statistics.mean(time_deltas)
        std_seconds = statistics.stdev(time_deltas) if len(time_deltas) > 1 else 0
        
        # Predict next interaction
        last_interaction = sorted_interactions[-1].timestamp
        predicted_next = last_interaction + timedelta(seconds=avg_seconds)
        
        return {
            "predicted_date": predicted_next.isoformat(),
            "confidence": "high" if std_seconds < avg_seconds * 0.3 else "medium",
            "average_days_between": round(avg_seconds / 86400, 1),
            "last_interaction": last_interaction.isoformat()
        }
