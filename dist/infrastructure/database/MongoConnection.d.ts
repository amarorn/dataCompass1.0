import { Db } from 'mongodb';
export declare class MongoConnection {
    private static instance;
    private client;
    private db;
    private constructor();
    static getInstance(): MongoConnection;
    connect(): Promise<Db>;
    disconnect(): Promise<void>;
    getDb(): Db;
    isConnected(): boolean;
    private extractDatabaseName;
    healthCheck(): Promise<{
        status: string;
        database: string;
        connected: boolean;
    }>;
}
//# sourceMappingURL=MongoConnection.d.ts.map