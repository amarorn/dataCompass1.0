"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ClientAnalysisService = void 0;
const Client_1 = require("@domain/entities/Client");
const Interaction_1 = require("@domain/entities/Interaction");
class ClientAnalysisService {
    /**
     * Calcula o score de engajamento do cliente
     * Baseado em: frequência de interação, recência, valor das compras, sentimento
     */
    calculateEngagementScore(data) {
        const { interactionCount, daysSinceLastInteraction, totalValue, purchaseFrequency, sentimentScore } = data;
        // Peso dos fatores (total = 1.0)
        const weights = {
            frequency: 0.3, // Frequência de interação
            recency: 0.25, // Recência da última interação
            value: 0.25, // Valor total das compras
            sentiment: 0.2 // Sentimento geral
        };
        // Score de frequência (0-100)
        const frequencyScore = Math.min(interactionCount * 5, 100);
        // Score de recência (0-100) - quanto menor os dias, maior o score
        const recencyScore = Math.max(0, 100 - (daysSinceLastInteraction * 2));
        // Score de valor (0-100) - normalizado baseado em valor médio
        const valueScore = Math.min((totalValue / 1000) * 10, 100);
        // Score de sentimento (0-100)
        const sentimentScoreNormalized = (sentimentScore + 1) * 50; // -1 a 1 -> 0 a 100
        // Cálculo final ponderado
        const finalScore = (frequencyScore * weights.frequency +
            recencyScore * weights.recency +
            valueScore * weights.value +
            sentimentScoreNormalized * weights.sentiment);
        return Math.round(Math.min(finalScore, 100));
    }
    /**
     * Determina o segmento do cliente baseado em comportamento e valor
     */
    determineClientSegment(data) {
        const { totalValue, interactionCount, daysSinceLastInteraction, purchaseFrequency } = data;
        // Critérios para VIP
        if (totalValue > 5000 && interactionCount > 20 && daysSinceLastInteraction < 7) {
            return Client_1.ClientSegment.VIP;
        }
        // Critérios para Frequente
        if (purchaseFrequency > 0.5 && interactionCount > 10 && daysSinceLastInteraction < 30) {
            return Client_1.ClientSegment.FREQUENT;
        }
        // Critérios para Inativo
        if (daysSinceLastInteraction > 90 || interactionCount < 3) {
            return Client_1.ClientSegment.INACTIVE;
        }
        // Padrão: Ocasional
        return Client_1.ClientSegment.OCCASIONAL;
    }
    /**
     * Calcula o risco de churn do cliente
     */
    calculateChurnRisk(data) {
        const { daysSinceLastInteraction, interactionCount, sentimentScore, purchaseFrequency } = data;
        let riskScore = 0;
        // Fatores que aumentam o risco
        if (daysSinceLastInteraction > 60)
            riskScore += 30;
        else if (daysSinceLastInteraction > 30)
            riskScore += 15;
        else if (daysSinceLastInteraction > 14)
            riskScore += 5;
        if (interactionCount < 5)
            riskScore += 20;
        else if (interactionCount < 10)
            riskScore += 10;
        if (sentimentScore < -0.3)
            riskScore += 25;
        else if (sentimentScore < 0)
            riskScore += 10;
        if (purchaseFrequency < 0.1)
            riskScore += 20;
        else if (purchaseFrequency < 0.3)
            riskScore += 10;
        // Determinar nível de risco
        if (riskScore >= 70)
            return Client_1.ChurnRisk.CRITICAL;
        if (riskScore >= 50)
            return Client_1.ChurnRisk.HIGH;
        if (riskScore >= 25)
            return Client_1.ChurnRisk.MEDIUM;
        return Client_1.ChurnRisk.LOW;
    }
    /**
     * Calcula o score de sentimento baseado nas interações
     */
    calculateSentimentScore(interactions) {
        if (interactions.length === 0)
            return 0;
        const sentimentValues = interactions.map(interaction => {
            switch (interaction.sentiment) {
                case Interaction_1.SentimentType.POSITIVE: return 1;
                case Interaction_1.SentimentType.NEUTRAL: return 0;
                case Interaction_1.SentimentType.NEGATIVE: return -1;
                default: return 0;
            }
        });
        const average = sentimentValues.reduce((sum, value) => sum + value, 0) / sentimentValues.length;
        return Math.round(average * 100) / 100; // Arredondar para 2 casas decimais
    }
    /**
     * Calcula a frequência de compras (compras por mês)
     */
    calculatePurchaseFrequency(interactions) {
        const purchases = interactions.filter(i => i.type === Interaction_1.InteractionType.PURCHASE);
        if (purchases.length === 0)
            return 0;
        // Calcular período em meses desde a primeira compra
        const firstPurchase = purchases.reduce((earliest, current) => current.createdAt < earliest.createdAt ? current : earliest);
        const monthsSinceFirst = Math.max(1, (Date.now() - firstPurchase.createdAt.getTime()) / (1000 * 60 * 60 * 24 * 30));
        return purchases.length / monthsSinceFirst;
    }
    /**
     * Identifica padrões de comportamento do cliente
     */
    identifyBehaviorPatterns(interactions) {
        const patterns = {};
        // Padrão temporal - horários preferidos
        const hourCounts = {};
        interactions.forEach(interaction => {
            const hour = interaction.createdAt.getHours();
            hourCounts[hour] = (hourCounts[hour] || 0) + 1;
        });
        const preferredHour = Object.entries(hourCounts)
            .sort(([, a], [, b]) => b - a)[0]?.[0];
        if (preferredHour) {
            patterns.preferredContactHour = parseInt(preferredHour);
        }
        // Padrão de categorias
        const categoryInteractions = interactions.filter(i => i.category);
        const categoryCounts = {};
        categoryInteractions.forEach(interaction => {
            if (interaction.category) {
                categoryCounts[interaction.category] = (categoryCounts[interaction.category] || 0) + 1;
            }
        });
        const topCategories = Object.entries(categoryCounts)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 3)
            .map(([category]) => category);
        if (topCategories.length > 0) {
            patterns.preferredCategories = topCategories;
        }
        // Padrão de valor de compra
        const purchases = interactions.filter(i => i.isPurchase() && i.hasValue());
        if (purchases.length > 0) {
            const values = purchases.map(p => p.getValueOrZero());
            const avgValue = values.reduce((sum, val) => sum + val, 0) / values.length;
            const maxValue = Math.max(...values);
            const minValue = Math.min(...values);
            patterns.purchasePattern = {
                averageValue: Math.round(avgValue),
                maxValue,
                minValue,
                totalPurchases: purchases.length
            };
        }
        // Padrão de comunicação
        const communicationPattern = {
            totalInteractions: interactions.length,
            questionsAsked: interactions.filter(i => i.type === Interaction_1.InteractionType.QUESTION).length,
            complaintsRaised: interactions.filter(i => i.type === Interaction_1.InteractionType.COMPLAINT).length,
            feedbackGiven: interactions.filter(i => i.type === Interaction_1.InteractionType.FEEDBACK).length
        };
        patterns.communicationPattern = communicationPattern;
        return patterns;
    }
    /**
     * Gera recomendações baseadas no perfil do cliente
     */
    generateRecommendations(data) {
        const recommendations = [];
        const { client, totalValue, daysSinceLastInteraction, sentimentScore } = data;
        // Recomendações baseadas em segmento
        switch (client.segment) {
            case Client_1.ClientSegment.VIP:
                recommendations.push('Produtos premium exclusivos');
                recommendations.push('Atendimento personalizado VIP');
                recommendations.push('Ofertas antecipadas de lançamentos');
                break;
            case Client_1.ClientSegment.FREQUENT:
                recommendations.push('Programa de fidelidade');
                recommendations.push('Descontos por volume');
                recommendations.push('Produtos complementares');
                break;
            case Client_1.ClientSegment.INACTIVE:
                recommendations.push('Campanha de reativação');
                recommendations.push('Ofertas especiais de retorno');
                recommendations.push('Pesquisa de satisfação');
                break;
        }
        // Recomendações baseadas em comportamento
        if (daysSinceLastInteraction > 30) {
            recommendations.push('Contato proativo para reengajamento');
        }
        if (sentimentScore < 0) {
            recommendations.push('Ação de melhoria da experiência');
            recommendations.push('Follow-up de satisfação');
        }
        if (totalValue > 3000) {
            recommendations.push('Upgrade para categoria premium');
        }
        return [...new Set(recommendations)]; // Remove duplicatas
    }
}
exports.ClientAnalysisService = ClientAnalysisService;
//# sourceMappingURL=ClientAnalysisService.js.map