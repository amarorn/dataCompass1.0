"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.analyticsRoutes = void 0;
const express_1 = require("express");
const errorHandler_1 = require("../middlewares/errorHandler");
const router = (0, express_1.Router)();
exports.analyticsRoutes = router;
// GET /api/analytics/dashboard - Dashboard geral
router.get('/dashboard', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    res.json({
        success: true,
        message: 'Dashboard analytics',
        data: {
            totalClients: 150,
            totalInteractions: 1250,
            totalInsights: 45,
            segments: {
                VIP: 15,
                FREQUENT: 45,
                OCCASIONAL: 70,
                INACTIVE: 20
            },
            churnRisk: {
                LOW: 100,
                MEDIUM: 30,
                HIGH: 15,
                CRITICAL: 5
            },
            averageEngagementScore: 68.5
        }
    });
}));
// GET /api/analytics/clients/:id - Analytics específico do cliente
router.get('/clients/:id', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { id } = req.params;
    res.json({
        success: true,
        message: 'Analytics do cliente',
        data: {
            clientId: id,
            engagementScore: 75,
            segment: 'FREQUENT',
            churnRisk: 'LOW',
            totalValue: 2500.00,
            interactionCount: 25,
            daysSinceLastInteraction: 3,
            sentimentScore: 0.7,
            recommendations: [
                'Programa de fidelidade',
                'Produtos complementares',
                'Descontos por volume'
            ],
            behaviorPatterns: {
                preferredContactHour: 14,
                preferredCategories: ['eletrônicos', 'casa'],
                purchasePattern: {
                    averageValue: 250,
                    totalPurchases: 10
                }
            }
        }
    });
}));
// GET /api/analytics/insights - Listar insights
router.get('/insights', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    res.json({
        success: true,
        message: 'Lista de insights',
        data: [
            {
                id: 'insight-1',
                type: 'CHURN_PREDICTION',
                title: 'Risco de Churn: 85%',
                description: 'Cliente com alta probabilidade de churn',
                priority: 'CRITICAL',
                confidence: 0.85,
                actionable: true,
                createdAt: new Date().toISOString()
            },
            {
                id: 'insight-2',
                type: 'RECOMMENDATION',
                title: 'Recomendações Personalizadas',
                description: 'Produtos recomendados baseados no perfil',
                priority: 'MEDIUM',
                confidence: 0.72,
                actionable: true,
                createdAt: new Date().toISOString()
            }
        ],
        meta: {
            total: 2,
            page: 1,
            limit: 10
        }
    });
}));
// POST /api/analytics/generate - Gerar novos insights
router.post('/generate', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { clientId, type } = req.body;
    res.json({
        success: true,
        message: 'Insights gerados com sucesso',
        data: {
            generated: 3,
            clientId,
            type,
            timestamp: new Date().toISOString()
        }
    });
}));
//# sourceMappingURL=analyticsRoutes.js.map