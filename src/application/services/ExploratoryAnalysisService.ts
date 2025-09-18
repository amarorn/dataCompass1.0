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
  
  // Estrutura dos dados
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
  
  // Qualidade dos dados
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
  
  // Estatísticas descritivas
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
      mostFrequent: { value: any; frequency: number };
      leastFrequent: { value: any; frequency: number };
      valueDistribution: Array<{ value: any; count: number; percentage: number }>;
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
      dateRange: number; // em dias
      mostCommonPeriod?: string;
    }>;
  };
  
  // Correlações e relacionamentos
  relationships: {
    correlationMatrix?: Record<string, Record<string, number>>;
    strongCorrelations: Array<{
      feature1: string;
      feature2: string;
      correlation: number;
      type: 'positive' | 'negative';
    }>;
  };
  
  // Insights automáticos
  insights: {
    keyFindings: string[];
    dataQualityIssues: string[];
    recommendations: string[];
    potentialMLFeatures: string[];
    businessInsights: string[];
  };
  
  // Visualizações sugeridas
  suggestedVisualizations: Array<{
    type: 'histogram' | 'boxplot' | 'scatter' | 'bar' | 'line' | 'heatmap';
    features: string[];
    description: string;
    priority: 'high' | 'medium' | 'low';
  }>;
}

export class ExploratoryAnalysisService {
  
  /**
   * Realizar análise exploratória completa dos dados
   */
  async performExploratoryAnalysis(
    messageId: string,
    filename: string,
    from: string,
    rawData: any[]
  ): Promise<ExploratoryAnalysisResult> {
    console.log(`🔍 Iniciando análise exploratória para ${filename} (${rawData.length} registros)`);
    
    const analysisDate = new Date();
    
    // 1. Análise da estrutura dos dados
    const dataStructure = this.analyzeDataStructure(rawData);
    
    // 2. Análise de qualidade dos dados
    const dataQuality = this.analyzeDataQuality(rawData, dataStructure.columnTypes);
    
    // 3. Estatísticas descritivas
    const descriptiveStats = this.calculateDescriptiveStatistics(rawData, dataStructure);
    
    // 4. Análise de relacionamentos
    const relationships = this.analyzeRelationships(rawData, dataStructure);
    
    // 5. Gerar insights automáticos
    const insights = this.generateInsights(rawData, dataStructure, dataQuality, descriptiveStats);
    
    // 6. Sugerir visualizações
    const suggestedVisualizations = this.suggestVisualizations(dataStructure, descriptiveStats);
    
    const result: ExploratoryAnalysisResult = {
      messageId,
      filename,
      from,
      totalRecords: rawData.length,
      analysisDate,
      dataStructure,
      dataQuality,
      descriptiveStats,
      relationships,
      insights,
      suggestedVisualizations
    };
    
    console.log(`✅ Análise exploratória concluída para ${filename}`);
    return result;
  }
  
  /**
   * Analisar estrutura dos dados
   */
  private analyzeDataStructure(data: any[]): ExploratoryAnalysisResult['dataStructure'] {
    if (data.length === 0) {
      return {
        totalColumns: 0,
        columnTypes: {},
        featureDistribution: {
          numeric: [],
          categorical: [],
          text: [],
          date: [],
          boolean: []
        }
      };
    }
    
    const columns = Object.keys(data[0]);
    const columnTypes: Record<string, string> = {};
    const featureDistribution = {
      numeric: [] as string[],
      categorical: [] as string[],
      text: [] as string[],
      date: [] as string[],
      boolean: [] as string[]
    };
    
    columns.forEach(column => {
      const values = data.map(row => row[column]).filter(val => val != null && val !== '');
      const dataType = this.detectDataType(values);
      
      columnTypes[column] = dataType;
      featureDistribution[dataType].push(column);
    });
    
    return {
      totalColumns: columns.length,
      columnTypes,
      featureDistribution
    };
  }
  
  /**
   * Detectar tipo de dados
   */
  private detectDataType(values: any[]): 'numeric' | 'categorical' | 'text' | 'date' | 'boolean' {
    if (values.length === 0) return 'text';
    
    // Verificar se é booleano
    const booleanValues = values.filter(val => 
      typeof val === 'boolean' || 
      ['true', 'false', '1', '0', 'sim', 'não', 'yes', 'no'].includes(String(val).toLowerCase())
    );
    if (booleanValues.length > values.length * 0.8) return 'boolean';
    
    // Verificar se é numérico
    const numericValues = values.filter(val => !isNaN(parseFloat(val)) && isFinite(val));
    if (numericValues.length > values.length * 0.8) return 'numeric';
    
    // Verificar se é data
    const dateValues = values.filter(val => {
      const dateTest = new Date(val);
      return !isNaN(dateTest.getTime()) && String(val).match(/\d{4}|\d{2}\/\d{2}|\d{2}-\d{2}/);
    });
    if (dateValues.length > values.length * 0.6) return 'date';
    
    // Verificar se é categórico (poucos valores únicos)
    const uniqueValues = new Set(values).size;
    const uniqueRatio = uniqueValues / values.length;
    
    if (uniqueRatio < 0.1 && uniqueValues < 50) return 'categorical';
    
    return 'text';
  }
  
  /**
   * Analisar qualidade dos dados
   */
  private analyzeDataQuality(
    data: any[], 
    columnTypes: Record<string, string>
  ): ExploratoryAnalysisResult['dataQuality'] {
    const columns = Object.keys(columnTypes);
    const totalCells = data.length * columns.length;
    
    // Completude
    const missingValues: Record<string, number> = {};
    const completenessPerColumn: Record<string, number> = {};
    let totalMissing = 0;
    
    columns.forEach(column => {
      const missing = data.filter(row => row[column] == null || row[column] === '').length;
      missingValues[column] = missing;
      completenessPerColumn[column] = (data.length - missing) / data.length;
      totalMissing += missing;
    });
    
    const completenessScore = (totalCells - totalMissing) / totalCells;
    
    // Consistência
    const inconsistentValues: Record<string, any[]> = {};
    let consistencyIssues = 0;
    
    columns.forEach(column => {
      const expectedType = columnTypes[column];
      const inconsistent: any[] = [];
      
      data.forEach(row => {
        const value = row[column];
        if (value != null && value !== '' && !this.isValueConsistentWithType(value, expectedType)) {
          inconsistent.push(value);
          consistencyIssues++;
        }
      });
      
      if (inconsistent.length > 0) {
        inconsistentValues[column] = [...new Set(inconsistent)].slice(0, 10); // Top 10 inconsistentes
      }
    });
    
    const consistencyScore = Math.max(0, (totalCells - totalMissing - consistencyIssues) / (totalCells - totalMissing));
    
    // Validade
    const invalidValues: Record<string, number> = {};
    let totalInvalid = 0;
    
    columns.forEach(column => {
      const invalid = data.filter(row => {
        const value = row[column];
        return value != null && value !== '' && !this.isValidValue(value, columnTypes[column]);
      }).length;
      
      invalidValues[column] = invalid;
      totalInvalid += invalid;
    });
    
    const validityScore = (totalCells - totalMissing - totalInvalid) / (totalCells - totalMissing);
    
    const overallScore = (completenessScore + consistencyScore + validityScore) / 3;
    
    return {
      overallScore: Math.round(overallScore * 100) / 100,
      completeness: {
        score: Math.round(completenessScore * 100) / 100,
        missingValues,
        completenessPerColumn
      },
      consistency: {
        score: Math.round(consistencyScore * 100) / 100,
        inconsistentValues
      },
      validity: {
        score: Math.round(validityScore * 100) / 100,
        invalidValues
      }
    };
  }
  
  /**
   * Verificar se valor é consistente com o tipo
   */
  private isValueConsistentWithType(value: any, type: string): boolean {
    switch (type) {
      case 'numeric':
        return !isNaN(parseFloat(value)) && isFinite(value);
      case 'boolean':
        return ['true', 'false', '1', '0', 'sim', 'não', 'yes', 'no'].includes(String(value).toLowerCase()) || typeof value === 'boolean';
      case 'date':
        return !isNaN(new Date(value).getTime());
      default:
        return true;
    }
  }
  
  /**
   * Verificar se valor é válido
   */
  private isValidValue(value: any, type: string): boolean {
    if (value == null || value === '') return false;
    return this.isValueConsistentWithType(value, type);
  }
  
  /**
   * Calcular estatísticas descritivas
   */
  private calculateDescriptiveStatistics(
    data: any[], 
    dataStructure: ExploratoryAnalysisResult['dataStructure']
  ): ExploratoryAnalysisResult['descriptiveStats'] {
    const stats: ExploratoryAnalysisResult['descriptiveStats'] = {
      numeric: {},
      categorical: {},
      text: {},
      date: {}
    };
    
    // Estatísticas numéricas
    dataStructure.featureDistribution.numeric.forEach(column => {
      const values = data
        .map(row => parseFloat(row[column]))
        .filter(val => !isNaN(val) && isFinite(val))
        .sort((a, b) => a - b);
      
      if (values.length > 0) {
        const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
        const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
        const std = Math.sqrt(variance);
        
        const q1Index = Math.floor(values.length * 0.25);
        const q3Index = Math.floor(values.length * 0.75);
        const q1 = values[q1Index];
        const q3 = values[q3Index];
        const iqr = q3 - q1;
        
        // Detectar outliers usando IQR
        const outlierThreshold = 1.5 * iqr;
        const outliers = values.filter(val => val < q1 - outlierThreshold || val > q3 + outlierThreshold);
        
        // Calcular skewness e kurtosis
        const skewness = this.calculateSkewness(values, mean, std);
        const kurtosis = this.calculateKurtosis(values, mean, std);
        
        stats.numeric[column] = {
          count: values.length,
          mean: Math.round(mean * 100) / 100,
          median: values[Math.floor(values.length / 2)],
          std: Math.round(std * 100) / 100,
          variance: Math.round(variance * 100) / 100,
          min: values[0],
          max: values[values.length - 1],
          q1,
          q3,
          iqr: Math.round(iqr * 100) / 100,
          skewness: Math.round(skewness * 100) / 100,
          kurtosis: Math.round(kurtosis * 100) / 100,
          outliers: outliers.slice(0, 10) // Top 10 outliers
        };
      }
    });
    
    // Estatísticas categóricas
    dataStructure.featureDistribution.categorical.forEach(column => {
      const values = data.map(row => row[column]).filter(val => val != null && val !== '');
      const valueCounts = new Map();
      
      values.forEach(val => {
        valueCounts.set(val, (valueCounts.get(val) || 0) + 1);
      });
      
      const sortedCounts = Array.from(valueCounts.entries())
        .sort((a, b) => b[1] - a[1]);
      
      const entropy = this.calculateEntropy(Array.from(valueCounts.values()));
      
      stats.categorical[column] = {
        count: values.length,
        uniqueValues: valueCounts.size,
        mostFrequent: { value: sortedCounts[0]?.[0], frequency: sortedCounts[0]?.[1] || 0 },
        leastFrequent: { value: sortedCounts[sortedCounts.length - 1]?.[0], frequency: sortedCounts[sortedCounts.length - 1]?.[1] || 0 },
        valueDistribution: sortedCounts.slice(0, 10).map(([value, count]) => ({
          value,
          count,
          percentage: Math.round((count / values.length) * 100 * 100) / 100
        })),
        entropy: Math.round(entropy * 100) / 100
      };
    });
    
    // Estatísticas de texto
    dataStructure.featureDistribution.text.forEach(column => {
      const values = data.map(row => String(row[column] || '')).filter(val => val !== '');
      const lengths = values.map(val => val.length);
      
      stats.text[column] = {
        count: values.length,
        avgLength: lengths.length > 0 ? Math.round(lengths.reduce((sum, len) => sum + len, 0) / lengths.length * 100) / 100 : 0,
        minLength: lengths.length > 0 ? Math.min(...lengths) : 0,
        maxLength: lengths.length > 0 ? Math.max(...lengths) : 0,
        uniqueValues: new Set(values).size
      };
    });
    
    // Estatísticas de data
    dataStructure.featureDistribution.date.forEach(column => {
      const dates = data
        .map(row => new Date(row[column]))
        .filter(date => !isNaN(date.getTime()))
        .sort((a, b) => a.getTime() - b.getTime());
      
      if (dates.length > 0) {
        const earliest = dates[0];
        const latest = dates[dates.length - 1];
        const rangeInDays = (latest.getTime() - earliest.getTime()) / (1000 * 60 * 60 * 24);
        
        stats.date[column] = {
          count: dates.length,
          earliestDate: earliest,
          latestDate: latest,
          dateRange: Math.round(rangeInDays)
        };
      }
    });
    
    return stats;
  }
  
  /**
   * Calcular skewness
   */
  private calculateSkewness(values: number[], mean: number, std: number): number {
    if (std === 0) return 0;
    const n = values.length;
    const skew = values.reduce((sum, val) => sum + Math.pow((val - mean) / std, 3), 0) / n;
    return skew;
  }
  
  /**
   * Calcular kurtosis
   */
  private calculateKurtosis(values: number[], mean: number, std: number): number {
    if (std === 0) return 0;
    const n = values.length;
    const kurt = values.reduce((sum, val) => sum + Math.pow((val - mean) / std, 4), 0) / n - 3;
    return kurt;
  }
  
  /**
   * Calcular entropia
   */
  private calculateEntropy(frequencies: number[]): number {
    const total = frequencies.reduce((sum, freq) => sum + freq, 0);
    if (total === 0) return 0;
    
    return -frequencies.reduce((entropy, freq) => {
      if (freq === 0) return entropy;
      const p = freq / total;
      return entropy + p * Math.log2(p);
    }, 0);
  }
  
  /**
   * Analisar relacionamentos entre variáveis
   */
  private analyzeRelationships(
    data: any[], 
    dataStructure: ExploratoryAnalysisResult['dataStructure']
  ): ExploratoryAnalysisResult['relationships'] {
    const numericFeatures = dataStructure.featureDistribution.numeric;
    const correlationMatrix: Record<string, Record<string, number>> = {};
    const strongCorrelations: Array<{
      feature1: string;
      feature2: string;
      correlation: number;
      type: 'positive' | 'negative';
    }> = [];
    
    // Calcular matriz de correlação para variáveis numéricas
    if (numericFeatures.length > 1) {
      numericFeatures.forEach(feature1 => {
        correlationMatrix[feature1] = {};
        
        numericFeatures.forEach(feature2 => {
          const correlation = this.calculateCorrelation(data, feature1, feature2);
          correlationMatrix[feature1][feature2] = correlation;
          
          // Identificar correlações fortes
          if (feature1 !== feature2 && Math.abs(correlation) > 0.5) {
            strongCorrelations.push({
              feature1,
              feature2,
              correlation: Math.round(correlation * 100) / 100,
              type: correlation > 0 ? 'positive' : 'negative'
            });
          }
        });
      });
    }
    
    return {
      correlationMatrix: Object.keys(correlationMatrix).length > 0 ? correlationMatrix : undefined,
      strongCorrelations
    };
  }
  
  /**
   * Calcular correlação de Pearson
   */
  private calculateCorrelation(data: any[], feature1: string, feature2: string): number {
    const pairs = data
      .map(row => [parseFloat(row[feature1]), parseFloat(row[feature2])])
      .filter(([x, y]) => !isNaN(x) && !isNaN(y) && isFinite(x) && isFinite(y));
    
    if (pairs.length < 2) return 0;
    
    const n = pairs.length;
    const sumX = pairs.reduce((sum, [x]) => sum + x, 0);
    const sumY = pairs.reduce((sum, [, y]) => sum + y, 0);
    const sumXY = pairs.reduce((sum, [x, y]) => sum + x * y, 0);
    const sumX2 = pairs.reduce((sum, [x]) => sum + x * x, 0);
    const sumY2 = pairs.reduce((sum, [, y]) => sum + y * y, 0);
    
    const numerator = n * sumXY - sumX * sumY;
    const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
    
    return denominator === 0 ? 0 : numerator / denominator;
  }
  
  /**
   * Gerar insights automáticos
   */
  private generateInsights(
    data: any[],
    dataStructure: ExploratoryAnalysisResult['dataStructure'],
    dataQuality: ExploratoryAnalysisResult['dataQuality'],
    descriptiveStats: ExploratoryAnalysisResult['descriptiveStats']
  ): ExploratoryAnalysisResult['insights'] {
    const insights: ExploratoryAnalysisResult['insights'] = {
      keyFindings: [],
      dataQualityIssues: [],
      recommendations: [],
      potentialMLFeatures: [],
      businessInsights: []
    };
    
    // Key findings
    insights.keyFindings.push(`Dataset contém ${data.length} registros e ${dataStructure.totalColumns} colunas`);
    insights.keyFindings.push(`Qualidade geral dos dados: ${(dataQuality.overallScore * 100).toFixed(1)}%`);
    
    if (dataStructure.featureDistribution.numeric.length > 0) {
      insights.keyFindings.push(`${dataStructure.featureDistribution.numeric.length} variáveis numéricas identificadas`);
    }
    
    if (dataStructure.featureDistribution.categorical.length > 0) {
      insights.keyFindings.push(`${dataStructure.featureDistribution.categorical.length} variáveis categóricas identificadas`);
    }
    
    // Data quality issues
    if (dataQuality.completeness.score < 0.9) {
      insights.dataQualityIssues.push(`Completude baixa: ${(dataQuality.completeness.score * 100).toFixed(1)}%`);
    }
    
    if (dataQuality.consistency.score < 0.9) {
      insights.dataQualityIssues.push(`Inconsistência nos dados: ${(dataQuality.consistency.score * 100).toFixed(1)}%`);
    }
    
    // Recommendations
    if (dataStructure.featureDistribution.numeric.length > 2) {
      insights.recommendations.push('Considere análise de correlação entre variáveis numéricas');
    }
    
    if (dataQuality.overallScore < 0.8) {
      insights.recommendations.push('Recomenda-se limpeza e pré-processamento dos dados');
    }
    
    // Potential ML features
    dataStructure.featureDistribution.numeric.forEach(feature => {
      const stats = descriptiveStats.numeric[feature];
      if (stats && Math.abs(stats.skewness) < 2) {
        insights.potentialMLFeatures.push(`${feature} (distribuição normal)`);
      }
    });
    
    dataStructure.featureDistribution.categorical.forEach(feature => {
      const stats = descriptiveStats.categorical[feature];
      if (stats && stats.uniqueValues > 1 && stats.uniqueValues < 20) {
        insights.potentialMLFeatures.push(`${feature} (categórica balanceada)`);
      }
    });
    
    return insights;
  }
  
  /**
   * Sugerir visualizações
   */
  private suggestVisualizations(
    dataStructure: ExploratoryAnalysisResult['dataStructure'],
    descriptiveStats: ExploratoryAnalysisResult['descriptiveStats']
  ): ExploratoryAnalysisResult['suggestedVisualizations'] {
    const suggestions: ExploratoryAnalysisResult['suggestedVisualizations'] = [];
    
    // Histogramas para variáveis numéricas
    dataStructure.featureDistribution.numeric.forEach(feature => {
      suggestions.push({
        type: 'histogram',
        features: [feature],
        description: `Distribuição de ${feature}`,
        priority: 'high'
      });
    });
    
    // Boxplots para detectar outliers
    if (dataStructure.featureDistribution.numeric.length > 0) {
      suggestions.push({
        type: 'boxplot',
        features: dataStructure.featureDistribution.numeric,
        description: 'Detecção de outliers em variáveis numéricas',
        priority: 'medium'
      });
    }
    
    // Gráficos de barras para categóricas
    dataStructure.featureDistribution.categorical.forEach(feature => {
      suggestions.push({
        type: 'bar',
        features: [feature],
        description: `Distribuição de frequência de ${feature}`,
        priority: 'medium'
      });
    });
    
    // Scatter plots para correlações
    if (dataStructure.featureDistribution.numeric.length > 1) {
      const numFeatures = dataStructure.featureDistribution.numeric;
      for (let i = 0; i < numFeatures.length - 1; i++) {
        for (let j = i + 1; j < numFeatures.length; j++) {
          suggestions.push({
            type: 'scatter',
            features: [numFeatures[i], numFeatures[j]],
            description: `Correlação entre ${numFeatures[i]} e ${numFeatures[j]}`,
            priority: 'low'
          });
        }
      }
    }
    
    // Heatmap de correlação
    if (dataStructure.featureDistribution.numeric.length > 2) {
      suggestions.push({
        type: 'heatmap',
        features: dataStructure.featureDistribution.numeric,
        description: 'Matriz de correlação das variáveis numéricas',
        priority: 'high'
      });
    }
    
    return suggestions;
  }
}
