import { WhatsAppMessage } from '../../infrastructure/external/WhatsAppService';
import { InteractionType, SentimentType } from '../../domain/entities/Interaction';

export interface ProcessedMessage {
  originalMessage: WhatsAppMessage;
  interactionType: InteractionType;
  sentiment: SentimentType;
  extractedData: {
    value?: number;
    category?: string;
    intent?: string;
    entities?: Record<string, any>;
  };
  shouldRespond: boolean;
  suggestedResponse?: string;
}

export interface MessagePattern {
  pattern: RegExp;
  type: InteractionType;
  category?: string;
  valueExtractor?: (text: string) => number | undefined;
}

export class MessageProcessorService {
  private readonly purchasePatterns: MessagePattern[] = [
    {
      pattern: /comprei|compra|gastei|paguei|adquiri/i,
      type: InteractionType.PURCHASE,
      category: 'geral',
      valueExtractor: this.extractValue
    },
    {
      pattern: /supermercado|mercado|alimentação|comida/i,
      type: InteractionType.PURCHASE,
      category: 'alimentação',
      valueExtractor: this.extractValue
    },
    {
      pattern: /roupa|vestuário|calça|camisa|vestido|sapato/i,
      type: InteractionType.PURCHASE,
      category: 'vestuário',
      valueExtractor: this.extractValue
    },
    {
      pattern: /eletrônico|celular|computador|tv|notebook/i,
      type: InteractionType.PURCHASE,
      category: 'eletrônicos',
      valueExtractor: this.extractValue
    },
    {
      pattern: /casa|móvel|decoração|cozinha/i,
      type: InteractionType.PURCHASE,
      category: 'casa',
      valueExtractor: this.extractValue
    }
  ];

  private readonly feedbackPatterns: MessagePattern[] = [
    {
      pattern: /gostei|adorei|excelente|ótimo|perfeito|recomendo/i,
      type: InteractionType.FEEDBACK,
      category: 'positivo'
    },
    {
      pattern: /não gostei|ruim|péssimo|horrível|decepcionado/i,
      type: InteractionType.FEEDBACK,
      category: 'negativo'
    },
    {
      pattern: /feedback|opinião|avaliação|comentário/i,
      type: InteractionType.FEEDBACK,
      category: 'geral'
    }
  ];

  private readonly complaintPatterns: MessagePattern[] = [
    {
      pattern: /reclamação|problema|defeito|quebrado|não funciona/i,
      type: InteractionType.COMPLAINT,
      category: 'produto'
    },
    {
      pattern: /atendimento|demora|espera|mal atendido/i,
      type: InteractionType.COMPLAINT,
      category: 'atendimento'
    },
    {
      pattern: /entrega|atraso|não chegou|perdido/i,
      type: InteractionType.COMPLAINT,
      category: 'entrega'
    }
  ];

  private readonly questionPatterns: MessagePattern[] = [
    {
      pattern: /\?|como|quando|onde|qual|quanto|por que/i,
      type: InteractionType.QUESTION,
      category: 'informação'
    },
    {
      pattern: /preço|valor|custo|quanto custa/i,
      type: InteractionType.QUESTION,
      category: 'preço'
    },
    {
      pattern: /disponível|estoque|tem|possui/i,
      type: InteractionType.QUESTION,
      category: 'disponibilidade'
    }
  ];

  private readonly profilePatterns: MessagePattern[] = [
    {
      pattern: /meu nome é|me chamo|sou|trabalho como|profissão/i,
      type: InteractionType.PROFILE_UPDATE,
      category: 'identificação'
    },
    {
      pattern: /moro em|cidade|endereço|localização/i,
      type: InteractionType.PROFILE_UPDATE,
      category: 'localização'
    },
    {
      pattern: /idade|anos|nasci|aniversário/i,
      type: InteractionType.PROFILE_UPDATE,
      category: 'idade'
    }
  ];

  /**
   * Processa uma mensagem do WhatsApp
   */
  public processMessage(message: WhatsAppMessage): ProcessedMessage {
    if (message.type !== 'text' || !message.text?.body) {
      return {
        originalMessage: message,
        interactionType: InteractionType.GENERAL,
        sentiment: SentimentType.NEUTRAL,
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
  private detectInteractionType(text: string): InteractionType {
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

    return InteractionType.GENERAL;
  }

  /**
   * Analisa o sentimento do texto
   */
  private analyzeSentiment(text: string): SentimentType {
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
      if (lowerText.includes(word)) positiveScore++;
    });

    negativeWords.forEach(word => {
      if (lowerText.includes(word)) negativeScore++;
    });

    if (positiveScore > negativeScore) return SentimentType.POSITIVE;
    if (negativeScore > positiveScore) return SentimentType.NEGATIVE;
    return SentimentType.NEUTRAL;
  }

  /**
   * Extrai dados estruturados do texto
   */
  private extractData(text: string, type: InteractionType): Record<string, any> {
    const data: Record<string, any> = {};

    // Extrair valor monetário
    const value = this.extractValue(text);
    if (value) data.value = value;

    // Extrair categoria baseada no tipo
    const category = this.extractCategory(text, type);
    if (category) data.category = category;

    // Extrair entidades específicas
    const entities = this.extractEntities(text);
    if (Object.keys(entities).length > 0) data.entities = entities;

    return data;
  }

  /**
   * Extrai valor monetário do texto
   */
  private extractValue(text: string): number | undefined {
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
            if (!isNaN(value)) return value;
          }
        }
      }
    }

    return undefined;
  }

  /**
   * Extrai categoria baseada no tipo de interação
   */
  private extractCategory(text: string, type: InteractionType): string | undefined {
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
  private extractEntities(text: string): Record<string, any> {
    const entities: Record<string, any> = {};

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
  private shouldGenerateResponse(type: InteractionType, sentiment: SentimentType): boolean {
    // Sempre responder a reclamações
    if (type === InteractionType.COMPLAINT) return true;
    
    // Responder a perguntas
    if (type === InteractionType.QUESTION) return true;
    
    // Responder a feedback negativo
    if (type === InteractionType.FEEDBACK && sentiment === SentimentType.NEGATIVE) return true;
    
    // Confirmar compras
    if (type === InteractionType.PURCHASE) return true;
    
    // Confirmar atualizações de perfil
    if (type === InteractionType.PROFILE_UPDATE) return true;

    return false;
  }

  /**
   * Gera uma resposta automática baseada no contexto
   */
  private generateResponse(
    type: InteractionType, 
    sentiment: SentimentType, 
    extractedData: Record<string, any>
  ): string {
    switch (type) {
      case InteractionType.PURCHASE:
        if (extractedData.value) {
          return `✅ Compra registrada! Valor: R$ ${extractedData.value.toFixed(2)}. Obrigado pela informação!`;
        }
        return '✅ Compra registrada! Obrigado por compartilhar essa informação conosco.';

      case InteractionType.COMPLAINT:
        return '😔 Lamentamos o inconveniente. Nossa equipe irá analisar sua reclamação e entrar em contato em breve.';

      case InteractionType.FEEDBACK:
        if (sentiment === SentimentType.POSITIVE) {
          return '😊 Que bom saber que você gostou! Seu feedback é muito importante para nós.';
        } else if (sentiment === SentimentType.NEGATIVE) {
          return '😔 Agradecemos seu feedback. Vamos trabalhar para melhorar sua experiência.';
        }
        return '📝 Obrigado pelo seu feedback! Sua opinião é muito valiosa para nós.';

      case InteractionType.QUESTION:
        return '❓ Recebemos sua pergunta! Nossa equipe irá responder em breve com as informações solicitadas.';

      case InteractionType.PROFILE_UPDATE:
        return '📝 Informações atualizadas com sucesso! Obrigado por manter seu perfil atualizado.';

      default:
        return '👋 Olá! Recebemos sua mensagem e nossa equipe irá analisá-la em breve.';
    }
  }

  /**
   * Processa múltiplas mensagens
   */
  public processMessages(messages: WhatsAppMessage[]): ProcessedMessage[] {
    return messages.map(message => this.processMessage(message));
  }
}

