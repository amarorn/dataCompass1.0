import { Router, Request, Response } from 'express';
import { asyncHandler } from '../middlewares/errorHandler';

const router = Router();

// GET /api/clients - Listar clientes
router.get('/', asyncHandler(async (req: Request, res: Response) => {
  res.json({
    success: true,
    message: 'Lista de clientes',
    data: [],
    meta: {
      total: 0,
      page: 1,
      limit: 10
    }
  });
}));

// GET /api/clients/:id - Buscar cliente por ID
router.get('/:id', asyncHandler(async (req: Request, res: Response) => {
  const { id } = req.params;
  
  res.json({
    success: true,
    message: 'Cliente encontrado',
    data: {
      id,
      whatsappNumber: '+5511999999999',
      name: 'Cliente Exemplo',
      segment: 'FREQUENT',
      engagementScore: 75
    }
  });
}));

// POST /api/clients - Criar novo cliente
router.post('/', asyncHandler(async (req: Request, res: Response) => {
  const clientData = req.body;
  
  res.status(201).json({
    success: true,
    message: 'Cliente criado com sucesso',
    data: {
      id: 'generated-uuid',
      ...clientData,
      createdAt: new Date().toISOString()
    }
  });
}));

// PUT /api/clients/:id - Atualizar cliente
router.put('/:id', asyncHandler(async (req: Request, res: Response) => {
  const { id } = req.params;
  const updateData = req.body;
  
  res.json({
    success: true,
    message: 'Cliente atualizado com sucesso',
    data: {
      id,
      ...updateData,
      updatedAt: new Date().toISOString()
    }
  });
}));

// DELETE /api/clients/:id - Deletar cliente
router.delete('/:id', asyncHandler(async (req: Request, res: Response) => {
  const { id } = req.params;
  
  res.json({
    success: true,
    message: 'Cliente deletado com sucesso',
    data: { id }
  });
}));

export { router as clientRoutes };

