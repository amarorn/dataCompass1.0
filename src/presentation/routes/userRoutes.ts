import { Router, Request, Response } from 'express';
import { asyncHandler } from '../middlewares/errorHandler';
import { MongoConnection } from '../../infrastructure/database/MongoConnection';
import { MongoUserRepository } from '../../infrastructure/database/MongoUserRepository';
import { User, UserRole, CreateUserRequest } from '../../domain/entities/User';

const router = Router();
let userRepository: MongoUserRepository | null = null;

// Inicializar MongoDB e repositório de usuários
async function initializeUserRepository() {
  try {
    const mongoConnection = MongoConnection.getInstance();
    const db = await mongoConnection.connect();
    userRepository = new MongoUserRepository(db);
    console.log('✅ User repository initialized');
  } catch (error) {
    console.error('❌ Failed to initialize user repository:', error);
  }
}

// Inicializar na primeira execução
initializeUserRepository();

// POST /api/users/register - Registrar novo usuário
router.post('/register', asyncHandler(async (req: Request, res: Response) => {
  const { email, password, name, company, phone, role } = req.body;

  if (!email || !password || !name) {
    return res.status(400).json({
      success: false,
      error: {
        message: 'Missing required fields: email, password, name',
        statusCode: 400
      }
    });
  }

  try {
    if (!userRepository) {
      throw new Error('User repository not initialized');
    }

    // Verificar se usuário já existe
    const existingUser = await userRepository.findByEmail(email);
    if (existingUser) {
      return res.status(409).json({
        success: false,
        error: {
          message: 'User already exists with this email',
          statusCode: 409
        }
      });
    }

    // Criar dados do usuário
    const userData: CreateUserRequest = {
      email,
      password,
      name,
      company,
      phone,
      role: role || UserRole.USER
    };

    const savedUser = await userRepository.create(userData);

    res.status(201).json({
      success: true,
      message: 'User registered successfully',
      data: {
        id: savedUser.id,
        email: savedUser.email,
        name: savedUser.name,
        company: savedUser.company,
        phone: savedUser.phone,
        role: savedUser.role,
        isActive: savedUser.isActive,
        createdAt: savedUser.createdAt
      }
    });

  } catch (error: any) {
    console.error('Error registering user:', error);
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to register user',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

// GET /api/users - Listar usuários
router.get('/', asyncHandler(async (req: Request, res: Response) => {
  try {
    if (!userRepository) {
      throw new Error('User repository not initialized');
    }

    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 10;
    const role = req.query.role as UserRole;

    const users = await userRepository.findAll(limit, (page - 1) * limit);

    res.json({
      success: true,
      message: 'Users retrieved successfully',
      data: {
        users: users.map(user => ({
          id: user.id,
          email: user.email,
          name: user.name,
          company: user.company,
          phone: user.phone,
          role: user.role,
          isActive: user.isActive,
          emailVerified: user.emailVerified,
          createdAt: user.createdAt,
          updatedAt: user.updatedAt,
          lastLoginAt: user.lastLoginAt
        })),
        pagination: {
          page,
          limit,
          total: users.length
        }
      }
    });

  } catch (error: any) {
    console.error('Error retrieving users:', error);
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to retrieve users',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

// GET /api/users/:id - Buscar usuário por ID
router.get('/:id', asyncHandler(async (req: Request, res: Response) => {
  const { id } = req.params;

  try {
    if (!userRepository) {
      throw new Error('User repository not initialized');
    }

    const user = await userRepository.findById(id);
    if (!user) {
      return res.status(404).json({
        success: false,
        error: {
          message: 'User not found',
          statusCode: 404
        }
      });
    }

    res.json({
      success: true,
      message: 'User retrieved successfully',
      data: {
        id: user.id,
        email: user.email,
        name: user.name,
        company: user.company,
        phone: user.phone,
        role: user.role,
        isActive: user.isActive,
        emailVerified: user.emailVerified,
        createdAt: user.createdAt,
        updatedAt: user.updatedAt,
        lastLoginAt: user.lastLoginAt
      }
    });

  } catch (error: any) {
    console.error('Error retrieving user:', error);
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to retrieve user',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

// PUT /api/users/:id - Atualizar usuário
router.put('/:id', asyncHandler(async (req: Request, res: Response) => {
  const { id } = req.params;
  const { name, company, phone, role, isActive } = req.body;

  try {
    if (!userRepository) {
      throw new Error('User repository not initialized');
    }

    const updateData: Partial<User> = {};
    if (name) updateData.name = name;
    if (company) updateData.company = company;
    if (phone) updateData.phone = phone;
    if (role) updateData.role = role;
    if (typeof isActive === 'boolean') updateData.isActive = isActive;
    updateData.updatedAt = new Date();

    const updatedUser = await userRepository.update(id, updateData);
    if (!updatedUser) {
      return res.status(404).json({
        success: false,
        error: {
          message: 'User not found',
          statusCode: 404
        }
      });
    }

    res.json({
      success: true,
      message: 'User updated successfully',
      data: {
        id: updatedUser.id,
        email: updatedUser.email,
        name: updatedUser.name,
        company: updatedUser.company,
        phone: updatedUser.phone,
        role: updatedUser.role,
        isActive: updatedUser.isActive,
        emailVerified: updatedUser.emailVerified,
        createdAt: updatedUser.createdAt,
        updatedAt: updatedUser.updatedAt
      }
    });

  } catch (error: any) {
    console.error('Error updating user:', error);
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to update user',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

// DELETE /api/users/:id - Deletar usuário
router.delete('/:id', asyncHandler(async (req: Request, res: Response) => {
  const { id } = req.params;

  try {
    if (!userRepository) {
      throw new Error('User repository not initialized');
    }

    const deleted = await userRepository.delete(id);
    if (!deleted) {
      return res.status(404).json({
        success: false,
        error: {
          message: 'User not found',
          statusCode: 404
        }
      });
    }

    res.json({
      success: true,
      message: 'User deleted successfully',
      data: {
        id,
        deletedAt: new Date().toISOString()
      }
    });

  } catch (error: any) {
    console.error('Error deleting user:', error);
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to delete user',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

// GET /api/users/email/:email - Buscar usuário por email
router.get('/email/:email', asyncHandler(async (req: Request, res: Response) => {
  const { email } = req.params;

  try {
    if (!userRepository) {
      throw new Error('User repository not initialized');
    }

    const user = await userRepository.findByEmail(email);
    if (!user) {
      return res.status(404).json({
        success: false,
        error: {
          message: 'User not found',
          statusCode: 404
        }
      });
    }

    res.json({
      success: true,
      message: 'User retrieved successfully',
      data: {
        id: user.id,
        email: user.email,
        name: user.name,
        company: user.company,
        phone: user.phone,
        role: user.role,
        isActive: user.isActive,
        emailVerified: user.emailVerified,
        createdAt: user.createdAt,
        updatedAt: user.updatedAt,
        lastLoginAt: user.lastLoginAt
      }
    });

  } catch (error: any) {
    console.error('Error retrieving user by email:', error);
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to retrieve user',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

// GET /api/users/stats - Estatísticas de usuários
router.get('/stats', asyncHandler(async (req: Request, res: Response) => {
  try {
    if (!userRepository) {
      throw new Error('User repository not initialized');
    }

    // Buscar todos os usuários para calcular estatísticas
    const allUsers = await userRepository.findAll(1000, 0);
    
    const stats = {
      total: allUsers.length,
      active: allUsers.filter(u => u.isActive).length,
      inactive: allUsers.filter(u => !u.isActive).length,
      admins: allUsers.filter(u => u.role === UserRole.ADMIN).length,
      managers: allUsers.filter(u => u.role === UserRole.MANAGER).length,
      users: allUsers.filter(u => u.role === UserRole.USER).length,
      emailVerified: allUsers.filter(u => u.emailVerified).length,
      registeredToday: allUsers.filter(u => {
        const today = new Date();
        const userDate = new Date(u.createdAt);
        return userDate.toDateString() === today.toDateString();
      }).length,
      registeredThisWeek: allUsers.filter(u => {
        const weekAgo = new Date();
        weekAgo.setDate(weekAgo.getDate() - 7);
        return new Date(u.createdAt) >= weekAgo;
      }).length
    };

    res.json({
      success: true,
      message: 'User statistics retrieved successfully',
      data: stats
    });

  } catch (error: any) {
    console.error('Error retrieving user stats:', error);
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to retrieve user statistics',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

export { router as userRoutes };

