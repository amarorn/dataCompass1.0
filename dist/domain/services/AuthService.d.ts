import { User, CreateUserRequest, LoginRequest, LoginResponse, RegisterResponse } from '../entities/User';
import { IUserRepository } from '../repositories/IUserRepository';
export declare class AuthService {
    private userRepository;
    private jwtSecret;
    private jwtExpiresIn;
    constructor(userRepository: IUserRepository);
    register(userData: CreateUserRequest): Promise<RegisterResponse>;
    login(loginData: LoginRequest): Promise<LoginResponse>;
    verifyToken(token: string): Promise<User | null>;
    private generateToken;
    private getTokenExpirationTime;
    private validateRegistrationData;
    private isValidEmail;
    private isValidPhone;
}
//# sourceMappingURL=AuthService.d.ts.map