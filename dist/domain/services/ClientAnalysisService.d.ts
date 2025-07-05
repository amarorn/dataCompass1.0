import { Client, ClientSegment, ChurnRisk } from '@domain/entities/Client';
import { Interaction } from '@domain/entities/Interaction';
export interface ClientAnalysisData {
    client: Client;
    interactions: Interaction[];
    totalValue: number;
    interactionCount: number;
    daysSinceLastInteraction: number;
    averageValue: number;
    purchaseFrequency: number;
    sentimentScore: number;
}
export declare class ClientAnalysisService {
    /**
     * Calcula o score de engajamento do cliente
     * Baseado em: frequência de interação, recência, valor das compras, sentimento
     */
    calculateEngagementScore(data: ClientAnalysisData): number;
    /**
     * Determina o segmento do cliente baseado em comportamento e valor
     */
    determineClientSegment(data: ClientAnalysisData): ClientSegment;
    /**
     * Calcula o risco de churn do cliente
     */
    calculateChurnRisk(data: ClientAnalysisData): ChurnRisk;
    /**
     * Calcula o score de sentimento baseado nas interações
     */
    calculateSentimentScore(interactions: Interaction[]): number;
    /**
     * Calcula a frequência de compras (compras por mês)
     */
    calculatePurchaseFrequency(interactions: Interaction[]): number;
    /**
     * Identifica padrões de comportamento do cliente
     */
    identifyBehaviorPatterns(interactions: Interaction[]): Record<string, any>;
    /**
     * Gera recomendações baseadas no perfil do cliente
     */
    generateRecommendations(data: ClientAnalysisData): string[];
}
//# sourceMappingURL=ClientAnalysisService.d.ts.map