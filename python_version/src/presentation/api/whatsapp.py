"""
WhatsApp API Routes
"""

import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Request, Response, HTTPException, Query, Body, BackgroundTasks
from fastapi.responses import PlainTextResponse
from pywa import WhatsApp
from pywa.types import Message, CallbackButton

from ...infrastructure.whatsapp import WhatsAppService, WhatsAppClient
from ...config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
whatsapp_service = WhatsAppService()
whatsapp_client = WhatsAppClient()

# Initialize PyWA webhook handler
wa = whatsapp_client.get_webhook_handler()


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge")
):
    """
    Webhook verification endpoint for WhatsApp
    
    This endpoint is called by WhatsApp to verify the webhook URL
    """
    logger.info(f"Webhook verification request: mode={hub_mode}, token={hub_verify_token}")
    
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_webhook_verify_token:
        logger.info("Webhook verified successfully")
        return PlainTextResponse(content=hub_challenge)
    else:
        logger.warning("Invalid webhook verification token")
        raise HTTPException(status_code=403, detail="Invalid verification token")


@router.post("/webhook")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Webhook endpoint to receive messages from WhatsApp
    
    This endpoint processes incoming WhatsApp messages and events
    """
    try:
        # Get request body
        body = await request.body()
        payload = await request.json()
        
        # Validate signature if configured
        signature = request.headers.get("X-Hub-Signature-256", "")
        if signature and not whatsapp_client.validate_signature(body.decode(), signature):
            logger.warning("Invalid webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        logger.info(f"Received webhook payload: {payload}")
        
        # Process webhook in background
        background_tasks.add_task(process_webhook_payload, payload)
        
        # Return immediate response
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        # Return 200 to avoid WhatsApp retries
        return {"status": "error", "message": str(e)}


async def process_webhook_payload(payload: Dict[str, Any]):
    """Process webhook payload in background"""
    try:
        # Check if it's a WhatsApp business account notification
        if payload.get("object") != "whatsapp_business_account":
            logger.warning(f"Unknown webhook object: {payload.get('object')}")
            return
        
        # Process each entry
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                await process_webhook_change(change)
                
    except Exception as e:
        logger.error(f"Error processing webhook payload: {e}")


async def process_webhook_change(change: Dict[str, Any]):
    """Process individual webhook change"""
    try:
        field = change.get("field")
        value = change.get("value", {})
        
        if field == "messages":
            # Process incoming messages
            for message_data in value.get("messages", []):
                await process_incoming_message(message_data)
        
        elif field == "statuses":
            # Process message status updates
            for status in value.get("statuses", []):
                await process_message_status(status)
                
    except Exception as e:
        logger.error(f"Error processing webhook change: {e}")


async def process_incoming_message(message_data: Dict[str, Any]):
    """Process incoming WhatsApp message"""
    try:
        # Convert to PyWA Message object
        message = Message.from_dict(message_data)
        
        # Process with service
        result = await whatsapp_service.process_incoming_message(message)
        
        logger.info(f"Message processed: {result}")
        
    except Exception as e:
        logger.error(f"Error processing incoming message: {e}")


async def process_message_status(status: Dict[str, Any]):
    """Process message status update"""
    try:
        message_id = status.get("id")
        status_type = status.get("status")
        recipient_id = status.get("recipient_id")
        timestamp = status.get("timestamp")
        
        logger.info(f"Message status update: {message_id} - {status_type}")
        
        # TODO: Update message status in database
        
    except Exception as e:
        logger.error(f"Error processing message status: {e}")


@router.post("/send")
async def send_message(
    to: str = Body(..., description="WhatsApp number to send message to"),
    message: str = Body(..., description="Message content"),
    preview_url: bool = Body(default=True, description="Enable URL preview")
):
    """
    Send a text message via WhatsApp
    """
    try:
        result = await whatsapp_client.send_text_message(to, message, preview_url)
        
        if result:
            return {
                "success": True,
                "message": "Message sent successfully",
                "message_id": result
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send message")
            
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-template")
async def send_template(
    to: str = Body(..., description="WhatsApp number"),
    template_name: str = Body(..., description="Template name"),
    language: str = Body(default="pt_BR", description="Template language"),
    components: Optional[List[Dict]] = Body(default=None, description="Template components")
):
    """
    Send a template message via WhatsApp
    """
    try:
        result = await whatsapp_client.send_template_message(
            to, template_name, components, language
        )
        
        if result:
            return {
                "success": True,
                "message": "Template sent successfully",
                "message_id": result
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send template")
            
    except Exception as e:
        logger.error(f"Error sending template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-image")
async def send_image(
    to: str = Body(..., description="WhatsApp number"),
    image_url: str = Body(..., description="Image URL or path"),
    caption: Optional[str] = Body(default=None, description="Image caption")
):
    """
    Send an image via WhatsApp
    """
    try:
        result = await whatsapp_client.send_image(to, image_url, caption)
        
        if result:
            return {
                "success": True,
                "message": "Image sent successfully",
                "message_id": result
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send image")
            
    except Exception as e:
        logger.error(f"Error sending image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-document")
async def send_document(
    to: str = Body(..., description="WhatsApp number"),
    document_url: str = Body(..., description="Document URL or path"),
    filename: Optional[str] = Body(default=None, description="Document filename"),
    caption: Optional[str] = Body(default=None, description="Document caption")
):
    """
    Send a document via WhatsApp
    """
    try:
        result = await whatsapp_client.send_document(
            to, document_url, filename, caption
        )
        
        if result:
            return {
                "success": True,
                "message": "Document sent successfully",
                "message_id": result
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send document")
            
    except Exception as e:
        logger.error(f"Error sending document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-location")
async def send_location(
    to: str = Body(..., description="WhatsApp number"),
    latitude: float = Body(..., description="Latitude"),
    longitude: float = Body(..., description="Longitude"),
    name: Optional[str] = Body(default=None, description="Location name"),
    address: Optional[str] = Body(default=None, description="Location address")
):
    """
    Send a location via WhatsApp
    """
    try:
        result = await whatsapp_client.send_location(
            to, latitude, longitude, name, address
        )
        
        if result:
            return {
                "success": True,
                "message": "Location sent successfully",
                "message_id": result
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send location")
            
    except Exception as e:
        logger.error(f"Error sending location: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-buttons")
async def send_buttons(
    to: str = Body(..., description="WhatsApp number"),
    text: str = Body(..., description="Message text"),
    buttons: List[Dict[str, str]] = Body(..., description="Button list"),
    header: Optional[str] = Body(default=None, description="Message header"),
    footer: Optional[str] = Body(default=None, description="Message footer")
):
    """
    Send interactive buttons message
    """
    try:
        result = await whatsapp_client.send_buttons(
            to, text, buttons, header, footer
        )
        
        if result:
            return {
                "success": True,
                "message": "Buttons sent successfully",
                "message_id": result
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send buttons")
            
    except Exception as e:
        logger.error(f"Error sending buttons: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-as-read")
async def mark_as_read(
    message_id: str = Body(..., description="Message ID to mark as read")
):
    """
    Mark a message as read
    """
    try:
        success = await whatsapp_client.mark_as_read(message_id)
        
        return {
            "success": success,
            "message": "Message marked as read" if success else "Failed to mark as read"
        }
        
    except Exception as e:
        logger.error(f"Error marking message as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/react")
async def react_to_message(
    message_id: str = Body(..., description="Message ID to react to"),
    emoji: str = Body(..., description="Reaction emoji")
):
    """
    React to a message with an emoji
    """
    try:
        success = await whatsapp_client.react_to_message(message_id, emoji)
        
        return {
            "success": success,
            "message": "Reaction sent" if success else "Failed to send reaction"
        }
        
    except Exception as e:
        logger.error(f"Error reacting to message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    """
    Get WhatsApp integration status
    """
    try:
        config_status = whatsapp_service.get_configuration_status()
        
        return {
            "success": True,
            "message": "WhatsApp integration status",
            "status": {
                "configured": config_status["configured"],
                "connection": "active" if config_status["configured"] else "inactive",
                "webhook_configured": config_status["webhook_configured"],
                "endpoints": {
                    "webhook": "/api/whatsapp/webhook",
                    "send": "/api/whatsapp/send",
                    "template": "/api/whatsapp/send-template",
                    "status": "/api/whatsapp/status"
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/business-profile")
async def get_business_profile():
    """
    Get WhatsApp Business profile
    """
    try:
        profile = await whatsapp_client.get_business_profile()
        
        if profile:
            return {
                "success": True,
                "profile": profile
            }
        else:
            raise HTTPException(status_code=404, detail="Profile not found")
            
    except Exception as e:
        logger.error(f"Error getting business profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/business-profile")
async def update_business_profile(
    about: Optional[str] = Body(default=None),
    address: Optional[str] = Body(default=None),
    description: Optional[str] = Body(default=None),
    email: Optional[str] = Body(default=None),
    profile_picture: Optional[str] = Body(default=None),
    websites: Optional[List[str]] = Body(default=None)
):
    """
    Update WhatsApp Business profile
    """
    try:
        success = await whatsapp_client.update_business_profile(
            about=about,
            address=address,
            description=description,
            email=email,
            profile_picture=profile_picture,
            websites=websites
        )
        
        return {
            "success": success,
            "message": "Profile updated" if success else "Failed to update profile"
        }
        
    except Exception as e:
        logger.error(f"Error updating business profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))
