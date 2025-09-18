"""
WhatsApp Service - High-level service for WhatsApp operations
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

from pywa.types import Message, CallbackButton
from pywa.errors import WhatsAppError

from .whatsapp_client import WhatsAppClient
from ...domain.entities.interaction import Interaction, InteractionType, MessageType
from ...domain.entities.client import Client
from ...application.services.message_processor_service import MessageProcessorService

logger = logging.getLogger(__name__)


class WhatsAppService:
    """High-level WhatsApp service for business logic"""
    
    def __init__(self):
        self.client = WhatsAppClient()
        self.message_processor = MessageProcessorService()
    
    async def process_incoming_message(self, message: Message) -> Dict[str, Any]:
        """Process an incoming WhatsApp message"""
        try:
            # Extract message data
            message_data = self._extract_message_data(message)
            
            # Process message content
            if message.type == "text":
                processed = self.message_processor.process_message(message.text)
            else:
                processed = {
                    "interaction_type": InteractionType.GENERAL.value,
                    "sentiment": "NEUTRAL",
                    "should_respond": True,
                    "suggested_response": f"Recebi seu {message.type}. Vou processar e retorno em breve!"
                }
            
            # Create interaction entity
            interaction = Interaction(
                message_id=message.id,
                client_id="",  # Will be filled by the service layer
                whatsapp_number=message.from_user.wa_id,
                timestamp=datetime.fromtimestamp(message.timestamp),
                message_type=MessageType(message.type),
                message_content=message.text if message.type == "text" else None,
                interaction_type=InteractionType(processed["interaction_type"]),
                sentiment=processed["sentiment"],
                confidence_score=processed.get("confidence_score", 0),
                extracted_value=processed.get("extracted_data", {}).get("value"),
                extracted_category=processed.get("category"),
                extracted_entities=processed.get("extracted_data", {}),
                keywords=processed.get("keywords", []),
                topics=processed.get("topics", [])
            )
            
            # Handle media messages
            if message.type in ["image", "document", "audio", "video"]:
                media_info = self._extract_media_info(message)
                interaction.media_id = media_info.get("id")
                interaction.media_mime_type = media_info.get("mime_type")
                interaction.media_sha256 = media_info.get("sha256")
                interaction.media_filename = media_info.get("filename")
            
            # Handle location messages
            elif message.type == "location":
                interaction.location_latitude = message.location.latitude
                interaction.location_longitude = message.location.longitude
                interaction.location_name = message.location.name
                interaction.location_address = message.location.address
            
            # Mark message as read
            await self.client.mark_as_read(message.id)
            
            # Send auto-response if needed
            if processed.get("should_respond") and processed.get("suggested_response"):
                await self.send_auto_response(
                    message.from_user.wa_id,
                    processed["suggested_response"],
                    message.id
                )
                interaction.set_response(
                    processed["suggested_response"],
                    "text"
                )
            
            return {
                "success": True,
                "interaction": interaction.to_dict(),
                "processed": processed
            }
            
        except Exception as e:
            logger.error(f"Error processing incoming message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_auto_response(
        self,
        to: str,
        message: str,
        reply_to: Optional[str] = None
    ) -> bool:
        """Send an automatic response"""
        try:
            result = await self.client.send_text_message(to, message)
            return result is not None
        except Exception as e:
            logger.error(f"Error sending auto response: {e}")
            return False
    
    async def send_welcome_message(self, client: Client) -> bool:
        """Send welcome message to new client"""
        try:
            message = (
                f"Olá {client.name or 'Cliente'}! 👋\n\n"
                "Bem-vindo ao DataCompass! 🎯\n\n"
                "Sou seu assistente virtual e estou aqui para ajudar você com:\n"
                "📊 Análises personalizadas\n"
                "🛍️ Informações sobre produtos\n"
                "💬 Suporte e atendimento\n"
                "📈 Relatórios e insights\n\n"
                "Como posso ajudar você hoje?"
            )
            
            buttons = [
                {"id": "catalog", "title": "📦 Ver Catálogo"},
                {"id": "support", "title": "💬 Suporte"},
                {"id": "profile", "title": "👤 Meu Perfil"}
            ]
            
            result = await self.client.send_buttons(
                client.whatsapp_number,
                message,
                buttons,
                header="Bem-vindo!",
                footer="DataCompass 2.0"
            )
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")
            return False
    
    async def send_analytics_report(
        self,
        client: Client,
        report_data: Dict[str, Any]
    ) -> bool:
        """Send analytics report to client"""
        try:
            # Format report message
            message = self._format_analytics_report(report_data)
            
            # Send main report
            await self.client.send_text_message(
                client.whatsapp_number,
                message
            )
            
            # Send charts if available
            if "charts" in report_data:
                for chart in report_data["charts"]:
                    await self.client.send_image(
                        client.whatsapp_number,
                        chart["path"],
                        caption=chart.get("caption", "")
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending analytics report: {e}")
            return False
    
    async def send_churn_alert(
        self,
        client: Client,
        risk_data: Dict[str, Any]
    ) -> bool:
        """Send churn risk alert for a client"""
        try:
            message = (
                f"⚠️ *Alerta de Risco de Churn*\n\n"
                f"Cliente: {client.name or client.whatsapp_number}\n"
                f"Nível de Risco: {client.churn_risk.value}\n"
                f"Score de Engajamento: {client.engagement_score:.1f}/100\n\n"
                f"*Ações Recomendadas:*\n"
            )
            
            for idx, action in enumerate(risk_data.get("recommended_actions", []), 1):
                message += f"{idx}. {action}\n"
            
            message += "\n💡 *Dica:* Entre em contato pessoalmente para entender as necessidades do cliente."
            
            # Send to admin/manager
            admin_number = "5511999999999"  # Configure admin number
            result = await self.client.send_text_message(admin_number, message)
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Error sending churn alert: {e}")
            return False
    
    async def send_csv_processing_status(
        self,
        to: str,
        filename: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send CSV processing status update"""
        try:
            if status == "started":
                message = f"📊 Iniciando processamento do arquivo: *{filename}*\n\nAguarde alguns instantes..."
            elif status == "completed":
                rows = details.get("rows_processed", 0) if details else 0
                message = (
                    f"✅ Arquivo processado com sucesso!\n\n"
                    f"📁 Arquivo: *{filename}*\n"
                    f"📊 Registros processados: {rows}\n\n"
                    f"Use os comandos abaixo para explorar os dados:\n"
                    f"• Digite 'análise' para ver estatísticas\n"
                    f"• Digite 'gráficos' para visualizações\n"
                    f"• Digite 'insights' para recomendações"
                )
            elif status == "error":
                error_msg = details.get("error", "Erro desconhecido") if details else "Erro desconhecido"
                message = (
                    f"❌ Erro ao processar arquivo\n\n"
                    f"📁 Arquivo: *{filename}*\n"
                    f"⚠️ Erro: {error_msg}\n\n"
                    f"Por favor, verifique o formato do arquivo e tente novamente."
                )
            else:
                message = f"📊 Status do processamento: {status}"
            
            result = await self.client.send_text_message(to, message)
            return result is not None
            
        except Exception as e:
            logger.error(f"Error sending CSV status: {e}")
            return False
    
    async def handle_button_response(
        self,
        callback: CallbackButton,
        from_number: str
    ) -> Dict[str, Any]:
        """Handle interactive button responses"""
        try:
            button_id = callback.callback_data
            
            responses = {
                "catalog": "📦 Aqui está nosso catálogo de produtos...",
                "support": "💬 Como posso ajudar você hoje?",
                "profile": "👤 Seus dados de perfil..."
            }
            
            response_text = responses.get(
                button_id,
                "Obrigado pela sua resposta!"
            )
            
            await self.client.send_text_message(from_number, response_text)
            
            return {
                "success": True,
                "button_id": button_id,
                "response_sent": True
            }
            
        except Exception as e:
            logger.error(f"Error handling button response: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_message_data(self, message: Message) -> Dict[str, Any]:
        """Extract relevant data from WhatsApp message"""
        return {
            "id": message.id,
            "from": message.from_user.wa_id,
            "name": message.from_user.name,
            "timestamp": message.timestamp,
            "type": message.type,
            "text": getattr(message, "text", None),
            "reply_to": getattr(message, "reply_to_message_id", None)
        }
    
    def _extract_media_info(self, message: Message) -> Dict[str, Any]:
        """Extract media information from message"""
        media_info = {}
        
        if hasattr(message, message.type):
            media = getattr(message, message.type)
            media_info = {
                "id": getattr(media, "id", None),
                "mime_type": getattr(media, "mime_type", None),
                "sha256": getattr(media, "sha256", None),
                "filename": getattr(media, "filename", None)
            }
        
        return media_info
    
    def _format_analytics_report(self, report_data: Dict[str, Any]) -> str:
        """Format analytics report for WhatsApp message"""
        message = "📊 *Relatório de Analytics*\n\n"
        
        # Add summary
        if "summary" in report_data:
            message += "*Resumo:*\n"
            for key, value in report_data["summary"].items():
                message += f"• {key}: {value}\n"
            message += "\n"
        
        # Add insights
        if "insights" in report_data:
            message += "*Principais Insights:*\n"
            for idx, insight in enumerate(report_data["insights"][:5], 1):
                message += f"{idx}. {insight}\n"
            message += "\n"
        
        # Add recommendations
        if "recommendations" in report_data:
            message += "*Recomendações:*\n"
            for idx, rec in enumerate(report_data["recommendations"][:3], 1):
                message += f"{idx}. {rec}\n"
        
        message += "\n_Gerado por DataCompass 2.0_"
        
        return message
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get WhatsApp configuration status"""
        return {
            "configured": self.client.is_configured(),
            "token_present": bool(self.client.client.token if self.client.client else False),
            "phone_id_present": bool(self.client.client.phone_id if self.client.client else False),
            "webhook_configured": bool(self.client.client.verify_token if self.client.client else False)
        }