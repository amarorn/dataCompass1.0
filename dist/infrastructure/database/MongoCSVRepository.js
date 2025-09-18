"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MongoCSVRepository = void 0;
const MongoConnection_1 = require("./MongoConnection");
class MongoCSVRepository {
    constructor() {
        this.connection = MongoConnection_1.MongoConnection.getInstance();
    }
    /**
     * Salvar CSV processado no MongoDB
     */
    async saveProcessedCSV(csvData) {
        try {
            await this.connection.connect();
            const db = this.connection.getDb();
            const collection = db.collection('processed_csvs');
            const document = {
                ...csvData,
                processedAt: new Date(csvData.processedAt)
            };
            delete document._id;
            const result = await collection.insertOne(document);
            console.log('✅ CSV saved to MongoDB:', result.insertedId);
            return result.insertedId.toString();
        }
        catch (error) {
            console.error('❌ Error saving CSV to MongoDB:', error);
            throw error;
        }
    }
    /**
     * Buscar todos os CSVs processados
     */
    async getAllProcessedCSVs(from) {
        try {
            await this.connection.connect();
            const db = this.connection.getDb();
            const collection = db.collection('processed_csvs');
            const filter = from ? { from } : {};
            const csvs = await collection
                .find(filter)
                .sort({ processedAt: -1 })
                .toArray();
            return csvs.map((csv) => ({
                ...csv,
                _id: csv._id.toString()
            }));
        }
        catch (error) {
            console.error('❌ Error fetching CSVs from MongoDB:', error);
            return [];
        }
    }
    /**
     * Buscar CSV específico por ID
     */
    async getProcessedCSVById(id) {
        try {
            await this.connection.connect();
            const db = this.connection.getDb();
            const collection = db.collection('processed_csvs');
            const csv = await collection.findOne({ id });
            if (!csv)
                return null;
            return {
                ...csv,
                _id: csv._id.toString()
            };
        }
        catch (error) {
            console.error('❌ Error fetching CSV by ID from MongoDB:', error);
            return null;
        }
    }
    /**
     * Atualizar análise de um CSV
     */
    async updateCSVAnalysis(id, analysis) {
        try {
            await this.connection.connect();
            const db = this.connection.getDb();
            const collection = db.collection('processed_csvs');
            const result = await collection.updateOne({ id }, { $set: { analysis, updatedAt: new Date() } });
            return result.modifiedCount > 0;
        }
        catch (error) {
            console.error('❌ Error updating CSV analysis in MongoDB:', error);
            return false;
        }
    }
    /**
     * Deletar CSV processado
     */
    async deleteProcessedCSV(id) {
        try {
            await this.connection.connect();
            const db = this.connection.getDb();
            const collection = db.collection('processed_csvs');
            const result = await collection.deleteOne({ id });
            return result.deletedCount > 0;
        }
        catch (error) {
            console.error('❌ Error deleting CSV from MongoDB:', error);
            return false;
        }
    }
    /**
     * Obter estatísticas dos CSVs
     */
    async getCSVStats() {
        try {
            await this.connection.connect();
            const db = this.connection.getDb();
            const collection = db.collection('processed_csvs');
            const stats = await collection.aggregate([
                {
                    $group: {
                        _id: null,
                        totalCSVs: { $sum: 1 },
                        totalRows: { $sum: '$summary.rows' },
                        uniqueUsers: { $addToSet: '$from' },
                        lastProcessed: { $max: '$processedAt' }
                    }
                },
                {
                    $project: {
                        _id: 0,
                        totalCSVs: 1,
                        totalRows: 1,
                        totalUsers: { $size: '$uniqueUsers' },
                        lastProcessed: 1
                    }
                }
            ]).toArray();
            if (stats.length === 0) {
                return {
                    totalCSVs: 0,
                    totalRows: 0,
                    totalUsers: 0,
                    lastProcessed: null
                };
            }
            return stats[0];
        }
        catch (error) {
            console.error('❌ Error getting CSV stats from MongoDB:', error);
            return {
                totalCSVs: 0,
                totalRows: 0,
                totalUsers: 0,
                lastProcessed: null
            };
        }
    }
}
exports.MongoCSVRepository = MongoCSVRepository;
//# sourceMappingURL=MongoCSVRepository.js.map