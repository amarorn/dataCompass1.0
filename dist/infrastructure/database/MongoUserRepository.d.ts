import { Db } from 'mongodb';
import { User, CreateUserRequest } from '../../domain/entities/User';
import { IUserRepository } from '../../domain/repositories/IUserRepository';
export declare class MongoUserRepository implements IUserRepository {
    private db;
    private collection;
    constructor(db: Db);
    private createIndexes;
    create(userData: CreateUserRequest): Promise<User>;
    findById(id: string): Promise<User | null>;
    findByEmail(email: string): Promise<User | null>;
    findAll(limit?: number, offset?: number): Promise<User[]>;
    update(id: string, userData: Partial<User>): Promise<User | null>;
    delete(id: string): Promise<boolean>;
    updateLastLogin(id: string): Promise<void>;
    countUsers(): Promise<number>;
    findByRole(role: string): Promise<User[]>;
    updatePassword(id: string, hashedPassword: string): Promise<boolean>;
    verifyEmail(id: string): Promise<boolean>;
}
//# sourceMappingURL=MongoUserRepository.d.ts.map