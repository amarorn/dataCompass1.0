import { Router, Request, Response } from 'express';
import { asyncHandler } from '../middlewares/errorHandler';

const router = Router();

// Sistema temporário de armazenamento em memória para mensagens
interface MessageHistory {
  id: string;
  from: string;
  message: string;
  timestamp: string;
  type: 'sent' | 'received';
  analysis?: {
    type: string;
    sentiment: string;
    value?: number;
    category?: string;
  };
}

// Array temporário para armazenar histórico de mensagens
let messageHistory: MessageHistory[] = [];

// Função para adicionar mensagem ao histórico
export function addToHistory(message: MessageHistory) {
  messageHistory.unshift(message); // Adiciona no início
  // Manter apenas os últimos 50 registros
  if (messageHistory.length > 50) {
    messageHistory = messageHistory.slice(0, 50);
  }
}

// GET /api/messages/history - Ver histórico de mensagens
router.get('/history', asyncHandler(async (req: Request, res: Response) => {
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
router.get('/received', asyncHandler(async (req: Request, res: Response) => {
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
router.get('/sent', asyncHandler(async (req: Request, res: Response) => {
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
router.get('/user/:phoneNumber', asyncHandler(async (req: Request, res: Response) => {
  const { phoneNumber } = req.params;
  
  const userMessages = messageHistory.filter(msg => 
    msg.from === phoneNumber || 
    msg.from === `55${phoneNumber}` || 
    msg.from === `+55${phoneNumber}`
  );
  
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
router.delete('/clear', asyncHandler(async (req: Request, res: Response) => {
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

export { router as messageHistoryRoutes };
