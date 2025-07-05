export interface User {
    id: string;
    email: string;
    password: string;
    name: string;
    company?: string;
    phone?: string;
    role: UserRole;
    isActive: boolean;
    emailVerified: boolean;
    createdAt: Date;
    updatedAt: Date;
    lastLoginAt?: Date;
    preferences?: UserPreferences;
}
export declare enum UserRole {
    ADMIN = "admin",
    USER = "user",
    MANAGER = "manager"
}
export interface UserPreferences {
    language: string;
    timezone: string;
    notifications: {
        email: boolean;
        whatsapp: boolean;
        dashboard: boolean;
    };
    dashboard: {
        defaultView: string;
        autoRefresh: boolean;
    };
}
export interface CreateUserRequest {
    email: string;
    password: string;
    name: string;
    company?: string;
    phone?: string;
    role?: UserRole;
}
export interface LoginRequest {
    email: string;
    password: string;
}
export interface LoginResponse {
    success: boolean;
    message: string;
    data?: {
        user: Omit<User, 'password'>;
        token: string;
        expiresIn: number;
    };
    error?: {
        message: string;
        statusCode: number;
    };
}
export interface RegisterResponse {
    success: boolean;
    message: string;
    data?: {
        user: Omit<User, 'password'>;
        token: string;
    };
    error?: {
        message: string;
        statusCode: number;
        details?: string[];
    };
}
//# sourceMappingURL=User.d.ts.map