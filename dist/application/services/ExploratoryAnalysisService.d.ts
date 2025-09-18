export interface RawDataRecord {
    _id?: string;
    messageId: string;
    filename: string;
    from: string;
    processedAt: Date;
    rowIndex: number;
    originalData: Record<string, any>;
    normalizedData: Record<string, any>;
    dataTypes: Record<string, 'numeric' | 'categorical' | 'text' | 'date' | 'boolean'>;
    metadata: {
        source: string;
        quality: {
            completeness: number;
            consistency: number;
            validity: number;
        };
    };
}
export interface ExploratoryAnalysisResult {
    messageId: string;
    filename: string;
    from: string;
    totalRecords: number;
    analysisDate: Date;
    dataStructure: {
        totalColumns: number;
        columnTypes: Record<string, string>;
        featureDistribution: {
            numeric: string[];
            categorical: string[];
            text: string[];
            date: string[];
            boolean: string[];
        };
    };
    dataQuality: {
        overallScore: number;
        completeness: {
            score: number;
            missingValues: Record<string, number>;
            completenessPerColumn: Record<string, number>;
        };
        consistency: {
            score: number;
            inconsistentValues: Record<string, any[]>;
        };
        validity: {
            score: number;
            invalidValues: Record<string, number>;
        };
    };
    descriptiveStats: {
        numeric: Record<string, {
            count: number;
            mean: number;
            median: number;
            mode?: number;
            std: number;
            variance: number;
            min: number;
            max: number;
            q1: number;
            q3: number;
            iqr: number;
            skewness: number;
            kurtosis: number;
            outliers: number[];
        }>;
        categorical: Record<string, {
            count: number;
            uniqueValues: number;
            mostFrequent: {
                value: any;
                frequency: number;
            };
            leastFrequent: {
                value: any;
                frequency: number;
            };
            valueDistribution: Array<{
                value: any;
                count: number;
                percentage: number;
            }>;
            entropy: number;
        }>;
        text: Record<string, {
            count: number;
            avgLength: number;
            minLength: number;
            maxLength: number;
            uniqueValues: number;
            commonWords?: string[];
        }>;
        date: Record<string, {
            count: number;
            earliestDate: Date;
            latestDate: Date;
            dateRange: number;
            mostCommonPeriod?: string;
        }>;
    };
    relationships: {
        correlationMatrix?: Record<string, Record<string, number>>;
        strongCorrelations: Array<{
            feature1: string;
            feature2: string;
            correlation: number;
            type: 'positive' | 'negative';
        }>;
    };
    insights: {
        keyFindings: string[];
        dataQualityIssues: string[];
        recommendations: string[];
        potentialMLFeatures: string[];
        businessInsights: string[];
    };
    suggestedVisualizations: Array<{
        type: 'histogram' | 'boxplot' | 'scatter' | 'bar' | 'line' | 'heatmap';
        features: string[];
        description: string;
        priority: 'high' | 'medium' | 'low';
    }>;
}
export declare class ExploratoryAnalysisService {
    /**
     * Realizar análise exploratória completa dos dados
     */
    performExploratoryAnalysis(messageId: string, filename: string, from: string, rawData: any[]): Promise<ExploratoryAnalysisResult>;
    /**
     * Analisar estrutura dos dados
     */
    private analyzeDataStructure;
    /**
     * Detectar tipo de dados
     */
    private detectDataType;
    /**
     * Analisar qualidade dos dados
     */
    private analyzeDataQuality;
    /**
     * Verificar se valor é consistente com o tipo
     */
    private isValueConsistentWithType;
    /**
     * Verificar se valor é válido
     */
    private isValidValue;
    /**
     * Calcular estatísticas descritivas
     */
    private calculateDescriptiveStatistics;
    /**
     * Calcular skewness
     */
    private calculateSkewness;
    /**
     * Calcular kurtosis
     */
    private calculateKurtosis;
    /**
     * Calcular entropia
     */
    private calculateEntropy;
    /**
     * Analisar relacionamentos entre variáveis
     */
    private analyzeRelationships;
    /**
     * Calcular correlação de Pearson
     */
    private calculateCorrelation;
    /**
     * Gerar insights automáticos
     */
    private generateInsights;
    /**
     * Sugerir visualizações
     */
    private suggestVisualizations;
}
//# sourceMappingURL=ExploratoryAnalysisService.d.ts.map