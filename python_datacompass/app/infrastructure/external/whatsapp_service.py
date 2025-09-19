"""
WhatsApp Business API service using PyWA.
"""

import hmac
import hashlib
from typing import Any, Dict, List, Optional

from pywa import WhatsApp
from pywa.types import Message, MessageType, MessageStatus
from pywa.errors import WhatsAppError

from app.core.config import settings
from app.core.logging import LoggerMixin


class WhatsAppService(LoggerMixin):
    """WhatsApp Business API service."""
    
    def __init__(self):
        self.client: Optional[WhatsApp] = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize WhatsApp client."""
        if not settings.whatsapp_token or not settings.whatsapp_phone_number_id:
            self.logger.warning("WhatsApp credentials not configured - using simulation mode")
            return
        
        try:
            self.client = WhatsApp(
                phone_id=settings.whatsapp_phone_number_id,
                token=settings.whatsapp_token,
                verify_token=settings.whatsapp_webhook_verify_token,
            )
            self.logger.info("WhatsApp client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize WhatsApp client: {e}")
            self.client = None
    
    def is_configured(self) -> bool:
        """Check if WhatsApp is properly configured."""
        return (
            self.client is not None and
            settings.whatsapp_token and
            settings.whatsapp_phone_number_id and
            not settings.whatsapp_token.startswith("your-") and
            not settings.whatsapp_phone_number_id.startswith("your-")
        )
    
    def validate_signature(self, payload: str, signature: str) -> bool:
        """Validate WhatsApp webhook signature."""
        if not settings.whatsapp_webhook_secret:
            self.logger.warning("Webhook secret not configured, skipping signature validation")
            return True
        
        try:
            expected_signature = hmac.new(
                settings.whatsapp_webhook_secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            received_signature = signature.replace('sha256=', '')
            
            return hmac.compare_digest(expected_signature, received_signature)
        except Exception as e:
            self.logger.error(f"Error validating webhook signature: {e}")
            return False
    
    async def send_text_message(self, to: str, message: str) -> Dict[str, Any]:
        """Send a text message via WhatsApp."""
        if not self.is_configured():
            self.logger.info(f"[SIMULATION] Sending message to {to}: {message}")
            return {
                "success": True,
                "message_id": f"sim-{hash(message)}",
                "simulated": True
            }
        
        try:
            # Clean phone number
            clean_number = ''.join(filter(str.isdigit, to))
            
            # Send message using PyWA
            result = await self.client.send_message(
                to=clean_number,
                text=message
            )
            
            self.logger.info(f"Message sent successfully to {to}")
            return {
                "success": True,
                "message_id": result.id,
                "whatsapp_response": result
            }
            
        except WhatsAppError as e:
            self.logger.error(f"WhatsApp API error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"Unexpected error sending message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_template_message(
        self, 
        to: str, 
        template_name: str, 
        language_code: str = "pt_BR",
        components: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send a template message via WhatsApp."""
        if not self.is_configured():
            self.logger.info(f"[SIMULATION] Sending template {template_name} to {to}")
            return {
                "success": True,
                "message_id": f"sim-template-{hash(template_name)}",
                "simulated": True
            }
        
        try:
            clean_number = ''.join(filter(str.isdigit, to))
            
            # Send template message using PyWA
            result = await self.client.send_template(
                to=clean_number,
                template=template_name,
                language=language_code,
                components=components or []
            )
            
            self.logger.info(f"Template message sent successfully to {to}")
            return {
                "success": True,
                "message_id": result.id,
                "whatsapp_response": result
            }
            
        except WhatsAppError as e:
            self.logger.error(f"WhatsApp template API error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"Unexpected error sending template: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_document(
        self, 
        to: str, 
        file_path: str, 
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a document via WhatsApp."""
        if not self.is_configured():
            self.logger.info(f"[SIMULATION] Sending document {file_path} to {to}")
            return {
                "success": True,
                "message_id": f"sim-doc-{hash(file_path)}",
                "simulated": True
            }
        
        try:
            clean_number = ''.join(filter(str.isdigit, to))
            
            # Determine if it's an image or document
            import os
            file_extension = os.path.splitext(file_path)[1].lower()
            image_extensions = ['.png', '.jpg', '.jpeg', '.gif']
            
            if file_extension in image_extensions:
                # Send as image
                result = await self.client.send_image(
                    to=clean_number,
                    image=file_path,
                    caption=caption
                )
            else:
                # Send as document
                result = await self.client.send_document(
                    to=clean_number,
                    document=file_path,
                    caption=caption
                )
            
            self.logger.info(f"Document sent successfully to {to}")
            return {
                "success": True,
                "message_id": result.id,
                "whatsapp_response": result
            }
            
        except WhatsAppError as e:
            self.logger.error(f"WhatsApp document API error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"Unexpected error sending document: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read."""
        if not self.is_configured():
            self.logger.info(f"[SIMULATION] Marking message {message_id} as read")
            return True
        
        try:
            await self.client.mark_as_read(message_id)
            return True
        except Exception as e:
            self.logger.error(f"Error marking message as read: {e}")
            return False
    
    async def get_profile(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Get WhatsApp profile information."""
        if not self.is_configured():
            self.logger.info(f"[SIMULATION] Getting profile for {phone_number}")
            return {
                "name": "Simulated User",
                "simulated": True
            }
        
        try:
            clean_number = ''.join(filter(str.isdigit, phone_number))
            profile = await self.client.get_profile(clean_number)
            return profile
        except Exception as e:
            self.logger.error(f"Error getting profile: {e}")
            return None
    
    def get_configuration_status(self) -> Dict[str, bool]:
        """Get WhatsApp configuration status."""
        return {
            "access_token": bool(settings.whatsapp_token),
            "phone_number_id": bool(settings.whatsapp_phone_number_id),
            "webhook_secret": bool(settings.whatsapp_webhook_secret),
            "configured": self.is_configured()
        }
    
    def process_webhook_message(self, message: Message) -> Dict[str, Any]:
        """Process a webhook message from WhatsApp."""
        return {
            "id": message.id,
            "from": message.from_user.wa_id,
            "timestamp": message.timestamp,
            "type": message.type.value if message.type else "unknown",
            "text": message.text.body if message.text else None,
            "document": {
                "id": message.document.id,
                "filename": message.document.filename,
                "mime_type": message.document.mime_type
            } if message.document else None,
            "image": {
                "id": message.image.id,
                "mime_type": message.image.mime_type
            } if message.image else None,
            "audio": {
                "id": message.audio.id,
                "mime_type": message.audio.mime_type
            } if message.audio else None
        }