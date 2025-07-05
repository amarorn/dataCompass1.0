import { MongoClient, Db, Collection } from 'mongodb';
import { v4 as uuidv4 } from 'uuid';
import { User, CreateUserRequest, UserRole } from '../../domain/entities/User';
import { IUserRepository } from '../../domain/repositories/IUserRepository';

export class MongoUserRepository implements IUserRepository {
  private db: Db;
  private collection: Collection<User>;

  constructor(db: Db) {
    this.db = db;
    this.collection = db.collection<User>('users');
    this.createIndexes();
  }

  private async createIndexes(): Promise<void> {
    try {
      // Criar índice único para email
      await this.collection.createIndex({ email: 1 }, { unique: true });
      // Criar índice para busca por role
      await this.collection.createIndex({ role: 1 });
      // Criar índice para busca por isActive
      await this.collection.createIndex({ isActive: 1 });
    } catch (error) {
      console.error('Error creating indexes:', error);
    }
  }

  async create(userData: CreateUserRequest): Promise<User> {
    const now = new Date();
    const user: User = {
      id: uuidv4(),
      email: userData.email.toLowerCase(),
      password: userData.password,
      name: userData.name,
      company: userData.company,
      phone: userData.phone,
      role: userData.role || UserRole.USER,
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

  async findById(id: string): Promise<User | null> {
    const user = await this.collection.findOne({ id });
    return user || null;
  }

  async findByEmail(email: string): Promise<User | null> {
    const user = await this.collection.findOne({ email: email.toLowerCase() });
    return user || null;
  }

  async findAll(limit: number = 50, offset: number = 0): Promise<User[]> {
    const users = await this.collection
      .find({})
      .skip(offset)
      .limit(limit)
      .sort({ createdAt: -1 })
      .toArray();
    
    return users;
  }

  async update(id: string, userData: Partial<User>): Promise<User | null> {
    const updateData = {
      ...userData,
      updatedAt: new Date()
    };

    const result = await this.collection.findOneAndUpdate(
      { id },
      { $set: updateData },
      { returnDocument: 'after' }
    );

    return result || null;
  }

  async delete(id: string): Promise<boolean> {
    const result = await this.collection.deleteOne({ id });
    return result.deletedCount === 1;
  }

  async updateLastLogin(id: string): Promise<void> {
    await this.collection.updateOne(
      { id },
      { $set: { lastLoginAt: new Date(), updatedAt: new Date() } }
    );
  }

  async countUsers(): Promise<number> {
    return await this.collection.countDocuments();
  }

  async findByRole(role: string): Promise<User[]> {
    const users = await this.collection
      .find({ role: role as UserRole })
      .sort({ createdAt: -1 })
      .toArray();
    
    return users;
  }

  async updatePassword(id: string, hashedPassword: string): Promise<boolean> {
    const result = await this.collection.updateOne(
      { id },
      { 
        $set: { 
          password: hashedPassword,
          updatedAt: new Date()
        }
      }
    );

    return result.modifiedCount === 1;
  }

  async verifyEmail(id: string): Promise<boolean> {
    const result = await this.collection.updateOne(
      { id },
      { 
        $set: { 
          emailVerified: true,
          updatedAt: new Date()
        }
      }
    );

    return result.modifiedCount === 1;
  }
}

