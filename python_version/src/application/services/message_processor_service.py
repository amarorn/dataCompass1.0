"""
Message Processor Service
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from ...domain.entities.interaction import InteractionType, SentimentType


class MessagePattern:
    """Pattern for message classification"""
    def __init__(
        self, 
        pattern: str, 
        type: InteractionType, 
        category: Optional[str] = None
    ):
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.type = type
        self.category = category


class MessageProcessorService:
    """Service for processing WhatsApp messages"""
    
    def __init__(self):
        self._initialize_patterns()
        self._initialize_sentiment_words()
    
    def _initialize_patterns(self):
        """Initialize message patterns for classification"""
        # Purchase patterns
        self.purchase_patterns = [
            MessagePattern(
                r'comprei|compra|gastei|paguei|adquiri',
                InteractionType.PURCHASE,
                'geral'
            ),
            MessagePattern(
                r'supermercado|mercado|alimentação|comida',
                InteractionType.PURCHASE,
                'alimentação'
            ),
            MessagePattern(
                r'roupa|vestuário|calça|camisa|vestido|sapato',
                InteractionType.PURCHASE,
                'vestuário'
            ),
            MessagePattern(
                r'eletrônico|celular|computador|tv|notebook',
                InteractionType.PURCHASE,
                'eletrônicos'
            ),
            MessagePattern(
                r'casa|móvel|decoração|cozinha',
                InteractionType.PURCHASE,
                'casa'
            )
        ]
        
        # Feedback patterns
        self.feedback_patterns = [
            MessagePattern(
                r'gostei|adorei|excelente|ótimo|perfeito|recomendo',
                InteractionType.FEEDBACK,
                'positivo'
            ),
            MessagePattern(
                r'não gostei|ruim|péssimo|horrível|decepcionado',
                InteractionType.FEEDBACK,
                'negativo'
            ),
            MessagePattern(
                r'feedback|opinião|avaliação|comentário',
                InteractionType.FEEDBACK,
                'geral'
            )
        ]
        
        # Complaint patterns
        self.complaint_patterns = [
            MessagePattern(
                r'reclamação|problema|defeito|quebrado|não funciona',
                InteractionType.COMPLAINT,
                'produto'
            ),
            MessagePattern(
                r'atendimento|demora|espera|mal atendido',
                InteractionType.COMPLAINT,
                'atendimento'
            ),
            MessagePattern(
                r'entrega|atraso|não chegou|perdido',
                InteractionType.COMPLAINT,
                'entrega'
            )
        ]
        
        # Question patterns
        self.question_patterns = [
            MessagePattern(
                r'\?|como|quando|onde|qual|quanto|por que',
                InteractionType.QUESTION,
                'informação'
            ),
            MessagePattern(
                r'preço|valor|custo|quanto custa',
                InteractionType.QUESTION,
                'preço'
            ),
            MessagePattern(
                r'disponível|estoque|tem|possui',
                InteractionType.QUESTION,
                'disponibilidade'
            )
        ]
        
        # Profile patterns
        self.profile_patterns = [
            MessagePattern(
                r'meu nome é|me chamo|sou|trabalho como|profissão',
                InteractionType.PROFILE_UPDATE,
                'identificação'
            ),
            MessagePattern(
                r'moro em|cidade|endereço|localização',
                InteractionType.PROFILE_UPDATE,
                'localização'
            ),
            MessagePattern(
                r'idade|anos|nasci|aniversário',
                InteractionType.PROFILE_UPDATE,
                'idade'
            )
        ]
    
    def _initialize_sentiment_words(self):
        """Initialize sentiment word lists"""
        self.positive_words = [
            'bom', 'ótimo', 'excelente', 'perfeito', 'adorei', 'gostei', 
            'maravilhoso', 'fantástico', 'incrível', 'satisfeito', 'feliz', 
            'recomendo', 'aprovado', 'legal', 'bacana', 'top', 'show'
        ]
        
        self.negative_words = [
            'ruim', 'péssimo', 'horrível', 'terrível', 'odeio', 'detesto', 
            'problema', 'defeito', 'quebrado', 'insatisfeito', 'decepcionado', 
            'frustrado', 'raiva', 'chato', 'irritado', 'pior', 'nunca'
        ]
    
    def process_message(self, message_text: str) -> Dict[str, Any]:
        """Process a WhatsApp message and extract information"""
        if not message_text:
            return self._empty_result()
        
        # Detect interaction type
        interaction_type, category = self._detect_interaction_type(message_text)
        
        # Analyze sentiment
        sentiment, confidence = self._analyze_sentiment(message_text)
        
        # Extract data
        extracted_data = self._extract_data(message_text, interaction_type)
        
        # Determine if response is needed
        should_respond = self._should_generate_response(interaction_type, sentiment)
        
        # Generate suggested response
        suggested_response = None
        if should_respond:
            suggested_response = self._generate_response(
                interaction_type, 
                sentiment, 
                extracted_data
            )
        
        return {
            "interaction_type": interaction_type.value,
            "category": category,
            "sentiment": sentiment.value,
            "confidence_score": confidence,
            "extracted_data": extracted_data,
            "should_respond": should_respond,
            "suggested_response": suggested_response,
            "keywords": self._extract_keywords(message_text),
            "topics": self._extract_topics(message_text, interaction_type)
        }
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result for invalid messages"""
        return {
            "interaction_type": InteractionType.GENERAL.value,
            "category": None,
            "sentiment": SentimentType.NEUTRAL.value,
            "confidence_score": 0.0,
            "extracted_data": {},
            "should_respond": False,
            "suggested_response": None,
            "keywords": [],
            "topics": []
        }
    
    def _detect_interaction_type(self, text: str) -> Tuple[InteractionType, Optional[str]]:
        """Detect the type of interaction and category"""
        # Check all pattern groups
        all_patterns = [
            self.purchase_patterns,
            self.complaint_patterns,
            self.feedback_patterns,
            self.profile_patterns,
            self.question_patterns
        ]
        
        for pattern_group in all_patterns:
            for pattern in pattern_group:
                if pattern.pattern.search(text):
                    return pattern.type, pattern.category
        
        return InteractionType.GENERAL, None
    
    def _analyze_sentiment(self, text: str) -> Tuple[SentimentType, float]:
        """Analyze sentiment of the text"""
        text_lower = text.lower()
        
        # Count positive and negative words
        positive_score = sum(1 for word in self.positive_words if word in text_lower)
        negative_score = sum(1 for word in self.negative_words if word in text_lower)
        
        total_score = positive_score + negative_score
        
        if total_score == 0:
            return SentimentType.NEUTRAL, 0.5
        
        # Calculate confidence
        confidence = min(1.0, total_score / 10)
        
        # Determine sentiment
        if positive_score > negative_score * 1.5:
            return SentimentType.POSITIVE, confidence
        elif negative_score > positive_score * 1.5:
            return SentimentType.NEGATIVE, confidence
        elif positive_score > 0 and negative_score > 0:
            return SentimentType.MIXED, confidence
        else:
            return SentimentType.NEUTRAL, confidence
    
    def _extract_data(self, text: str, interaction_type: InteractionType) -> Dict[str, Any]:
        """Extract relevant data from the message"""
        extracted = {}
        
        # Extract monetary values
        value = self._extract_value(text)
        if value:
            extracted["value"] = value
        
        # Extract dates
        date = self._extract_date(text)
        if date:
            extracted["date"] = date
        
        # Extract product mentions
        if interaction_type == InteractionType.PURCHASE:
            products = self._extract_products(text)
            if products:
                extracted["products"] = products
        
        # Extract contact information
        email = self._extract_email(text)
        if email:
            extracted["email"] = email
        
        phone = self._extract_phone(text)
        if phone:
            extracted["phone"] = phone
        
        # Extract location
        location = self._extract_location(text)
        if location:
            extracted["location"] = location
        
        return extracted
    
    def _extract_value(self, text: str) -> Optional[float]:
        """Extract monetary value from text"""
        # Pattern for Brazilian currency
        patterns = [
            r'R\$\s*([0-9]+(?:[.,][0-9]+)?)',
            r'([0-9]+(?:[.,][0-9]+)?)\s*reais',
            r'([0-9]+(?:[.,][0-9]+)?)\s*real'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(',', '.')
                try:
                    return float(value_str)
                except ValueError:
                    continue
        
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text"""
        # Simple date patterns
        patterns = [
            r'(\d{1,2}/\d{1,2}/\d{2,4})',
            r'(\d{1,2}-\d{1,2}-\d{2,4})',
            r'(hoje|ontem|amanhã)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_products(self, text: str) -> List[str]:
        """Extract product mentions from text"""
        # Common product keywords
        product_keywords = [
            'celular', 'notebook', 'computador', 'tv', 'geladeira',
            'fogão', 'microondas', 'sofá', 'cama', 'mesa', 'cadeira',
            'roupa', 'calça', 'camisa', 'vestido', 'sapato', 'tênis'
        ]
        
        found_products = []
        text_lower = text.lower()
        
        for product in product_keywords:
            if product in text_lower:
                found_products.append(product)
        
        return found_products
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email from text"""
        pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        match = re.search(pattern, text)
        return match.group(0) if match else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        pattern = r'(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?(?:9\s?)?\d{4}[-\s]?\d{4}'
        match = re.search(pattern, text)
        return match.group(0) if match else None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location mentions from text"""
        # Brazilian cities and states
        locations = [
            'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Brasília',
            'Salvador', 'Fortaleza', 'Curitiba', 'Recife', 'Porto Alegre'
        ]
        
        text_lower = text.lower()
        for location in locations:
            if location.lower() in text_lower:
                return location
        
        return None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Remove common words
        stopwords = [
            'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'da', 'do',
            'para', 'com', 'em', 'no', 'na', 'por', 'que', 'e'
        ]
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if len(w) > 3 and w not in stopwords]
        
        # Return unique keywords
        return list(set(keywords))[:10]
    
    def _extract_topics(self, text: str, interaction_type: InteractionType) -> List[str]:
        """Extract topics from text based on interaction type"""
        topics = []
        
        # Add interaction type as topic
        topics.append(interaction_type.value.lower())
        
        # Add category-specific topics
        text_lower = text.lower()
        
        topic_keywords = {
            'vendas': ['compra', 'venda', 'produto', 'serviço'],
            'suporte': ['ajuda', 'problema', 'dúvida', 'erro'],
            'financeiro': ['pagamento', 'boleto', 'cartão', 'pix'],
            'entrega': ['envio', 'frete', 'prazo', 'rastreio']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics[:5]
    
    def _should_generate_response(
        self, 
        interaction_type: InteractionType, 
        sentiment: SentimentType
    ) -> bool:
        """Determine if a response should be generated"""
        # Always respond to questions and complaints
        if interaction_type in [InteractionType.QUESTION, InteractionType.COMPLAINT]:
            return True
        
        # Respond to negative feedback
        if interaction_type == InteractionType.FEEDBACK and sentiment == SentimentType.NEGATIVE:
            return True
        
        # Respond to registration requests
        if interaction_type == InteractionType.REGISTRATION:
            return True
        
        return False
    
    def _generate_response(
        self, 
        interaction_type: InteractionType,
        sentiment: SentimentType,
        extracted_data: Dict[str, Any]
    ) -> str:
        """Generate a suggested response based on the interaction"""
        responses = {
            InteractionType.QUESTION: self._generate_question_response,
            InteractionType.COMPLAINT: self._generate_complaint_response,
            InteractionType.FEEDBACK: self._generate_feedback_response,
            InteractionType.PURCHASE: self._generate_purchase_response,
            InteractionType.REGISTRATION: self._generate_registration_response
        }
        
        generator = responses.get(interaction_type, self._generate_general_response)
        return generator(sentiment, extracted_data)
    
    def _generate_question_response(self, sentiment: SentimentType, data: Dict) -> str:
        """Generate response for questions"""
        return (
            "Obrigado por entrar em contato! 📝\n\n"
            "Recebi sua pergunta e vou verificar as informações para você. "
            "Em breve retorno com a resposta.\n\n"
            "Se precisar de algo urgente, pode me avisar!"
        )
    
    def _generate_complaint_response(self, sentiment: SentimentType, data: Dict) -> str:
        """Generate response for complaints"""
        return (
            "Lamento muito pelo inconveniente! 😔\n\n"
            "Sua reclamação foi registrada e será tratada com prioridade. "
            "Nossa equipe entrará em contato em breve para resolver esta situação.\n\n"
            "Protocolo: #" + str(datetime.now().timestamp())[:10]
        )
    
    def _generate_feedback_response(self, sentiment: SentimentType, data: Dict) -> str:
        """Generate response for feedback"""
        if sentiment == SentimentType.POSITIVE:
            return (
                "Muito obrigado pelo seu feedback positivo! 😊\n\n"
                "Ficamos felizes em saber que teve uma boa experiência. "
                "Sua opinião é muito importante para nós!"
            )
        else:
            return (
                "Agradecemos seu feedback! 📝\n\n"
                "Sua opinião é fundamental para melhorarmos nossos serviços. "
                "Vamos analisar seus comentários com atenção."
            )
    
    def _generate_purchase_response(self, sentiment: SentimentType, data: Dict) -> str:
        """Generate response for purchases"""
        return (
            "Obrigado pela sua compra! 🛍️\n\n"
            "Sua transação foi registrada com sucesso. "
            "Caso precise de alguma assistência, estou à disposição!"
        )
    
    def _generate_registration_response(self, sentiment: SentimentType, data: Dict) -> str:
        """Generate response for registration"""
        return (
            "Bem-vindo! 🎉\n\n"
            "Para completar seu cadastro, preciso de algumas informações:\n"
            "1️⃣ Nome completo\n"
            "2️⃣ Email\n"
            "3️⃣ Cidade\n\n"
            "Pode enviar essas informações quando quiser!"
        )
    
    def _generate_general_response(self, sentiment: SentimentType, data: Dict) -> str:
        """Generate general response"""
        return (
            "Obrigado pela mensagem! 💬\n\n"
            "Recebi sua mensagem e em breve retornarei. "
            "Se tiver alguma dúvida específica, fique à vontade para perguntar!"
        )