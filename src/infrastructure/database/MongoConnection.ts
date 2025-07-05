import { MongoClient, Db } from 'mongodb';

export class MongoConnection {
  private static instance: MongoConnection;
  private client: MongoClient | null = null;
  private db: Db | null = null;

  private constructor() {}

  public static getInstance(): MongoConnection {
    if (!MongoConnection.instance) {
      MongoConnection.instance = new MongoConnection();
    }
    return MongoConnection.instance;
  }

  public async connect(): Promise<Db> {
    if (this.db) {
      return this.db;
    }

    try {
      const mongoUrl = process.env.DATABASE_URL || 'mongodb://localhost:27017/datacompass';
      
      console.log('🔌 Connecting to MongoDB...');
      
      this.client = new MongoClient(mongoUrl, {
        maxPoolSize: 10,
        serverSelectionTimeoutMS: 5000,
        socketTimeoutMS: 45000,
      });

      await this.client.connect();
      
      // Extrair nome do banco da URL ou usar padrão
      const dbName = this.extractDatabaseName(mongoUrl);
      this.db = this.client.db(dbName);

      console.log(`✅ Connected to MongoDB database: ${dbName}`);
      
      // Testar conexão
      await this.db.admin().ping();
      console.log('🏓 MongoDB ping successful');

      return this.db;
    } catch (error) {
      console.error('❌ MongoDB connection error:', error);
      throw new Error(`Failed to connect to MongoDB: ${error}`);
    }
  }

  public async disconnect(): Promise<void> {
    if (this.client) {
      await this.client.close();
      this.client = null;
      this.db = null;
      console.log('🔌 Disconnected from MongoDB');
    }
  }

  public getDb(): Db {
    if (!this.db) {
      throw new Error('MongoDB not connected. Call connect() first.');
    }
    return this.db;
  }

  public isConnected(): boolean {
    return this.db !== null;
  }

  private extractDatabaseName(url: string): string {
    try {
      // Extrair nome do banco da URL
      const urlParts = url.split('/');
      const dbNameWithParams = urlParts[urlParts.length - 1];
      const dbName = dbNameWithParams.split('?')[0];
      
      return dbName || 'datacompass';
    } catch (error) {
      console.warn('Could not extract database name from URL, using default');
      return 'datacompass';
    }
  }

  public async healthCheck(): Promise<{ status: string; database: string; connected: boolean }> {
    try {
      if (!this.db) {
        return {
          status: 'disconnected',
          database: 'unknown',
          connected: false
        };
      }

      await this.db.admin().ping();
      
      return {
        status: 'connected',
        database: this.db.databaseName,
        connected: true
      };
    } catch (error) {
      return {
        status: 'error',
        database: this.db?.databaseName || 'unknown',
        connected: false
      };
    }
  }
}

