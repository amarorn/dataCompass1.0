import { Router, Request, Response } from 'express';
import { asyncHandler } from '../middlewares/errorHandler';
import { TokenManager } from '../../infrastructure/external/TokenManager';

const router = Router();
const tokenManager = new TokenManager();

// GET /api/token/info - Informações do token atual
router.get('/info', asyncHandler(async (req: Request, res: Response) => {
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
  } catch (error: any) {
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
router.post('/refresh', asyncHandler(async (req: Request, res: Response) => {
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
  } catch (error: any) {
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
router.get('/validate', asyncHandler(async (req: Request, res: Response) => {
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
  } catch (error: any) {
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

export { router as tokenRoutes };
