"""
Message processor service - processes WhatsApp messages and extracts insights.
"""

import re
from typing import Dict, List, Optional

from app.core.logging import LoggerMixin
from app.domain.entities.interaction import Interaction, InteractionType, SentimentType


class ProcessedMessage:
    """Processed message result."""
    
    def __init__(
        self,
        original_message: Dict[str, any],
        interaction_type: InteractionType,
        sentiment: SentimentType,
        extracted_data: Dict[str, any],
        should_respond: bool,
        suggested_response: Optional[str] = None
    ):
        self.original_message = original_message
        self.interaction_type = interaction_type
        self.sentiment = sentiment
        self.extracted_data = extracted_data
        self.should_respond = should_respond
        self.suggested_response = suggested_response


class MessagePattern:
    """Message pattern for classification."""
    
    def __init__(
        self,
        pattern: str,
        interaction_type: InteractionType,
        category: Optional[str] = None,
        value_extractor: Optional[callable] = None
    ):
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.interaction_type = interaction_type
        self.category = category
        self.value_extractor = value_extractor


class MessageProcessorService(LoggerMixin):
    """Service for processing WhatsApp messages."""
    
    def __init__(self):
        self.purchase_patterns = [
            MessagePattern(
                r"comprei|compra|gastei|paguei|adquiri",
                InteractionType.PURCHASE,
                "geral",
                self._extract_value
            ),
            MessagePattern(
                r"supermercado|mercado|alimentação|comida",
                InteractionType.PURCHASE,
                "alimentação",
                self._extract_value
            ),
            MessagePattern(
                r"roupa|vestuário|calça|camisa|vestido|sapato",
                InteractionType.PURCHASE,
                "vestuário",
                self._extract_value
            ),
            MessagePattern(
                r"eletrônico|celular|computador|tv|notebook",
                InteractionType.PURCHASE,
                "eletrônicos",
                self._extract_value
            ),
            MessagePattern(
                r"casa|móvel|decoração|cozinha",
                InteractionType.PURCHASE,
                "casa",
                self._extract_value
            )
        ]
        
        self.feedback_patterns = [
            MessagePattern(
                r"gostei|adorei|excelente|ótimo|perfeito|recomendo",
                InteractionType.FEEDBACK,
                "positivo"
            ),
            MessagePattern(
                r"não gostei|ruim|péssimo|horrível|decepcionado",
                InteractionType.FEEDBACK,
                "negativo"
            ),
            MessagePattern(
                r"feedback|opinião|avaliação|comentário",
                InteractionType.FEEDBACK,
                "geral"
            )
        ]
        
        self.complaint_patterns = [
            MessagePattern(
                r"reclamação|problema|defeito|quebrado|não funciona",
                InteractionType.COMPLAINT,
                "produto"
            ),
            MessagePattern(
                r"atendimento|demora|espera|mal atendido",
                InteractionType.COMPLAINT,
                "atendimento"
            ),
            MessagePattern(
                r"entrega|atraso|não chegou|perdido",
                InteractionType.COMPLAINT,
                "entrega"
            )
        ]
        
        self.question_patterns = [
            MessagePattern(
                r"\?|como|quando|onde|qual|quanto|por que",
                InteractionType.QUESTION,
                "informação"
            ),
            MessagePattern(
                r"preço|valor|custo|quanto custa",
                InteractionType.QUESTION,
                "preço"
            ),
            MessagePattern(
                r"disponível|estoque|tem|possui",
                InteractionType.QUESTION,
                "disponibilidade"
            )
        ]
        
        self.profile_patterns = [
            MessagePattern(
                r"meu nome é|me chamo|sou|trabalho como|profissão",
                InteractionType.PROFILE_UPDATE,
                "identificação"
            ),
            MessagePattern(
                r"moro em|cidade|endereço|localização",
                InteractionType.PROFILE_UPDATE,
                "localização"
            ),
            MessagePattern(
                r"idade|anos|nasci|aniversário",
                InteractionType.PROFILE_UPDATE,
                "idade"
            )
        ]
    
    def process_message(self, message: Dict[str, any]) -> ProcessedMessage:
        """Process a WhatsApp message."""
        if message.get("type") != "text" or not message.get("text", {}).get("body"):
            return ProcessedMessage(
                original_message=message,
                interaction_type=InteractionType.GENERAL,
                sentiment=SentimentType.NEUTRAL,
                extracted_data={},
                should_respond=False
            )
        
        text = message["text"]["body"]
        interaction_type = self._detect_interaction_type(text)
        sentiment = self._analyze_sentiment(text)
        extracted_data = self._extract_data(text, interaction_type)
        should_respond = self._should_generate_response(interaction_type, sentiment)
        suggested_response = (
            self._generate_response(interaction_type, sentiment, extracted_data)
            if should_respond else None
        )
        
        return ProcessedMessage(
            original_message=message,
            interaction_type=interaction_type,
            sentiment=sentiment,
            extracted_data=extracted_data,
            should_respond=should_respond,
            suggested_response=suggested_response
        )
    
    def _detect_interaction_type(self, text: str) -> InteractionType:
        """Detect interaction type based on text patterns."""
        all_patterns = (
            self.purchase_patterns +
            self.complaint_patterns +
            self.feedback_patterns +
            self.profile_patterns +
            self.question_patterns
        )
        
        for pattern in all_patterns:
            if pattern.pattern.search(text):
                return pattern.interaction_type
        
        return InteractionType.GENERAL
    
    def _analyze_sentiment(self, text: str) -> SentimentType:
        """Analyze sentiment of the text."""
        positive_words = [
            "bom", "ótimo", "excelente", "perfeito", "adorei", "gostei", "maravilhoso",
            "fantástico", "incrível", "satisfeito", "feliz", "recomendo", "aprovado"
        ]
        
        negative_words = [
            "ruim", "péssimo", "horrível", "terrível", "odeio", "detesto", "problema",
            "defeito", "quebrado", "insatisfeito", "decepcionado", "frustrado", "raiva"
        ]
        
        lower_text = text.lower()
        
        positive_score = sum(1 for word in positive_words if word in lower_text)
        negative_score = sum(1 for word in negative_words if word in lower_text)
        
        if positive_score > negative_score:
            return SentimentType.POSITIVE
        elif negative_score > positive_score:
            return SentimentType.NEGATIVE
        else:
            return SentimentType.NEUTRAL
    
    def _extract_data(self, text: str, interaction_type: InteractionType) -> Dict[str, any]:
        """Extract structured data from text."""
        data = {}
        
        # Extract monetary value
        value = self._extract_value(text)
        if value:
            data["value"] = value
        
        # Extract category based on type
        category = self._extract_category(text, interaction_type)
        if category:
            data["category"] = category
        
        # Extract entities
        entities = self._extract_entities(text)
        if entities:
            data["entities"] = entities
        
        return data
    
    def _extract_value(self, text: str) -> Optional[float]:
        """Extract monetary value from text."""
        patterns = [
            r"R\$\s*(\d+(?:[.,]\d{2})?)",
            r"(\d+(?:[.,]\d{2})?)\s*reais?",
            r"(\d+(?:[.,]\d{2})?)\s*(?:R\$|reais?)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for match in matches:
                    value = float(match.replace(",", "."))
                    if not value != value:  # Check for NaN
                        return value
        
        return None
    
    def _extract_category(self, text: str, interaction_type: InteractionType) -> Optional[str]:
        """Extract category based on interaction type."""
        all_patterns = (
            self.purchase_patterns +
            self.feedback_patterns +
            self.complaint_patterns +
            self.question_patterns +
            self.profile_patterns
        )
        
        for pattern in all_patterns:
            if pattern.interaction_type == interaction_type and pattern.pattern.search(text):
                return pattern.category
        
        return None
    
    def _extract_entities(self, text: str) -> Dict[str, any]:
        """Extract named entities from text."""
        entities = {}
        
        # Extract names
        name_pattern = r"(?:me chamo|meu nome é|sou)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
        name_match = re.search(name_pattern, text, re.IGNORECASE)
        if name_match:
            entities["name"] = name_match.group(1)
        
        # Extract cities
        city_pattern = r"(?:moro em|cidade|de)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
        city_match = re.search(city_pattern, text, re.IGNORECASE)
        if city_match:
            entities["city"] = city_match.group(1)
        
        # Extract age
        age_pattern = r"(\d{1,2})\s*anos?"
        age_match = re.search(age_pattern, text, re.IGNORECASE)
        if age_match:
            entities["age"] = int(age_match.group(1))
        
        # Extract profession
        profession_pattern = r"(?:trabalho como|sou|profissão)\s+([a-z]+(?:\s+[a-z]+)*)"
        profession_match = re.search(profession_pattern, text, re.IGNORECASE)
        if profession_match:
            entities["profession"] = profession_match.group(1)
        
        return entities
    
    def _should_generate_response(
        self, 
        interaction_type: InteractionType, 
        sentiment: SentimentType
    ) -> bool:
        """Determine if should generate an automatic response."""
        # Always respond to complaints
        if interaction_type == InteractionType.COMPLAINT:
            return True
        
        # Respond to questions
        if interaction_type == InteractionType.QUESTION:
            return True
        
        # Respond to negative feedback
        if interaction_type == InteractionType.FEEDBACK and sentiment == SentimentType.NEGATIVE:
            return True
        
        # Confirm purchases
        if interaction_type == InteractionType.PURCHASE:
            return True
        
        # Confirm profile updates
        if interaction_type == InteractionType.PROFILE_UPDATE:
            return True
        
        return False
    
    def _generate_response(
        self,
        interaction_type: InteractionType,
        sentiment: SentimentType,
        extracted_data: Dict[str, any]
    ) -> str:
        """Generate automatic response based on context."""
        if interaction_type == InteractionType.PURCHASE:
            if extracted_data.get("value"):
                return f"✅ Compra registrada! Valor: R$ {extracted_data['value']:.2f}. Obrigado pela informação!"
            return "✅ Compra registrada! Obrigado por compartilhar essa informação conosco."
        
        elif interaction_type == InteractionType.COMPLAINT:
            return "😔 Lamentamos o inconveniente. Nossa equipe irá analisar sua reclamação e entrar em contato em breve."
        
        elif interaction_type == InteractionType.FEEDBACK:
            if sentiment == SentimentType.POSITIVE:
                return "😊 Que bom saber que você gostou! Seu feedback é muito importante para nós."
            elif sentiment == SentimentType.NEGATIVE:
                return "😔 Agradecemos seu feedback. Vamos trabalhar para melhorar sua experiência."
            return "📝 Obrigado pelo seu feedback! Sua opinião é muito valiosa para nós."
        
        elif interaction_type == InteractionType.QUESTION:
            return "❓ Recebemos sua pergunta! Nossa equipe irá responder em breve com as informações solicitadas."
        
        elif interaction_type == InteractionType.PROFILE_UPDATE:
            return "📝 Informações atualizadas com sucesso! Obrigado por manter seu perfil atualizado."
        
        else:
            return "👋 Olá! Recebemos sua mensagem e nossa equipe irá analisá-la em breve."
    
    def process_messages(self, messages: List[Dict[str, any]]) -> List[ProcessedMessage]:
        """Process multiple messages."""
        return [self.process_message(message) for message in messages]