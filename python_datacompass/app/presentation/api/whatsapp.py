"""
WhatsApp API routes.
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.application.services.chart_generator_service import ChartGeneratorService
from app.application.services.exploratory_analysis_service import ExploratoryAnalysisService
from app.application.services.message_processor_service import MessageProcessorService
from app.core.logging import get_logger
from app.core.security import validate_whatsapp_signature
from app.domain.entities.client import Client
from app.domain.entities.interaction import Interaction
from app.domain.repositories.client_repository import IClientRepository
from app.domain.repositories.interaction_repository import IInteractionRepository
from app.domain.services.client_analysis_service import ClientAnalysisService
from app.infrastructure.external.whatsapp_service import WhatsAppService

logger = get_logger(__name__)

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp"])

# Services
whatsapp_service = WhatsAppService()
message_processor = MessageProcessorService()
chart_generator = ChartGeneratorService()
analysis_service = ExploratoryAnalysisService()


# Dependency injection
async def get_client_repository() -> IClientRepository:
    """Get client repository dependency."""
    # This would be injected from the main app
    pass


async def get_interaction_repository() -> IInteractionRepository:
    """Get interaction repository dependency."""
    # This would be injected from the main app
    pass


# Pydantic models for request/response
class WebhookVerificationRequest(BaseModel):
    """Webhook verification request."""
    hub_mode: str
    hub_verify_token: str
    hub_challenge: str


class SendMessageRequest(BaseModel):
    """Send message request."""
    to: str
    message: str
    type: str = "text"


class SendTemplateRequest(BaseModel):
    """Send template request."""
    to: str
    template_name: str
    language_code: str = "pt_BR"
    components: Optional[List[Dict[str, any]]] = None


class TestMessageRequest(BaseModel):
    """Test message processing request."""
    message: str
    from_number: str = "5511999999999"


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str,
    hub_verify_token: str,
    hub_challenge: str
):
    """Verify WhatsApp webhook."""
    logger.info(f"Webhook verification request: mode={hub_mode}")
    
    from app.core.config import settings
    expected_token = settings.whatsapp_webhook_verify_token
    
    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        logger.info("Webhook verified successfully")
        return hub_challenge
    else:
        logger.warning("Webhook verification failed")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Webhook verification failed"
        )


@router.post("/webhook")
async def receive_webhook(
    request: Request,
    client_repo: IClientRepository = Depends(get_client_repository),
    interaction_repo: IInteractionRepository = Depends(get_interaction_repository)
):
    """Receive WhatsApp webhook messages."""
    logger.info("Received WhatsApp webhook")
    
    # Get raw body for signature validation
    body = await request.body()
    signature = request.headers.get("x-hub-signature-256", "")
    
    # Validate signature
    from app.core.config import settings
    if not validate_whatsapp_signature(
        body.decode(), 
        signature, 
        settings.whatsapp_webhook_secret or ""
    ):
        logger.warning("Invalid webhook signature")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    
    try:
        # Parse webhook payload
        webhook_data = await request.json()
        
        # Process messages using PyWA
        from pywa import WhatsApp
        # This would need to be properly integrated with PyWA webhook handling
        
        # For now, simulate message processing
        processed_count = 0
        
        # Process each message
        # This is a simplified version - in reality, you'd use PyWA's webhook handlers
        
        return {
            "success": True,
            "processed": processed_count,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing webhook"
        )


@router.post("/send")
async def send_message(request: SendMessageRequest):
    """Send a text message via WhatsApp."""
    try:
        result = await whatsapp_service.send_text_message(request.to, request.message)
        
        if result.get("success"):
            return {
                "success": True,
                "message": "Message sent successfully",
                "data": {
                    "to": request.to,
                    "message": request.message,
                    "message_id": result.get("message_id"),
                    "simulated": result.get("simulated", False)
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to send message")
            )
            
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )


@router.post("/template")
async def send_template(request: SendTemplateRequest):
    """Send a template message via WhatsApp."""
    try:
        result = await whatsapp_service.send_template_message(
            request.to,
            request.template_name,
            request.language_code,
            request.components
        )
        
        if result.get("success"):
            return {
                "success": True,
                "message": "Template sent successfully",
                "data": {
                    "to": request.to,
                    "template_name": request.template_name,
                    "language_code": request.language_code,
                    "message_id": result.get("message_id"),
                    "simulated": result.get("simulated", False)
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to send template")
            )
            
    except Exception as e:
        logger.error(f"Error sending template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send template"
        )


@router.get("/status")
async def get_status():
    """Get WhatsApp integration status."""
    config_status = whatsapp_service.get_configuration_status()
    
    return {
        "success": True,
        "message": "WhatsApp integration status",
        "data": {
            "configured": whatsapp_service.is_configured(),
            "configuration": config_status,
            "environment": "development"  # Would come from settings
        }
    }


@router.post("/test")
async def test_message_processing(request: TestMessageRequest):
    """Test message processing."""
    try:
        # Simulate WhatsApp message
        simulated_message = {
            "id": f"test-{hash(request.message)}",
            "from": request.from_number,
            "timestamp": "2024-01-01T00:00:00Z",
            "type": "text",
            "text": {
                "body": request.message
            }
        }
        
        # Process message
        processed_message = message_processor.process_message(simulated_message)
        
        return {
            "success": True,
            "message": "Message processed successfully",
            "data": {
                "original_message": simulated_message,
                "processed": {
                    "interaction_type": processed_message.interaction_type.value,
                    "sentiment": processed_message.sentiment.value,
                    "should_respond": processed_message.should_respond,
                    "extracted_data": processed_message.extracted_data,
                    "suggested_response": processed_message.suggested_response
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error testing message processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process test message"
        )


@router.post("/csv/process")
async def process_csv_file(
    message_id: str,
    filename: str,
    from_number: str,
    csv_data: List[Dict[str, any]]
):
    """Process CSV file and generate analysis."""
    try:
        logger.info(f"Processing CSV file: {filename} from {from_number}")
        
        # Perform exploratory analysis
        analysis_result = await analysis_service.perform_exploratory_analysis(
            message_id, filename, from_number, csv_data
        )
        
        # Generate and send charts
        chart_result = await chart_generator.generate_and_send_charts(
            message_id, filename, from_number, csv_data
        )
        
        return {
            "success": True,
            "message": "CSV processed successfully",
            "data": {
                "message_id": message_id,
                "filename": filename,
                "from": from_number,
                "analysis": {
                    "total_records": analysis_result.total_records,
                    "data_structure": {
                        "total_columns": analysis_result.data_structure.total_columns,
                        "feature_distribution": analysis_result.data_structure.feature_distribution
                    },
                    "data_quality": {
                        "overall_score": analysis_result.data_quality.overall_score
                    },
                    "insights": {
                        "key_findings": analysis_result.insights.key_findings,
                        "recommendations": analysis_result.insights.recommendations
                    }
                },
                "charts": {
                    "success": chart_result.success,
                    "charts_generated": len(chart_result.charts),
                    "message": chart_result.message
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process CSV file"
        )