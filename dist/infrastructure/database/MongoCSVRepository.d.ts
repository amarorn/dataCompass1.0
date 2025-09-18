export interface ProcessedCSVDocument {
    _id?: string;
    id: string;
    filename: string;
    from: string;
    processedAt: Date;
    data: any[];
    summary: {
        rows: number;
        columns: string[];
        insights: string[];
    };
    analysis?: any;
}
export declare class MongoCSVRepository {
    private connection;
    constructor();
    /**
     * Salvar CSV processado no MongoDB
     */
    saveProcessedCSV(csvData: Omit<ProcessedCSVDocument, '_id'>): Promise<string>;
    /**
     * Buscar todos os CSVs processados
     */
    getAllProcessedCSVs(from?: string): Promise<ProcessedCSVDocument[]>;
    /**
     * Buscar CSV específico por ID
     */
    getProcessedCSVById(id: string): Promise<ProcessedCSVDocument | null>;
    /**
     * Atualizar análise de um CSV
     */
    updateCSVAnalysis(id: string, analysis: any): Promise<boolean>;
    /**
     * Deletar CSV processado
     */
    deleteProcessedCSV(id: string): Promise<boolean>;
    /**
     * Obter estatísticas dos CSVs
     */
    getCSVStats(): Promise<{
        totalCSVs: number;
        totalRows: number;
        totalUsers: number;
        lastProcessed: Date | null;
    }>;
}
//# sourceMappingURL=MongoCSVRepository.d.ts.map