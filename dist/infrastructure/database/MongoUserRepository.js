"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MongoUserRepository = void 0;
const uuid_1 = require("uuid");
const User_1 = require("../../domain/entities/User");
class MongoUserRepository {
    constructor(db) {
        this.db = db;
        this.collection = db.collection('users');
        this.createIndexes();
    }
    async createIndexes() {
        try {
            // Criar índice único para email
            await this.collection.createIndex({ email: 1 }, { unique: true });
            // Criar índice para busca por role
            await this.collection.createIndex({ role: 1 });
            // Criar índice para busca por isActive
            await this.collection.createIndex({ isActive: 1 });
        }
        catch (error) {
            console.error('Error creating indexes:', error);
        }
    }
    async create(userData) {
        const now = new Date();
        const user = {
            id: (0, uuid_1.v4)(),
            email: userData.email.toLowerCase(),
            password: userData.password,
            name: userData.name,
            company: userData.company,
            phone: userData.phone,
            role: userData.role || User_1.UserRole.USER,
            isActive: true,
            emailVerified: false,
            createdAt: now,
            updatedAt: now,
            preferences: {
                language: 'pt-BR',
                timezone: 'America/Sao_Paulo',
                notifications: {
                    email: true,
                    whatsapp: true,
                    dashboard: true
                },
                dashboard: {
                    defaultView: 'overview',
                    autoRefresh: true
                }
            }
        };
        const result = await this.collection.insertOne(user);
        if (!result.acknowledged) {
            throw new Error('Failed to create user');
        }
        return user;
    }
    async findById(id) {
        const user = await this.collection.findOne({ id });
        return user || null;
    }
    async findByEmail(email) {
        const user = await this.collection.findOne({ email: email.toLowerCase() });
        return user || null;
    }
    async findAll(limit = 50, offset = 0) {
        const users = await this.collection
            .find({})
            .skip(offset)
            .limit(limit)
            .sort({ createdAt: -1 })
            .toArray();
        return users;
    }
    async update(id, userData) {
        const updateData = {
            ...userData,
            updatedAt: new Date()
        };
        const result = await this.collection.findOneAndUpdate({ id }, { $set: updateData }, { returnDocument: 'after' });
        return result || null;
    }
    async delete(id) {
        const result = await this.collection.deleteOne({ id });
        return result.deletedCount === 1;
    }
    async updateLastLogin(id) {
        await this.collection.updateOne({ id }, { $set: { lastLoginAt: new Date(), updatedAt: new Date() } });
    }
    async countUsers() {
        return await this.collection.countDocuments();
    }
    async findByRole(role) {
        const users = await this.collection
            .find({ role: role })
            .sort({ createdAt: -1 })
            .toArray();
        return users;
    }
    async updatePassword(id, hashedPassword) {
        const result = await this.collection.updateOne({ id }, {
            $set: {
                password: hashedPassword,
                updatedAt: new Date()
            }
        });
        return result.modifiedCount === 1;
    }
    async verifyEmail(id) {
        const result = await this.collection.updateOne({ id }, {
            $set: {
                emailVerified: true,
                updatedAt: new Date()
            }
        });
        return result.modifiedCount === 1;
    }
}
exports.MongoUserRepository = MongoUserRepository;
//# sourceMappingURL=MongoUserRepository.js.map