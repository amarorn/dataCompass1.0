export interface MLDataRecord {
    _id?: string;
    csvId: string;
    filename: string;
    from: string;
    processedAt: Date;
    rowIndex: number;
    originalData: Record<string, any>;
    normalizedData: Record<string, any>;
    dataTypes: Record<string, 'numeric' | 'categorical' | 'text' | 'date' | 'boolean'>;
    features: {
        numericFeatures: string[];
        categoricalFeatures: string[];
        textFeatures: string[];
        dateFeatures: string[];
        booleanFeatures: string[];
    };
    metadata: {
        source: string;
        quality: {
            completeness: number;
            consistency: number;
            validity: number;
        };
        statistics?: Record<string, any>;
    };
}
export interface MLDatasetSummary {
    csvId: string;
    filename: string;
    totalRecords: number;
    features: {
        total: number;
        numeric: number;
        categorical: number;
        text: number;
        date: number;
        boolean: number;
    };
    dataQuality: {
        averageCompleteness: number;
        averageConsistency: number;
        averageValidity: number;
    };
    statistics: {
        numericStats: Record<string, {
            min: number;
            max: number;
            mean: number;
            median: number;
            std: number;
            nullCount: number;
        }>;
        categoricalStats: Record<string, {
            uniqueValues: number;
            topValues: Array<{
                value: any;
                count: number;
            }>;
            nullCount: number;
        }>;
    };
    createdAt: Date;
    updatedAt: Date;
}
export declare class MongoMLRepository {
    private connection;
    constructor();
    /**
     * Processar e salvar dados de CSV para análise de ML
     */
    processCSVForML(csvId: string, filename: string, from: string, csvData: any[]): Promise<string>;
    /**
     * Analisar estrutura dos dados
     */
    private analyzeDataStructure;
    /**
     * Detectar tipo de dados
     */
    private detectDataType;
    /**
     * Normalizar dados
     */
    private normalizeData;
    /**
     * Normalizar valores booleanos
     */
    private normalizeBoolean;
    /**
     * Calcular qualidade dos dados
     */
    private calculateDataQuality;
    /**
     * Verificar se valor é consistente com o tipo
     */
    private isValueConsistentWithType;
    /**
     * Criar resumo do dataset
     */
    private createDatasetSummary;
    /**
     * Calcular estatísticas numéricas
     */
    private calculateNumericStatistics;
    /**
     * Calcular estatísticas categóricas
     */
    private calculateCategoricalStatistics;
    /**
     * Buscar dados para ML por CSV ID
     */
    getMLDataByCSV(csvId: string): Promise<MLDataRecord[]>;
    /**
     * Buscar resumo do dataset
     */
    getDatasetSummary(csvId: string): Promise<MLDatasetSummary | null>;
    /**
     * Listar todos os datasets disponíveis
     */
    getAllDatasets(): Promise<MLDatasetSummary[]>;
}
//# sourceMappingURL=MongoMLRepository.d.ts.map