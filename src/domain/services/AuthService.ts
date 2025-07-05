import bcrypt from 'bcryptjs';
import jwt, { SignOptions } from 'jsonwebtoken';
import { User, CreateUserRequest, LoginRequest, LoginResponse, RegisterResponse, UserRole } from '../entities/User';
import { IUserRepository } from '../repositories/IUserRepository';

export class AuthService {
  private userRepository: IUserRepository;
  private jwtSecret: string;
  private jwtExpiresIn: string;

  constructor(userRepository: IUserRepository) {
    this.userRepository = userRepository;
    this.jwtSecret = process.env.JWT_SECRET || 'your-jwt-secret-here';
    this.jwtExpiresIn = process.env.JWT_EXPIRES_IN || '7d';
  }

  async register(userData: CreateUserRequest): Promise<RegisterResponse> {
    try {
      // Validar dados de entrada
      const validation = this.validateRegistrationData(userData);
      if (!validation.isValid) {
        return {
          success: false,
          message: 'Dados de registro inválidos',
          error: {
            message: 'Validation failed',
            statusCode: 400,
            details: validation.errors
          }
        };
      }

      // Verificar se o email já existe
      const existingUser = await this.userRepository.findByEmail(userData.email);
      if (existingUser) {
        return {
          success: false,
          message: 'Email já está em uso',
          error: {
            message: 'Email already exists',
            statusCode: 409
          }
        };
      }

      // Hash da senha
      const hashedPassword = await bcrypt.hash(userData.password, 12);

      // Criar usuário
      const newUser = await this.userRepository.create({
        ...userData,
        password: hashedPassword,
        role: userData.role || UserRole.USER
      });

      // Gerar token JWT
      const token = this.generateToken(newUser);

      // Remover senha da resposta
      const { password, ...userWithoutPassword } = newUser;

      return {
        success: true,
        message: 'Usuário registrado com sucesso',
        data: {
          user: userWithoutPassword,
          token
        }
      };

    } catch (error: any) {
      console.error('Error in register:', error);
      return {
        success: false,
        message: 'Erro interno do servidor',
        error: {
          message: 'Internal server error',
          statusCode: 500
        }
      };
    }
  }

  async login(loginData: LoginRequest): Promise<LoginResponse> {
    try {
      // Validar dados de entrada
      if (!loginData.email || !loginData.password) {
        return {
          success: false,
          message: 'Email e senha são obrigatórios',
          error: {
            message: 'Missing required fields',
            statusCode: 400
          }
        };
      }

      // Buscar usuário por email
      const user = await this.userRepository.findByEmail(loginData.email);
      if (!user) {
        return {
          success: false,
          message: 'Credenciais inválidas',
          error: {
            message: 'Invalid credentials',
            statusCode: 401
          }
        };
      }

      // Verificar se o usuário está ativo
      if (!user.isActive) {
        return {
          success: false,
          message: 'Conta desativada',
          error: {
            message: 'Account deactivated',
            statusCode: 401
          }
        };
      }

      // Verificar senha
      const isPasswordValid = await bcrypt.compare(loginData.password, user.password);
      if (!isPasswordValid) {
        return {
          success: false,
          message: 'Credenciais inválidas',
          error: {
            message: 'Invalid credentials',
            statusCode: 401
          }
        };
      }

      // Atualizar último login
      await this.userRepository.updateLastLogin(user.id);

      // Gerar token JWT
      const token = this.generateToken(user);
      const expiresIn = this.getTokenExpirationTime();

      // Remover senha da resposta
      const { password, ...userWithoutPassword } = user;

      return {
        success: true,
        message: 'Login realizado com sucesso',
        data: {
          user: userWithoutPassword,
          token,
          expiresIn
        }
      };

    } catch (error: any) {
      console.error('Error in login:', error);
      return {
        success: false,
        message: 'Erro interno do servidor',
        error: {
          message: 'Internal server error',
          statusCode: 500
        }
      };
    }
  }

  async verifyToken(token: string): Promise<User | null> {
    try {
      const decoded = jwt.verify(token, this.jwtSecret) as any;
      const user = await this.userRepository.findById(decoded.userId);
      
      if (!user || !user.isActive) {
        return null;
      }

      return user;
    } catch (error) {
      return null;
    }
  }

  private generateToken(user: User): string {
    const payload = {
      userId: user.id,
      email: user.email,
      role: user.role
    };
    
    return jwt.sign(payload, this.jwtSecret as string, { expiresIn: '7d' });
  }

  private getTokenExpirationTime(): number {
    // Retorna tempo de expiração em segundos
    const expiresIn = this.jwtExpiresIn;
    if (expiresIn.endsWith('d')) {
      return parseInt(expiresIn) * 24 * 60 * 60;
    } else if (expiresIn.endsWith('h')) {
      return parseInt(expiresIn) * 60 * 60;
    } else if (expiresIn.endsWith('m')) {
      return parseInt(expiresIn) * 60;
    }
    return 7 * 24 * 60 * 60; // 7 dias por padrão
  }

  private validateRegistrationData(userData: CreateUserRequest): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Validar email
    if (!userData.email) {
      errors.push('Email é obrigatório');
    } else if (!this.isValidEmail(userData.email)) {
      errors.push('Email deve ter um formato válido');
    }

    // Validar senha
    if (!userData.password) {
      errors.push('Senha é obrigatória');
    } else if (userData.password.length < 6) {
      errors.push('Senha deve ter pelo menos 6 caracteres');
    }

    // Validar nome
    if (!userData.name) {
      errors.push('Nome é obrigatório');
    } else if (userData.name.length < 2) {
      errors.push('Nome deve ter pelo menos 2 caracteres');
    }

    // Validar telefone (se fornecido)
    if (userData.phone && !this.isValidPhone(userData.phone)) {
      errors.push('Telefone deve ter um formato válido (+5511999999999)');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  private isValidPhone(phone: string): boolean {
    const phoneRegex = /^\+[1-9]\d{1,14}$/;
    return phoneRegex.test(phone);
  }
}

