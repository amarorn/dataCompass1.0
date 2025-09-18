"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.tokenRoutes = void 0;
const express_1 = require("express");
const errorHandler_1 = require("../middlewares/errorHandler");
const TokenManager_1 = require("../../infrastructure/external/TokenManager");
const router = (0, express_1.Router)();
exports.tokenRoutes = router;
const tokenManager = new TokenManager_1.TokenManager();
// GET /api/token/info - Informações do token atual
router.get('/info', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    try {
        const tokenInfo = await tokenManager.getTokenInfo();
        const isValid = await tokenManager.validateToken();
        const isExpiringSoon = tokenManager.isTokenExpiringSoon();
        res.json({
            success: true,
            message: 'Token information retrieved',
            data: {
                tokenInfo,
                isValid,
                isExpiringSoon,
                currentToken: process.env.WHATSAPP_TOKEN ?
                    `${process.env.WHATSAPP_TOKEN.substring(0, 20)}...` : 'Not configured',
                timestamp: new Date().toISOString()
            }
        });
    }
    catch (error) {
        res.status(500).json({
            success: false,
            error: {
                message: 'Failed to get token information',
                statusCode: 500,
                details: error.message
            }
        });
    }
}));
// POST /api/token/refresh - Renovar token
router.post('/refresh', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    try {
        const newToken = await tokenManager.refreshTokenMethod();
        res.json({
            success: true,
            message: 'Token refreshed successfully',
            data: {
                newToken: `${newToken.substring(0, 20)}...`,
                timestamp: new Date().toISOString(),
                note: 'Update your .env file with the new token'
            }
        });
    }
    catch (error) {
        res.status(500).json({
            success: false,
            error: {
                message: 'Failed to refresh token',
                statusCode: 500,
                details: error.message
            }
        });
    }
}));
// GET /api/token/validate - Validar token atual
router.get('/validate', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    try {
        const isValid = await tokenManager.validateToken();
        res.json({
            success: true,
            message: 'Token validation completed',
            data: {
                isValid,
                timestamp: new Date().toISOString()
            }
        });
    }
    catch (error) {
        res.status(500).json({
            success: false,
            error: {
                message: 'Failed to validate token',
                statusCode: 500,
                details: error.message
            }
        });
    }
}));
//# sourceMappingURL=tokenRoutes.js.map