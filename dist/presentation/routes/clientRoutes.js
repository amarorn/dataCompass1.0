"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.clientRoutes = void 0;
const express_1 = require("express");
const errorHandler_1 = require("../middlewares/errorHandler");
const router = (0, express_1.Router)();
exports.clientRoutes = router;
// GET /api/clients - Listar clientes
router.get('/', (0, errorHandler_1.asyncHandler)(async (req, res) => {
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
router.get('/:id', (0, errorHandler_1.asyncHandler)(async (req, res) => {
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
router.post('/', (0, errorHandler_1.asyncHandler)(async (req, res) => {
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
router.put('/:id', (0, errorHandler_1.asyncHandler)(async (req, res) => {
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
router.delete('/:id', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { id } = req.params;
    res.json({
        success: true,
        message: 'Cliente deletado com sucesso',
        data: { id }
    });
}));
//# sourceMappingURL=clientRoutes.js.map