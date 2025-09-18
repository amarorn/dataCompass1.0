import { MongoConnection } from './MongoConnection';

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
      topValues: Array<{value: any, count: number}>;
      nullCount: number;
    }>;
  };
  createdAt: Date;
  updatedAt: Date;
}

export class MongoMLRepository {
  private connection: MongoConnection;

  constructor() {
    this.connection = MongoConnection.getInstance();
  }

  /**
   * Processar e salvar dados de CSV para análise de ML
   */
  async processCSVForML(
    csvId: string,
    filename: string,
    from: string,
    csvData: any[]
  ): Promise<string> {
    try {
      await this.connection.connect();
      const db = this.connection.getDb();
      const collection = db.collection('ml_data');
      
      console.log(`🤖 Processing CSV for ML: ${filename} (${csvData.length} rows)`);
      
      // Analisar estrutura dos dados
      const dataAnalysis = this.analyzeDataStructure(csvData);
      
      // Processar cada linha do CSV
      const mlRecords: MLDataRecord[] = csvData.map((row, index) => {
        const normalizedData = this.normalizeData(row, dataAnalysis.dataTypes);
        
        return {
          csvId,
          filename,
          from,
          processedAt: new Date(),
          rowIndex: index,
          originalData: row,
          normalizedData,
          dataTypes: dataAnalysis.dataTypes,
          features: dataAnalysis.features,
          metadata: {
            source: 'whatsapp_csv',
            quality: this.calculateDataQuality(row, dataAnalysis.dataTypes)
          }
        };
      });
      
      // Inserir todos os registros (remover _id antes de inserir)
      const recordsToInsert = mlRecords.map(record => {
        const { _id, ...recordWithoutId } = record;
        return recordWithoutId;
      });
      const result = await collection.insertMany(recordsToInsert);
      
      // Criar resumo do dataset
      await this.createDatasetSummary(csvId, filename, mlRecords, dataAnalysis);
      
      console.log(`✅ ML data processed: ${result.insertedCount} records inserted`);
      
      return `${result.insertedCount} records processed for ML`;
    } catch (error) {
      console.error('❌ Error processing CSV for ML:', error);
      throw error;
    }
  }

  /**
   * Analisar estrutura dos dados
   */
  private analyzeDataStructure(data: any[]): {
    dataTypes: Record<string, 'numeric' | 'categorical' | 'text' | 'date' | 'boolean'>;
    features: {
      numericFeatures: string[];
      categoricalFeatures: string[];
      textFeatures: string[];
      dateFeatures: string[];
      booleanFeatures: string[];
    };
  } {
    if (data.length === 0) {
      return {
        dataTypes: {},
        features: {
          numericFeatures: [],
          categoricalFeatures: [],
          textFeatures: [],
          dateFeatures: [],
          booleanFeatures: []
        }
      };
    }
    
    const columns = Object.keys(data[0]);
    const dataTypes: Record<string, 'numeric' | 'categorical' | 'text' | 'date' | 'boolean'> = {};
    const features = {
      numericFeatures: [] as string[],
      categoricalFeatures: [] as string[],
      textFeatures: [] as string[],
      dateFeatures: [] as string[],
      booleanFeatures: [] as string[]
    };
    
    columns.forEach(column => {
      const values = data.map(row => row[column]).filter(val => val != null && val !== '');
      const dataType = this.detectDataType(values);
      
      dataTypes[column] = dataType;
      
      switch (dataType) {
        case 'numeric':
          features.numericFeatures.push(column);
          break;
        case 'categorical':
          features.categoricalFeatures.push(column);
          break;
        case 'text':
          features.textFeatures.push(column);
          break;
        case 'date':
          features.dateFeatures.push(column);
          break;
        case 'boolean':
          features.booleanFeatures.push(column);
          break;
      }
    });
    
    return { dataTypes, features };
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
    
    // Default para texto
    return 'text';
  }

  /**
   * Normalizar dados
   */
  private normalizeData(
    row: Record<string, any>, 
    dataTypes: Record<string, string>
  ): Record<string, any> {
    const normalized: Record<string, any> = {};
    
    Object.entries(row).forEach(([key, value]) => {
      const dataType = dataTypes[key];
      
      switch (dataType) {
        case 'numeric':
          normalized[key] = value != null ? parseFloat(value) : null;
          break;
        case 'boolean':
          normalized[key] = this.normalizeBoolean(value);
          break;
        case 'date':
          normalized[key] = value ? new Date(value) : null;
          break;
        case 'categorical':
          normalized[key] = value ? String(value).trim().toLowerCase() : null;
          break;
        case 'text':
          normalized[key] = value ? String(value).trim() : null;
          break;
        default:
          normalized[key] = value;
      }
    });
    
    return normalized;
  }

  /**
   * Normalizar valores booleanos
   */
  private normalizeBoolean(value: any): boolean | null {
    if (value == null) return null;
    
    const strValue = String(value).toLowerCase();
    const trueValues = ['true', '1', 'sim', 'yes', 'verdadeiro', 's', 'y'];
    const falseValues = ['false', '0', 'não', 'no', 'falso', 'n'];
    
    if (trueValues.includes(strValue)) return true;
    if (falseValues.includes(strValue)) return false;
    
    return typeof value === 'boolean' ? value : null;
  }

  /**
   * Calcular qualidade dos dados
   */
  private calculateDataQuality(
    row: Record<string, any>, 
    dataTypes: Record<string, string>
  ): { completeness: number; consistency: number; validity: number } {
    const totalFields = Object.keys(dataTypes).length;
    
    // Completude: % de campos preenchidos
    const filledFields = Object.values(row).filter(val => val != null && val !== '').length;
    const completeness = totalFields > 0 ? filledFields / totalFields : 0;
    
    // Consistência: % de campos no formato esperado
    let consistentFields = 0;
    Object.entries(row).forEach(([key, value]) => {
      const expectedType = dataTypes[key];
      if (this.isValueConsistentWithType(value, expectedType)) {
        consistentFields++;
      }
    });
    const consistency = totalFields > 0 ? consistentFields / totalFields : 0;
    
    // Validade: % de valores válidos (não nulos e consistentes)
    const validity = (completeness + consistency) / 2;
    
    return {
      completeness: Math.round(completeness * 100) / 100,
      consistency: Math.round(consistency * 100) / 100,
      validity: Math.round(validity * 100) / 100
    };
  }

  /**
   * Verificar se valor é consistente com o tipo
   */
  private isValueConsistentWithType(value: any, type: string): boolean {
    if (value == null || value === '') return false;
    
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
   * Criar resumo do dataset
   */
  private async createDatasetSummary(
    csvId: string,
    filename: string,
    records: MLDataRecord[],
    dataAnalysis: any
  ): Promise<void> {
    try {
      const db = this.connection.getDb();
      const collection = db.collection('ml_datasets');
      
      // Calcular estatísticas
      const numericStats = this.calculateNumericStatistics(records, dataAnalysis.features.numericFeatures);
      const categoricalStats = this.calculateCategoricalStatistics(records, dataAnalysis.features.categoricalFeatures);
      
      // Calcular qualidade média
      const qualityMetrics = records.map(r => r.metadata.quality);
      const avgQuality = {
        averageCompleteness: qualityMetrics.reduce((sum, q) => sum + q.completeness, 0) / qualityMetrics.length,
        averageConsistency: qualityMetrics.reduce((sum, q) => sum + q.consistency, 0) / qualityMetrics.length,
        averageValidity: qualityMetrics.reduce((sum, q) => sum + q.validity, 0) / qualityMetrics.length
      };
      
      const summary: Omit<MLDatasetSummary, '_id'> = {
        csvId,
        filename,
        totalRecords: records.length,
        features: {
          total: Object.keys(dataAnalysis.dataTypes).length,
          numeric: dataAnalysis.features.numericFeatures.length,
          categorical: dataAnalysis.features.categoricalFeatures.length,
          text: dataAnalysis.features.textFeatures.length,
          date: dataAnalysis.features.dateFeatures.length,
          boolean: dataAnalysis.features.booleanFeatures.length
        },
        dataQuality: avgQuality,
        statistics: {
          numericStats,
          categoricalStats
        },
        createdAt: new Date(),
        updatedAt: new Date()
      };
      
      // Inserir ou atualizar resumo
      await collection.replaceOne(
        { csvId },
        summary,
        { upsert: true }
      );
      
      console.log(`📊 Dataset summary created for ${filename}`);
    } catch (error) {
      console.error('❌ Error creating dataset summary:', error);
    }
  }

  /**
   * Calcular estatísticas numéricas
   */
  private calculateNumericStatistics(
    records: MLDataRecord[],
    numericFeatures: string[]
  ): Record<string, any> {
    const stats: Record<string, any> = {};
    
    numericFeatures.forEach(feature => {
      const values = records
        .map(r => r.normalizedData[feature])
        .filter(val => val != null && !isNaN(val))
        .map(val => parseFloat(val));
      
      if (values.length > 0) {
        const sorted = values.sort((a, b) => a - b);
        const sum = values.reduce((acc, val) => acc + val, 0);
        const mean = sum / values.length;
        const variance = values.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / values.length;
        
        stats[feature] = {
          min: sorted[0],
          max: sorted[sorted.length - 1],
          mean: Math.round(mean * 100) / 100,
          median: sorted.length % 2 === 0 
            ? (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2
            : sorted[Math.floor(sorted.length / 2)],
          std: Math.round(Math.sqrt(variance) * 100) / 100,
          nullCount: records.length - values.length
        };
      }
    });
    
    return stats;
  }

  /**
   * Calcular estatísticas categóricas
   */
  private calculateCategoricalStatistics(
    records: MLDataRecord[],
    categoricalFeatures: string[]
  ): Record<string, any> {
    const stats: Record<string, any> = {};
    
    categoricalFeatures.forEach(feature => {
      const values = records
        .map(r => r.normalizedData[feature])
        .filter(val => val != null);
      
      const valueCounts = new Map();
      values.forEach(val => {
        valueCounts.set(val, (valueCounts.get(val) || 0) + 1);
      });
      
      const topValues = Array.from(valueCounts.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(([value, count]) => ({ value, count }));
      
      stats[feature] = {
        uniqueValues: valueCounts.size,
        topValues,
        nullCount: records.length - values.length
      };
    });
    
    return stats;
  }

  /**
   * Buscar dados para ML por CSV ID
   */
  async getMLDataByCSV(csvId: string): Promise<MLDataRecord[]> {
    try {
      await this.connection.connect();
      const db = this.connection.getDb();
      const collection = db.collection('ml_data');
      
      const data = await collection
        .find({ csvId })
        .sort({ rowIndex: 1 })
        .toArray();
      
      return data.map((record: any) => ({
        ...record,
        _id: record._id.toString()
      }));
    } catch (error) {
      console.error('❌ Error fetching ML data:', error);
      return [];
    }
  }

  /**
   * Buscar resumo do dataset
   */
  async getDatasetSummary(csvId: string): Promise<MLDatasetSummary | null> {
    try {
      await this.connection.connect();
      const db = this.connection.getDb();
      const collection = db.collection('ml_datasets');
      
      const summary = await collection.findOne({ csvId });
      
      if (!summary) return null;
      
      return {
        csvId: summary.csvId,
        filename: summary.filename,
        totalRecords: summary.totalRecords,
        features: summary.features,
        dataQuality: summary.dataQuality,
        statistics: summary.statistics,
        createdAt: summary.createdAt,
        updatedAt: summary.updatedAt,
        _id: summary._id?.toString()
      } as MLDatasetSummary;
    } catch (error) {
      console.error('❌ Error fetching dataset summary:', error);
      return null;
    }
  }

  /**
   * Listar todos os datasets disponíveis
   */
  async getAllDatasets(): Promise<MLDatasetSummary[]> {
    try {
      await this.connection.connect();
      const db = this.connection.getDb();
      const collection = db.collection('ml_datasets');
      
      const datasets = await collection
        .find({})
        .sort({ createdAt: -1 })
        .toArray();
      
      return datasets.map((dataset: any) => ({
        ...dataset,
        _id: dataset._id.toString()
      }));
    } catch (error) {
      console.error('❌ Error fetching datasets:', error);
      return [];
    }
  }
}
