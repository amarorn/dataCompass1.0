"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.messageHistoryRoutes = void 0;
exports.addToHistory = addToHistory;
const express_1 = require("express");
const errorHandler_1 = require("../middlewares/errorHandler");
const router = (0, express_1.Router)();
exports.messageHistoryRoutes = router;
// Array temporário para armazenar histórico de mensagens
let messageHistory = [];
// Função para adicionar mensagem ao histórico
function addToHistory(message) {
    messageHistory.unshift(message); // Adiciona no início
    // Manter apenas os últimos 50 registros
    if (messageHistory.length > 50) {
        messageHistory = messageHistory.slice(0, 50);
    }
}
// GET /api/messages/history - Ver histórico de mensagens
router.get('/history', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { limit = 10, type } = req.query;
    let filteredMessages = messageHistory;
    // Filtrar por tipo se especificado
    if (type && (type === 'sent' || type === 'received')) {
        filteredMessages = messageHistory.filter(msg => msg.type === type);
    }
    // Aplicar limite
    const limitedMessages = filteredMessages.slice(0, Number(limit));
    res.json({
        success: true,
        message: 'Histórico de mensagens',
        data: limitedMessages,
        meta: {
            total: filteredMessages.length,
            showing: limitedMessages.length,
            filter: type || 'all'
        }
    });
}));
// GET /api/messages/received - Ver apenas mensagens recebidas
router.get('/received', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const receivedMessages = messageHistory.filter(msg => msg.type === 'received');
    res.json({
        success: true,
        message: 'Mensagens recebidas dos usuários',
        data: receivedMessages,
        meta: {
            total: receivedMessages.length,
            lastReceived: receivedMessages[0]?.timestamp || null
        }
    });
}));
// GET /api/messages/sent - Ver apenas mensagens enviadas
router.get('/sent', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const sentMessages = messageHistory.filter(msg => msg.type === 'sent');
    res.json({
        success: true,
        message: 'Mensagens enviadas para usuários',
        data: sentMessages,
        meta: {
            total: sentMessages.length,
            lastSent: sentMessages[0]?.timestamp || null
        }
    });
}));
// GET /api/messages/user/:phoneNumber - Ver mensagens de um usuário específico
router.get('/user/:phoneNumber', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { phoneNumber } = req.params;
    const userMessages = messageHistory.filter(msg => msg.from === phoneNumber ||
        msg.from === `55${phoneNumber}` ||
        msg.from === `+55${phoneNumber}`);
    res.json({
        success: true,
        message: `Mensagens do usuário ${phoneNumber}`,
        data: userMessages,
        meta: {
            phoneNumber,
            total: userMessages.length,
            received: userMessages.filter(m => m.type === 'received').length,
            sent: userMessages.filter(m => m.type === 'sent').length
        }
    });
}));
// DELETE /api/messages/clear - Limpar histórico
router.delete('/clear', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const previousCount = messageHistory.length;
    messageHistory = [];
    res.json({
        success: true,
        message: 'Histórico limpo com sucesso',
        data: {
            previousCount,
            currentCount: 0
        }
    });
}));
//# sourceMappingURL=messageHistoryRoutes.js.map