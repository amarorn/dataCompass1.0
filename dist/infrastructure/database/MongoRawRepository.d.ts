import { RawDataRecord, ExploratoryAnalysisResult } from '../../application/services/ExploratoryAnalysisService';
export declare class MongoRawRepository {
    private connection;
    constructor();
    /**
     * Salvar dados brutos vinculados ao ID da mensagem
     */
    saveRawData(messageId: string, filename: string, from: string, csvData: any[]): Promise<string>;
    /**
     * Buscar dados brutos por ID da mensagem
     */
    getRawDataByMessageId(messageId: string): Promise<RawDataRecord[]>;
    /**
     * Listar todas as mensagens com dados brutos
     */
    getAllRawDataMessages(): Promise<Array<{
        messageId: string;
        filename: string;
        from: string;
        processedAt: Date;
        recordCount: number;
    }>>;
    /**
     * Salvar resultado de análise exploratória
     */
    saveExploratoryAnalysis(analysis: ExploratoryAnalysisResult): Promise<void>;
    /**
     * Buscar análise exploratória por ID da mensagem
     */
    getExploratoryAnalysisByMessageId(messageId: string): Promise<ExploratoryAnalysisResult | null>;
    /**
     * Listar todas as análises exploratórias
     */
    getAllExploratoryAnalyses(): Promise<Array<{
        messageId: string;
        filename: string;
        from: string;
        totalRecords: number;
        analysisDate: Date;
        overallQuality: number;
    }>>;
    /**
     * Deletar dados brutos por ID da mensagem
     */
    deleteRawDataByMessageId(messageId: string): Promise<number>;
    /**
     * Obter estatísticas gerais da coleção raw
     */
    getRawDataStats(): Promise<{
        totalMessages: number;
        totalRecords: number;
        totalSize: number;
        oldestRecord: Date | null;
        newestRecord: Date | null;
        topSenders: Array<{
            from: string;
            messageCount: number;
            recordCount: number;
        }>;
    }>;
    /**
     * Analisar estrutura dos dados (método auxiliar)
     */
    private analyzeDataStructure;
    /**
     * Detectar tipo de dados (método auxiliar)
     */
    private detectDataType;
    /**
     * Normalizar dados (método auxiliar)
     */
    private normalizeData;
    /**
     * Normalizar valores booleanos (método auxiliar)
     */
    private normalizeBoolean;
    /**
     * Calcular qualidade dos dados (método auxiliar)
     */
    private calculateDataQuality;
    /**
     * Verificar se valor é consistente com o tipo (método auxiliar)
     */
    private isValueConsistentWithType;
}
//# sourceMappingURL=MongoRawRepository.d.ts.map