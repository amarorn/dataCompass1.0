"""
WhatsApp Client using PyWA
"""

import logging
from typing import Optional, Dict, Any, List, BinaryIO
from pathlib import Path

from pywa import WhatsApp
from pywa.types import Message, CallbackButton, CallbackSelection
from pywa.types.flows import FlowStatus

from ...config import settings

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """WhatsApp client wrapper using PyWA"""
    
    def __init__(self):
        """Initialize WhatsApp client with PyWA"""
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the PyWA WhatsApp client"""
        try:
            self.client = WhatsApp(
                phone_id=settings.whatsapp_phone_number_id,
                token=settings.whatsapp_token,
                server=None,  # Use default Meta server
                webhook_endpoint=settings.pywa_webhook_endpoint,
                verify_token=settings.whatsapp_webhook_verify_token,
                app_id=settings.whatsapp_app_id,
                app_secret=settings.whatsapp_app_secret,
                business_account_id=settings.whatsapp_business_id,
                callback_url=settings.pywa_callback_url,
                verify_webhook_signature=True,
                business_private_key=None,
                business_private_key_password=None,
                continue_flow_request_on_error=False,
                validate_updates=True,
                api_version="21.0"
            )
            logger.info("WhatsApp client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WhatsApp client: {e}")
            raise
    
    def is_configured(self) -> bool:
        """Check if WhatsApp client is properly configured"""
        return (
            self.client is not None and
            bool(settings.whatsapp_token) and
            bool(settings.whatsapp_phone_number_id)
        )
    
    async def send_text_message(
        self, 
        to: str, 
        text: str,
        preview_url: bool = True
    ) -> Optional[str]:
        """Send a text message via WhatsApp"""
        try:
            if not self.is_configured():
                logger.error("WhatsApp client not configured")
                return None
            
            # Clean phone number
            to_number = self._clean_phone_number(to)
            
            # Send message using PyWA
            response = self.client.send_message(
                to=to_number,
                text=text,
                preview_url=preview_url
            )
            
            logger.info(f"Message sent successfully to {to_number}")
            return response
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return None
    
    async def send_template_message(
        self,
        to: str,
        template: str,
        components: Optional[List[Dict]] = None,
        language: str = "pt_BR"
    ) -> Optional[str]:
        """Send a template message via WhatsApp"""
        try:
            if not self.is_configured():
                logger.error("WhatsApp client not configured")
                return None
            
            to_number = self._clean_phone_number(to)
            
            # Send template using PyWA
            response = self.client.send_template(
                to=to_number,
                template=template,
                components=components or [],
                lang=language
            )
            
            logger.info(f"Template message sent successfully to {to_number}")
            return response
            
        except Exception as e:
            logger.error(f"Error sending template message: {e}")
            return None
    
    async def send_image(
        self,
        to: str,
        image: str | BinaryIO,
        caption: Optional[str] = None
    ) -> Optional[str]:
        """Send an image via WhatsApp"""
        try:
            if not self.is_configured():
                return None
            
            to_number = self._clean_phone_number(to)
            
            response = self.client.send_image(
                to=to_number,
                image=image,
                caption=caption
            )
            
            logger.info(f"Image sent successfully to {to_number}")
            return response
            
        except Exception as e:
            logger.error(f"Error sending image: {e}")
            return None
    
    async def send_document(
        self,
        to: str,
        document: str | BinaryIO,
        filename: Optional[str] = None,
        caption: Optional[str] = None
    ) -> Optional[str]:
        """Send a document via WhatsApp"""
        try:
            if not self.is_configured():
                return None
            
            to_number = self._clean_phone_number(to)
            
            response = self.client.send_document(
                to=to_number,
                document=document,
                filename=filename,
                caption=caption
            )
            
            logger.info(f"Document sent successfully to {to_number}")
            return response
            
        except Exception as e:
            logger.error(f"Error sending document: {e}")
            return None
    
    async def send_location(
        self,
        to: str,
        latitude: float,
        longitude: float,
        name: Optional[str] = None,
        address: Optional[str] = None
    ) -> Optional[str]:
        """Send a location via WhatsApp"""
        try:
            if not self.is_configured():
                return None
            
            to_number = self._clean_phone_number(to)
            
            response = self.client.send_location(
                to=to_number,
                lat=latitude,
                long=longitude,
                name=name,
                address=address
            )
            
            logger.info(f"Location sent successfully to {to_number}")
            return response
            
        except Exception as e:
            logger.error(f"Error sending location: {e}")
            return None
    
    async def send_buttons(
        self,
        to: str,
        text: str,
        buttons: List[Dict[str, str]],
        header: Optional[str] = None,
        footer: Optional[str] = None
    ) -> Optional[str]:
        """Send interactive buttons message"""
        try:
            if not self.is_configured():
                return None
            
            to_number = self._clean_phone_number(to)
            
            # Create button objects
            button_objects = [
                CallbackButton(
                    title=btn.get("title", ""),
                    callback_data=btn.get("id", "")
                )
                for btn in buttons[:3]  # Max 3 buttons
            ]
            
            response = self.client.send_message(
                to=to_number,
                text=text,
                buttons=button_objects,
                header=header,
                footer=footer
            )
            
            logger.info(f"Button message sent successfully to {to_number}")
            return response
            
        except Exception as e:
            logger.error(f"Error sending button message: {e}")
            return None
    
    async def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read"""
        try:
            if not self.is_configured():
                return False
            
            self.client.mark_message_as_read(message_id)
            return True
            
        except Exception as e:
            logger.error(f"Error marking message as read: {e}")
            return False
    
    async def react_to_message(
        self,
        message_id: str,
        emoji: str
    ) -> bool:
        """React to a message with an emoji"""
        try:
            if not self.is_configured():
                return False
            
            self.client.send_reaction(
                to="",  # Not needed for reactions
                message_id=message_id,
                emoji=emoji
            )
            return True
            
        except Exception as e:
            logger.error(f"Error reacting to message: {e}")
            return False
    
    async def download_media(
        self,
        media_id: str,
        mime_type: Optional[str] = None,
        save_path: Optional[Path] = None
    ) -> Optional[bytes]:
        """Download media from WhatsApp"""
        try:
            if not self.is_configured():
                return None
            
            media_bytes = self.client.download_media(
                media_id=media_id,
                path=str(save_path) if save_path else None,
                mime_type=mime_type
            )
            
            logger.info(f"Media downloaded successfully: {media_id}")
            return media_bytes
            
        except Exception as e:
            logger.error(f"Error downloading media: {e}")
            return None
    
    async def upload_media(
        self,
        media: BinaryIO | bytes | str,
        mime_type: str
    ) -> Optional[str]:
        """Upload media to WhatsApp and get media ID"""
        try:
            if not self.is_configured():
                return None
            
            media_id = self.client.upload_media(
                media=media,
                mime_type=mime_type
            )
            
            logger.info(f"Media uploaded successfully: {media_id}")
            return media_id
            
        except Exception as e:
            logger.error(f"Error uploading media: {e}")
            return None
    
    async def get_business_profile(self) -> Optional[Dict[str, Any]]:
        """Get business profile information"""
        try:
            if not self.is_configured():
                return None
            
            profile = self.client.get_business_profile()
            return profile
            
        except Exception as e:
            logger.error(f"Error getting business profile: {e}")
            return None
    
    async def update_business_profile(
        self,
        about: Optional[str] = None,
        address: Optional[str] = None,
        description: Optional[str] = None,
        email: Optional[str] = None,
        profile_picture: Optional[str] = None,
        websites: Optional[List[str]] = None
    ) -> bool:
        """Update business profile information"""
        try:
            if not self.is_configured():
                return False
            
            success = self.client.update_business_profile(
                about=about,
                address=address,
                description=description,
                email=email,
                profile_picture_handle=profile_picture,
                websites=websites
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating business profile: {e}")
            return False
    
    def _clean_phone_number(self, number: str) -> str:
        """Clean and format phone number"""
        # Remove all non-numeric characters
        clean = ''.join(filter(str.isdigit, number))
        
        # Add country code if not present (assuming Brazil)
        if not clean.startswith('55'):
            clean = '55' + clean
        
        return clean
    
    def get_webhook_handler(self):
        """Get PyWA webhook handler for FastAPI"""
        return self.client
    
    def validate_signature(self, payload: str, signature: str) -> bool:
        """Validate webhook signature"""
        try:
            return self.client.validate_signature(payload, signature)
        except Exception as e:
            logger.error(f"Error validating signature: {e}")
            return False