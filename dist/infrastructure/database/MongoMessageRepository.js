"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MongoMessageRepository = void 0;
const MongoConnection_1 = require("./MongoConnection");
class MongoMessageRepository {
    constructor() {
        this.connection = MongoConnection_1.MongoConnection.getInstance();
    }
    /**
     * Adicionar mensagem ao histórico
     */
    async addToHistory(messageData) {
        try {
            await this.connection.connect();
            const db = this.connection.getDb();
            const collection = db.collection('message_history');
            const document = {
                ...messageData,
                timestamp: new Date(messageData.timestamp)
            };
            delete document._id;
            const result = await collection.insertOne(document);
            console.log(`📝 Message added to MongoDB history (${messageData.type}): ${messageData.message}`);
            return result.insertedId.toString();
        }
        catch (error) {
            console.error('❌ Error saving message to MongoDB:', error);
            throw error;
        }
    }
    /**
     * Buscar histórico completo
     */
    async getHistory() {
        try {
            await this.connection.connect();
            const db = this.connection.getDb();
            const collection = db.collection('message_history');
            const messages = await collection
                .find({})
                .sort({ timestamp: -1 })
                .toArray();
            return messages.map((msg) => ({
                ...msg,
                _id: msg._id.toString()
            }));
        }
        catch (error) {
            console.error('❌ Error fetching message history from MongoDB:', error);
            return [];
        }
    }
    /**
     * Buscar mensagens recebidas
     */
    async getReceivedMessages() {
        try {
            await this.connection.connect();
            const db = this.connection.getDb();
            const collection = db.collection('message_history');
            const messages = await collection
                .find({ type: 'received' })
                .sort({ timestamp: -1 })
                .toArray();
            return messages.map((msg) => ({
                ...msg,
                _id: msg._id.toString()
            }));
        }
        catch (error) {
            console.error('❌ Error fetching received messages from MongoDB:', error);
            return [];
        }
    }
    /**
     * Buscar mensagens enviadas
     */
    async getSentMessages() {
        try {
            await this.connection.connect();
            const db = this.connection.getDb();
            const collection = db.collection('message_history');
            const messages = await collection
                .find({ type: 'sent' })
                .sort({ timestamp: -1 })
                .toArray();
            return messages.map((msg) => ({
                ...msg,
                _id: msg._id.toString()
            }));
        }
        catch (error) {
            console.error('❌ Error fetching sent messages from MongoDB:', error);
            return [];
        }
    }
    /**
     * Buscar mensagens de um usuário específico
     */
    async getUserMessages(phoneNumber) {
        try {
            await this.connection.connect();
            const db = this.connection.getDb();
            const collection = db.collection('message_history');
            const messages = await collection
                .find({
                $or: [
                    { from: phoneNumber },
                    { from: `55${phoneNumber}` },
                    { to: phoneNumber },
                    { to: `55${phoneNumber}` }
                ]
            })
                .sort({ timestamp: -1 })
                .toArray();
            return messages.map((msg) => ({
                ...msg,
                _id: msg._id.toString()
            }));
        }
        catch (error) {
            console.error('❌ Error fetching user messages from MongoDB:', error);
            return [];
        }
    }
    /**
     * Obter estatísticas das mensagens
     */
    async getMessageStats() {
        try {
            await this.connection.connect();
            const db = this.connection.getDb();
            const collection = db.collection('message_history');
            const stats = await collection.aggregate([
                {
                    $group: {
                        _id: '$type',
                        count: { $sum: 1 },
                        lastMessage: { $max: '$timestamp' }
                    }
                }
            ]).toArray();
            const result = {
                total: 0,
                received: 0,
                sent: 0,
                lastReceived: null,
                lastSent: null
            };
            stats.forEach((stat) => {
                result.total += stat.count;
                if (stat._id === 'received') {
                    result.received = stat.count;
                    result.lastReceived = stat.lastMessage;
                }
                else if (stat._id === 'sent') {
                    result.sent = stat.count;
                    result.lastSent = stat.lastMessage;
                }
            });
            return result;
        }
        catch (error) {
            console.error('❌ Error getting message stats from MongoDB:', error);
            return {
                total: 0,
                received: 0,
                sent: 0,
                lastReceived: null,
                lastSent: null
            };
        }
    }
    /**
     * Limpar mensagens antigas (mais de X dias)
     */
    async cleanOldMessages(daysToKeep = 30) {
        try {
            await this.connection.connect();
            const db = this.connection.getDb();
            const collection = db.collection('message_history');
            const cutoffDate = new Date();
            cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);
            const result = await collection.deleteMany({
                timestamp: { $lt: cutoffDate }
            });
            console.log(`🧹 Cleaned ${result.deletedCount} old messages (older than ${daysToKeep} days)`);
            return result.deletedCount;
        }
        catch (error) {
            console.error('❌ Error cleaning old messages from MongoDB:', error);
            return 0;
        }
    }
}
exports.MongoMessageRepository = MongoMessageRepository;
//# sourceMappingURL=MongoMessageRepository.js.map