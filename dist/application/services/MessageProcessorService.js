"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MessageProcessorService = void 0;
const Interaction_1 = require("../../domain/entities/Interaction");
class MessageProcessorService {
    constructor() {
        this.purchasePatterns = [
            {
                pattern: /comprei|compra|gastei|paguei|adquiri/i,
                type: Interaction_1.InteractionType.PURCHASE,
                category: 'geral',
                valueExtractor: this.extractValue
            },
            {
                pattern: /supermercado|mercado|alimentação|comida/i,
                type: Interaction_1.InteractionType.PURCHASE,
                category: 'alimentação',
                valueExtractor: this.extractValue
            },
            {
                pattern: /roupa|vestuário|calça|camisa|vestido|sapato/i,
                type: Interaction_1.InteractionType.PURCHASE,
                category: 'vestuário',
                valueExtractor: this.extractValue
            },
            {
                pattern: /eletrônico|celular|computador|tv|notebook/i,
                type: Interaction_1.InteractionType.PURCHASE,
                category: 'eletrônicos',
                valueExtractor: this.extractValue
            },
            {
                pattern: /casa|móvel|decoração|cozinha/i,
                type: Interaction_1.InteractionType.PURCHASE,
                category: 'casa',
                valueExtractor: this.extractValue
            }
        ];
        this.feedbackPatterns = [
            {
                pattern: /gostei|adorei|excelente|ótimo|perfeito|recomendo/i,
                type: Interaction_1.InteractionType.FEEDBACK,
                category: 'positivo'
            },
            {
                pattern: /não gostei|ruim|péssimo|horrível|decepcionado/i,
                type: Interaction_1.InteractionType.FEEDBACK,
                category: 'negativo'
            },
            {
                pattern: /feedback|opinião|avaliação|comentário/i,
                type: Interaction_1.InteractionType.FEEDBACK,
                category: 'geral'
            }
        ];
        this.complaintPatterns = [
            {
                pattern: /reclamação|problema|defeito|quebrado|não funciona/i,
                type: Interaction_1.InteractionType.COMPLAINT,
                category: 'produto'
            },
            {
                pattern: /atendimento|demora|espera|mal atendido/i,
                type: Interaction_1.InteractionType.COMPLAINT,
                category: 'atendimento'
            },
            {
                pattern: /entrega|atraso|não chegou|perdido/i,
                type: Interaction_1.InteractionType.COMPLAINT,
                category: 'entrega'
            }
        ];
        this.questionPatterns = [
            {
                pattern: /\?|como|quando|onde|qual|quanto|por que/i,
                type: Interaction_1.InteractionType.QUESTION,
                category: 'informação'
            },
            {
                pattern: /preço|valor|custo|quanto custa/i,
                type: Interaction_1.InteractionType.QUESTION,
                category: 'preço'
            },
            {
                pattern: /disponível|estoque|tem|possui/i,
                type: Interaction_1.InteractionType.QUESTION,
                category: 'disponibilidade'
            }
        ];
        this.profilePatterns = [
            {
                pattern: /meu nome é|me chamo|sou|trabalho como|profissão/i,
                type: Interaction_1.InteractionType.PROFILE_UPDATE,
                category: 'identificação'
            },
            {
                pattern: /moro em|cidade|endereço|localização/i,
                type: Interaction_1.InteractionType.PROFILE_UPDATE,
                category: 'localização'
            },
            {
                pattern: /idade|anos|nasci|aniversário/i,
                type: Interaction_1.InteractionType.PROFILE_UPDATE,
                category: 'idade'
            }
        ];
    }
    /**
     * Processa uma mensagem do WhatsApp
     */
    processMessage(message) {
        if (message.type !== 'text' || !message.text?.body) {
            return {
                originalMessage: message,
                interactionType: Interaction_1.InteractionType.GENERAL,
                sentiment: Interaction_1.SentimentType.NEUTRAL,
                extractedData: {},
                shouldRespond: false
            };
        }
        const text = message.text.body;
        const interactionType = this.detectInteractionType(text);
        const sentiment = this.analyzeSentiment(text);
        const extractedData = this.extractData(text, interactionType);
        const shouldRespond = this.shouldGenerateResponse(interactionType, sentiment);
        const suggestedResponse = shouldRespond ? this.generateResponse(interactionType, sentiment, extractedData) : undefined;
        return {
            originalMessage: message,
            interactionType,
            sentiment,
            extractedData,
            shouldRespond,
            suggestedResponse
        };
    }
    /**
     * Detecta o tipo de interação baseado no texto
     */
    detectInteractionType(text) {
        // Verificar padrões em ordem de prioridade
        const allPatterns = [
            ...this.purchasePatterns,
            ...this.complaintPatterns,
            ...this.feedbackPatterns,
            ...this.profilePatterns,
            ...this.questionPatterns
        ];
        for (const pattern of allPatterns) {
            if (pattern.pattern.test(text)) {
                return pattern.type;
            }
        }
        return Interaction_1.InteractionType.GENERAL;
    }
    /**
     * Analisa o sentimento do texto
     */
    analyzeSentiment(text) {
        const positiveWords = [
            'bom', 'ótimo', 'excelente', 'perfeito', 'adorei', 'gostei', 'maravilhoso',
            'fantástico', 'incrível', 'satisfeito', 'feliz', 'recomendo', 'aprovado'
        ];
        const negativeWords = [
            'ruim', 'péssimo', 'horrível', 'terrível', 'odeio', 'detesto', 'problema',
            'defeito', 'quebrado', 'insatisfeito', 'decepcionado', 'frustrado', 'raiva'
        ];
        const lowerText = text.toLowerCase();
        let positiveScore = 0;
        let negativeScore = 0;
        positiveWords.forEach(word => {
            if (lowerText.includes(word))
                positiveScore++;
        });
        negativeWords.forEach(word => {
            if (lowerText.includes(word))
                negativeScore++;
        });
        if (positiveScore > negativeScore)
            return Interaction_1.SentimentType.POSITIVE;
        if (negativeScore > positiveScore)
            return Interaction_1.SentimentType.NEGATIVE;
        return Interaction_1.SentimentType.NEUTRAL;
    }
    /**
     * Extrai dados estruturados do texto
     */
    extractData(text, type) {
        const data = {};
        // Extrair valor monetário
        const value = this.extractValue(text);
        if (value)
            data.value = value;
        // Extrair categoria baseada no tipo
        const category = this.extractCategory(text, type);
        if (category)
            data.category = category;
        // Extrair entidades específicas
        const entities = this.extractEntities(text);
        if (Object.keys(entities).length > 0)
            data.entities = entities;
        return data;
    }
    /**
     * Extrai valor monetário do texto
     */
    extractValue(text) {
        // Padrões para valores em reais
        const patterns = [
            /R\$\s*(\d+(?:[.,]\d{2})?)/g,
            /(\d+(?:[.,]\d{2})?)?\s*reais?/gi,
            /(\d+(?:[.,]\d{2})?)\s*(?:R\$|reais?)/gi
        ];
        for (const pattern of patterns) {
            const matches = text.match(pattern);
            if (matches) {
                for (const match of matches) {
                    const numberMatch = match.match(/(\d+(?:[.,]\d{2})?)/);
                    if (numberMatch) {
                        const value = parseFloat(numberMatch[1].replace(',', '.'));
                        if (!isNaN(value))
                            return value;
                    }
                }
            }
        }
        return undefined;
    }
    /**
     * Extrai categoria baseada no tipo de interação
     */
    extractCategory(text, type) {
        const allPatterns = [
            ...this.purchasePatterns,
            ...this.feedbackPatterns,
            ...this.complaintPatterns,
            ...this.questionPatterns,
            ...this.profilePatterns
        ];
        for (const pattern of allPatterns) {
            if (pattern.type === type && pattern.pattern.test(text)) {
                return pattern.category;
            }
        }
        return undefined;
    }
    /**
     * Extrai entidades nomeadas do texto
     */
    extractEntities(text) {
        const entities = {};
        // Extrair nomes (palavras capitalizadas)
        const namePattern = /(?:me chamo|meu nome é|sou)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/i;
        const nameMatch = text.match(namePattern);
        if (nameMatch) {
            entities.name = nameMatch[1];
        }
        // Extrair cidades
        const cityPattern = /(?:moro em|cidade|de)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/i;
        const cityMatch = text.match(cityPattern);
        if (cityMatch) {
            entities.city = cityMatch[1];
        }
        // Extrair idade
        const agePattern = /(\d{1,2})\s*anos?/i;
        const ageMatch = text.match(agePattern);
        if (ageMatch) {
            entities.age = parseInt(ageMatch[1]);
        }
        // Extrair profissão
        const professionPattern = /(?:trabalho como|sou|profissão)\s+([a-z]+(?:\s+[a-z]+)*)/i;
        const professionMatch = text.match(professionPattern);
        if (professionMatch) {
            entities.profession = professionMatch[1];
        }
        return entities;
    }
    /**
     * Determina se deve gerar uma resposta automática
     */
    shouldGenerateResponse(type, sentiment) {
        // Sempre responder a reclamações
        if (type === Interaction_1.InteractionType.COMPLAINT)
            return true;
        // Responder a perguntas
        if (type === Interaction_1.InteractionType.QUESTION)
            return true;
        // Responder a feedback negativo
        if (type === Interaction_1.InteractionType.FEEDBACK && sentiment === Interaction_1.SentimentType.NEGATIVE)
            return true;
        // Confirmar compras
        if (type === Interaction_1.InteractionType.PURCHASE)
            return true;
        // Confirmar atualizações de perfil
        if (type === Interaction_1.InteractionType.PROFILE_UPDATE)
            return true;
        return false;
    }
    /**
     * Gera uma resposta automática baseada no contexto
     */
    generateResponse(type, sentiment, extractedData) {
        switch (type) {
            case Interaction_1.InteractionType.PURCHASE:
                if (extractedData.value) {
                    return `✅ Compra registrada! Valor: R$ ${extractedData.value.toFixed(2)}. Obrigado pela informação!`;
                }
                return '✅ Compra registrada! Obrigado por compartilhar essa informação conosco.';
            case Interaction_1.InteractionType.COMPLAINT:
                return '😔 Lamentamos o inconveniente. Nossa equipe irá analisar sua reclamação e entrar em contato em breve.';
            case Interaction_1.InteractionType.FEEDBACK:
                if (sentiment === Interaction_1.SentimentType.POSITIVE) {
                    return '😊 Que bom saber que você gostou! Seu feedback é muito importante para nós.';
                }
                else if (sentiment === Interaction_1.SentimentType.NEGATIVE) {
                    return '😔 Agradecemos seu feedback. Vamos trabalhar para melhorar sua experiência.';
                }
                return '📝 Obrigado pelo seu feedback! Sua opinião é muito valiosa para nós.';
            case Interaction_1.InteractionType.QUESTION:
                return '❓ Recebemos sua pergunta! Nossa equipe irá responder em breve com as informações solicitadas.';
            case Interaction_1.InteractionType.PROFILE_UPDATE:
                return '📝 Informações atualizadas com sucesso! Obrigado por manter seu perfil atualizado.';
            default:
                return '👋 Olá! Recebemos sua mensagem e nossa equipe irá analisá-la em breve.';
        }
    }
    /**
     * Processa múltiplas mensagens
     */
    processMessages(messages) {
        return messages.map(message => this.processMessage(message));
    }
}
exports.MessageProcessorService = MessageProcessorService;
//# sourceMappingURL=MessageProcessorService.js.map