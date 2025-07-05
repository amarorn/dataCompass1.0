"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AuthService = void 0;
const bcryptjs_1 = __importDefault(require("bcryptjs"));
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const User_1 = require("../entities/User");
class AuthService {
    constructor(userRepository) {
        this.userRepository = userRepository;
        this.jwtSecret = process.env.JWT_SECRET || 'your-jwt-secret-here';
        this.jwtExpiresIn = process.env.JWT_EXPIRES_IN || '7d';
    }
    async register(userData) {
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
            const hashedPassword = await bcryptjs_1.default.hash(userData.password, 12);
            // Criar usuário
            const newUser = await this.userRepository.create({
                ...userData,
                password: hashedPassword,
                role: userData.role || User_1.UserRole.USER
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
        }
        catch (error) {
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
    async login(loginData) {
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
            const isPasswordValid = await bcryptjs_1.default.compare(loginData.password, user.password);
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
        }
        catch (error) {
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
    async verifyToken(token) {
        try {
            const decoded = jsonwebtoken_1.default.verify(token, this.jwtSecret);
            const user = await this.userRepository.findById(decoded.userId);
            if (!user || !user.isActive) {
                return null;
            }
            return user;
        }
        catch (error) {
            return null;
        }
    }
    generateToken(user) {
        const payload = {
            userId: user.id,
            email: user.email,
            role: user.role
        };
        return jsonwebtoken_1.default.sign(payload, this.jwtSecret, { expiresIn: '7d' });
    }
    getTokenExpirationTime() {
        // Retorna tempo de expiração em segundos
        const expiresIn = this.jwtExpiresIn;
        if (expiresIn.endsWith('d')) {
            return parseInt(expiresIn) * 24 * 60 * 60;
        }
        else if (expiresIn.endsWith('h')) {
            return parseInt(expiresIn) * 60 * 60;
        }
        else if (expiresIn.endsWith('m')) {
            return parseInt(expiresIn) * 60;
        }
        return 7 * 24 * 60 * 60; // 7 dias por padrão
    }
    validateRegistrationData(userData) {
        const errors = [];
        // Validar email
        if (!userData.email) {
            errors.push('Email é obrigatório');
        }
        else if (!this.isValidEmail(userData.email)) {
            errors.push('Email deve ter um formato válido');
        }
        // Validar senha
        if (!userData.password) {
            errors.push('Senha é obrigatória');
        }
        else if (userData.password.length < 6) {
            errors.push('Senha deve ter pelo menos 6 caracteres');
        }
        // Validar nome
        if (!userData.name) {
            errors.push('Nome é obrigatório');
        }
        else if (userData.name.length < 2) {
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
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    isValidPhone(phone) {
        const phoneRegex = /^\+[1-9]\d{1,14}$/;
        return phoneRegex.test(phone);
    }
}
exports.AuthService = AuthService;
//# sourceMappingURL=AuthService.js.map