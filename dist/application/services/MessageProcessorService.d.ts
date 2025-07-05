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
export declare class MessageProcessorService {
    private readonly purchasePatterns;
    private readonly feedbackPatterns;
    private readonly complaintPatterns;
    private readonly questionPatterns;
    private readonly profilePatterns;
    /**
     * Processa uma mensagem do WhatsApp
     */
    processMessage(message: WhatsAppMessage): ProcessedMessage;
    /**
     * Detecta o tipo de interação baseado no texto
     */
    private detectInteractionType;
    /**
     * Analisa o sentimento do texto
     */
    private analyzeSentiment;
    /**
     * Extrai dados estruturados do texto
     */
    private extractData;
    /**
     * Extrai valor monetário do texto
     */
    private extractValue;
    /**
     * Extrai categoria baseada no tipo de interação
     */
    private extractCategory;
    /**
     * Extrai entidades nomeadas do texto
     */
    private extractEntities;
    /**
     * Determina se deve gerar uma resposta automática
     */
    private shouldGenerateResponse;
    /**
     * Gera uma resposta automática baseada no contexto
     */
    private generateResponse;
    /**
     * Processa múltiplas mensagens
     */
    processMessages(messages: WhatsAppMessage[]): ProcessedMessage[];
}
//# sourceMappingURL=MessageProcessorService.d.ts.map