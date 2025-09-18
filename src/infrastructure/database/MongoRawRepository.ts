import { MongoConnection } from './MongoConnection';
import { RawDataRecord, ExploratoryAnalysisResult } from '../../application/services/ExploratoryAnalysisService';

export class MongoRawRepository {
  private connection: MongoConnection;

  constructor() {
    this.connection = MongoConnection.getInstance();
  }

  /**
   * Salvar dados brutos vinculados ao ID da mensagem
   */
  async saveRawData(
    messageId: string,
    filename: string,
    from: string,
    csvData: any[]
  ): Promise<string> {
    try {
      await this.connection.connect();
      const db = this.connection.getDb();
      const collection = db.collection('raw');
      
      console.log(`💾 Salvando dados brutos para mensagem ${messageId} (${csvData.length} registros)`);
      
      // Analisar estrutura dos dados
      const dataAnalysis = this.analyzeDataStructure(csvData);
      
      // Processar cada linha do CSV
      const rawRecords: Omit<RawDataRecord, '_id'>[] = csvData.map((row, index) => {
        const normalizedData = this.normalizeData(row, dataAnalysis.dataTypes);
        
        return {
          messageId,
          filename,
          from,
          processedAt: new Date(),
          rowIndex: index,
          originalData: row,
          normalizedData,
          dataTypes: dataAnalysis.dataTypes,
          metadata: {
            source: 'whatsapp_csv',
            quality: this.calculateDataQuality(row, dataAnalysis.dataTypes)
          }
        };
      });
      
      // Inserir todos os registros
      const result = await collection.insertMany(rawRecords);
      
      console.log(`✅ Dados brutos salvos: ${result.insertedCount} registros na coleção 'raw'`);
      
      return `${result.insertedCount} registros salvos na coleção raw`;
    } catch (error) {
      console.error('❌ Erro ao salvar dados brutos:', error);
      throw error;
    }
  }

  /**
   * Buscar dados brutos por ID da mensagem
   */
  async getRawDataByMessageId(messageId: string): Promise<RawDataRecord[]> {
    try {
      await this.connection.connect();
      const db = this.connection.getDb();
      const collection = db.collection('raw');
      
      const data = await collection
        .find({ messageId })
        .sort({ rowIndex: 1 })
        .toArray();
      
      return data.map((record: any) => ({
        ...record,
        _id: record._id.toString()
      }));
    } catch (error) {
      console.error('❌ Erro ao buscar dados brutos:', error);
      return [];
    }
  }

  /**
   * Listar todas as mensagens com dados brutos
   */
  async getAllRawDataMessages(): Promise<Array<{
    messageId: string;
    filename: string;
    from: string;
    processedAt: Date;
    recordCount: number;
  }>> {
    try {
      await this.connection.connect();
      const db = this.connection.getDb();
      const collection = db.collection('raw');
      
      const pipeline = [
        {
          $group: {
            _id: '$messageId',
            filename: { $first: '$filename' },
            from: { $first: '$from' },
            processedAt: { $first: '$processedAt' },
            recordCount: { $sum: 1 }
          }
        },
        {
          $project: {
            messageId: '$_id',
            filename: 1,
            from: 1,
            processedAt: 1,
            recordCount: 1,
            _id: 0
          }
        },
        {
          $sort: { processedAt: -1 }
        }
      ];
      
      const results = await collection.aggregate(pipeline).toArray();
      
      return results.map((result: any) => ({
        messageId: result.messageId,
        filename: result.filename,
        from: result.from,
        processedAt: result.processedAt,
        recordCount: result.recordCount
      }));
    } catch (error) {
      console.error('❌ Erro ao listar mensagens com dados brutos:', error);
      return [];
    }
  }

  /**
   * Salvar resultado de análise exploratória
   */
  async saveExploratoryAnalysis(analysis: ExploratoryAnalysisResult): Promise<void> {
    try {
      await this.connection.connect();
      const db = this.connection.getDb();
      const collection = db.collection('exploratory_analysis');
      
      // Remover análise anterior para a mesma mensagem
      await collection.deleteMany({ messageId: analysis.messageId });
      
      // Inserir nova análise
      await collection.insertOne(analysis);
      
      console.log(`📊 Análise exploratória salva para mensagem ${analysis.messageId}`);
    } catch (error) {
      console.error('❌ Erro ao salvar análise exploratória:', error);
      throw error;
    }
  }

  /**
   * Buscar análise exploratória por ID da mensagem
   */
  async getExploratoryAnalysisByMessageId(messageId: string): Promise<ExploratoryAnalysisResult | null> {
    try {
      await this.connection.connect();
      const db = this.connection.getDb();
      const collection = db.collection('exploratory_analysis');
      
      const analysis = await collection.findOne({ messageId });
      
      if (!analysis) return null;
      
      return {
        messageId: analysis.messageId,
        filename: analysis.filename,
        from: analysis.from,
        totalRecords: analysis.totalRecords,
        analysisDate: analysis.analysisDate,
        dataStructure: analysis.dataStructure,
        dataQuality: analysis.dataQuality,
        descriptiveStats: analysis.descriptiveStats,
        relationships: analysis.relationships,
        insights: analysis.insights,
        suggestedVisualizations: analysis.suggestedVisualizations,
        _id: analysis._id?.toString()
      } as ExploratoryAnalysisResult;
    } catch (error) {
      console.error('❌ Erro ao buscar análise exploratória:', error);
      return null;
    }
  }

  /**
   * Listar todas as análises exploratórias
   */
  async getAllExploratoryAnalyses(): Promise<Array<{
    messageId: string;
    filename: string;
    from: string;
    totalRecords: number;
    analysisDate: Date;
    overallQuality: number;
  }>> {
    try {
      await this.connection.connect();
      const db = this.connection.getDb();
      const collection = db.collection('exploratory_analysis');
      
      const analyses = await collection
        .find({})
        .sort({ analysisDate: -1 })
        .toArray();
      
      return analyses.map((analysis: any) => ({
        messageId: analysis.messageId,
        filename: analysis.filename,
        from: analysis.from,
        totalRecords: analysis.totalRecords,
        analysisDate: analysis.analysisDate,
        overallQuality: analysis.dataQuality.overallScore
      }));
    } catch (error) {
      console.error('❌ Erro ao listar análises exploratórias:', error);
      return [];
    }
  }

  /**
   * Deletar dados brutos por ID da mensagem
   */
  async deleteRawDataByMessageId(messageId: string): Promise<number> {
    try {
      await this.connection.connect();
      const db = this.connection.getDb();
      const rawCollection = db.collection('raw');
      const analysisCollection = db.collection('exploratory_analysis');
      
      // Deletar dados brutos
      const rawResult = await rawCollection.deleteMany({ messageId });
      
      // Deletar análise exploratória
      await analysisCollection.deleteMany({ messageId });
      
      console.log(`🗑️ Removidos ${rawResult.deletedCount} registros brutos para mensagem ${messageId}`);
      
      return rawResult.deletedCount;
    } catch (error) {
      console.error('❌ Erro ao deletar dados brutos:', error);
      return 0;
    }
  }

  /**
   * Obter estatísticas gerais da coleção raw
   */
  async getRawDataStats(): Promise<{
    totalMessages: number;
    totalRecords: number;
    totalSize: number;
    oldestRecord: Date | null;
    newestRecord: Date | null;
    topSenders: Array<{ from: string; messageCount: number; recordCount: number }>;
  }> {
    try {
      await this.connection.connect();
      const db = this.connection.getDb();
      const collection = db.collection('raw');
      
      const [
        totalRecords,
        messageStats,
        dateStats,
        senderStats
      ] = await Promise.all([
        // Total de registros
        collection.countDocuments(),
        
        // Estatísticas de mensagens
        collection.aggregate([
          {
            $group: {
              _id: null,
              uniqueMessages: { $addToSet: '$messageId' },
              totalSize: { $sum: { $bsonSize: '$$ROOT' } }
            }
          }
        ]).toArray(),
        
        // Estatísticas de datas
        collection.aggregate([
          {
            $group: {
              _id: null,
              oldestRecord: { $min: '$processedAt' },
              newestRecord: { $max: '$processedAt' }
            }
          }
        ]).toArray(),
        
        // Top remetentes
        collection.aggregate([
          {
            $group: {
              _id: '$from',
              messageCount: { $addToSet: '$messageId' },
              recordCount: { $sum: 1 }
            }
          },
          {
            $project: {
              from: '$_id',
              messageCount: { $size: '$messageCount' },
              recordCount: 1,
              _id: 0
            }
          },
          {
            $sort: { recordCount: -1 }
          },
          {
            $limit: 10
          }
        ]).toArray()
      ]);
      
      return {
        totalMessages: messageStats[0]?.uniqueMessages?.length || 0,
        totalRecords,
        totalSize: messageStats[0]?.totalSize || 0,
        oldestRecord: dateStats[0]?.oldestRecord || null,
        newestRecord: dateStats[0]?.newestRecord || null,
        topSenders: senderStats.map((stat: any) => ({
          from: stat.from,
          messageCount: stat.messageCount,
          recordCount: stat.recordCount
        }))
      };
    } catch (error) {
      console.error('❌ Erro ao obter estatísticas dos dados brutos:', error);
      return {
        totalMessages: 0,
        totalRecords: 0,
        totalSize: 0,
        oldestRecord: null,
        newestRecord: null,
        topSenders: []
      };
    }
  }

  /**
   * Analisar estrutura dos dados (método auxiliar)
   */
  private analyzeDataStructure(data: any[]): {
    dataTypes: Record<string, 'numeric' | 'categorical' | 'text' | 'date' | 'boolean'>;
  } {
    if (data.length === 0) {
      return { dataTypes: {} };
    }
    
    const columns = Object.keys(data[0]);
    const dataTypes: Record<string, 'numeric' | 'categorical' | 'text' | 'date' | 'boolean'> = {};
    
    columns.forEach(column => {
      const values = data.map(row => row[column]).filter(val => val != null && val !== '');
      const dataType = this.detectDataType(values);
      dataTypes[column] = dataType;
    });
    
    return { dataTypes };
  }

  /**
   * Detectar tipo de dados (método auxiliar)
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
   * Normalizar dados (método auxiliar)
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
   * Normalizar valores booleanos (método auxiliar)
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
   * Calcular qualidade dos dados (método auxiliar)
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
   * Verificar se valor é consistente com o tipo (método auxiliar)
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
}
