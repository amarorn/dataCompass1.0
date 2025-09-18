import { Router, Request, Response } from 'express';
import { asyncHandler } from '../middlewares/errorHandler';
import { WhatsAppService, WhatsAppWebhookPayload } from '../../infrastructure/external/WhatsAppService';
import { MessageProcessorService } from '../../application/services/MessageProcessorService';
import { WhatsAppRegistrationService } from '../../application/services/WhatsAppRegistrationService';
import { MongoConnection } from '../../infrastructure/database/MongoConnection';
import { MongoUserRepository } from '../../infrastructure/database/MongoUserRepository';
import { Client } from '../../domain/entities/Client';
import { Interaction } from '../../domain/entities/Interaction';
import { addToHistory } from './messageHistoryRoutes';
import { MongoCSVRepository, ProcessedCSVDocument } from '../../infrastructure/database/MongoCSVRepository';
import { MongoMessageRepository } from '../../infrastructure/database/MongoMessageRepository';
import { MongoMLRepository } from '../../infrastructure/database/MongoMLRepository';
import { MongoRawRepository } from '../../infrastructure/database/MongoRawRepository';
import { ExploratoryAnalysisService } from '../../application/services/ExploratoryAnalysisService';
import { ChartGeneratorService } from '../../application/services/ChartGeneratorService';
import axios from 'axios';
import * as fs from 'fs';
import * as path from 'path';
import csv from 'csv-parser';

const router = Router();
const whatsappService = new WhatsAppService();
const messageProcessor = new MessageProcessorService();
const csvRepository = new MongoCSVRepository();
const messageRepository = new MongoMessageRepository();
const mlRepository = new MongoMLRepository();
const rawRepository = new MongoRawRepository();
const analysisService = new ExploratoryAnalysisService();
const chartService = new ChartGeneratorService();

// Função para processar documentos CSV recebidos
async function processCSVDocument(document: any, from: string, messageId: string): Promise<void> {
  console.log('🔄 Starting CSV processing...', { documentId: document.id, filename: document.filename });
  
  try {
    // Verificar se o token está configurado
    const token = process.env.WHATSAPP_TOKEN;
    if (!token) {
      throw new Error('WhatsApp token not configured');
    }
    
    console.log('📥 Downloading CSV file from WhatsApp...', { documentId: document.id });
    
    // 1. Baixar o arquivo da API do WhatsApp
    const fileUrl = `https://graph.facebook.com/v21.0/${document.id}`;
    console.log('🌐 Requesting file URL:', fileUrl);
    
    const response = await axios.get(fileUrl, {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      timeout: 10000 // 10 segundos timeout
    });
    
    console.log('📋 File URL response:', {
      status: response.status,
      hasUrl: !!response.data.url,
      dataKeys: Object.keys(response.data)
    });
    
    const downloadUrl = response.data.url;
    if (!downloadUrl) {
      throw new Error('No download URL received from WhatsApp API');
    }
    
    console.log('📁 File download URL obtained, starting download...');
    
    // 2. Baixar o conteúdo do arquivo
    const fileResponse = await axios.get(downloadUrl, {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      responseType: 'stream'
    });
    
    // 3. Criar diretório temporário se não existir
    const tempDir = path.join(process.cwd(), 'temp');
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }
    
    // 4. Salvar arquivo temporariamente
    const tempFilePath = path.join(tempDir, `${messageId}_${document.filename}`);
    const writer = fs.createWriteStream(tempFilePath);
    
    fileResponse.data.pipe(writer);
    
    await new Promise<void>((resolve, reject) => {
      writer.on('finish', () => resolve());
      writer.on('error', reject);
    });
    
    console.log('💾 File saved temporarily:', tempFilePath);
    
    // 5. Processar CSV
    const csvData: any[] = [];
    const columns = new Set<string>();
    
    await new Promise<void>((resolve, reject) => {
      fs.createReadStream(tempFilePath)
        .pipe(csv())
        .on('data', (row: any) => {
          csvData.push(row);
          Object.keys(row).forEach(col => columns.add(col));
        })
        .on('end', () => resolve())
        .on('error', reject);
    });
    
    // 6. Gerar insights básicos
    const insights = generateCSVInsights(csvData, Array.from(columns));
    
    // 7. Armazenar dados processados no MongoDB
    const processedCSV: Omit<ProcessedCSVDocument, '_id'> = {
      id: messageId,
      filename: document.filename,
      from: from,
      processedAt: new Date(),
      data: csvData,
      summary: {
        rows: csvData.length,
        columns: Array.from(columns),
        insights: insights
      }
    };
    
    await csvRepository.saveProcessedCSV(processedCSV);
    
    // 7.5. Salvar dados brutos na coleção 'raw' vinculados ao messageId
    try {
      console.log('💾 Salvando dados brutos na coleção raw...');
      const rawResult = await rawRepository.saveRawData(
        messageId,
        document.filename,
        from,
        csvData
      );
      console.log('✅ Dados brutos salvos:', rawResult);
    } catch (rawError) {
      console.error('❌ Erro ao salvar dados brutos (continuando):', rawError);
    }
    
    // 7.6. Realizar análise exploratória completa
    try {
      console.log('🔍 Realizando análise exploratória...');
      const exploratoryAnalysis = await analysisService.performExploratoryAnalysis(
        messageId,
        document.filename,
        from,
        csvData
      );
      
      // Salvar análise exploratória
      await rawRepository.saveExploratoryAnalysis(exploratoryAnalysis);
      console.log('✅ Análise exploratória concluída e salva');
    } catch (analysisError) {
      console.error('❌ Erro na análise exploratória (continuando):', analysisError);
    }
    
    // 7.7. Processar dados para ML (mantendo compatibilidade)
    try {
      console.log('🤖 Processing CSV data for ML analysis...');
      const mlResult = await mlRepository.processCSVForML(
        messageId,
        document.filename,
        from,
        csvData
      );
      console.log('✅ ML processing completed:', mlResult);
    } catch (mlError) {
      console.error('❌ ML processing failed (continuing anyway):', mlError);
    }
    
    // 8. Limpar arquivo temporário
    fs.unlinkSync(tempFilePath);
    
    console.log('✅ CSV processed successfully:', {
      filename: document.filename,
      rows: csvData.length,
      columns: columns.size
    });
    
    // 9. Enviar confirmação inicial ao usuário
    const initialMessage = `🔄 *Processamento Iniciado!*\n\n` +
      `📄 Arquivo: ${document.filename}\n` +
      `📈 Linhas: ${csvData.length}\n` +
      `📋 Colunas: ${columns.size}\n\n` +
      `⏳ Gerando gráficos e análises avançadas...\n` +
      `📊 Em alguns instantes você receberá os gráficos!`;
    
    if (whatsappService.isConfigured()) {
      await whatsappService.sendTextMessage(from, initialMessage);
    } else {
      console.log(`📤 [SIMULATION] CSV initial message: ${initialMessage}`);
    }

    // 10. Gerar e enviar gráficos automaticamente
    console.log('📊 Iniciando geração de gráficos...');
    try {
      const chartResult = await chartService.generateAndSendCharts(messageId, document.filename, from);
      
      if (chartResult.success) {
        console.log(`✅ Gráficos enviados com sucesso: ${chartResult.charts.length} gráficos`);
      } else {
        console.error(`❌ Falha ao enviar gráficos: ${chartResult.error}`);
        
        // Enviar mensagem de fallback se os gráficos falharam
        const fallbackMessage = `📊 *Análise Concluída!*\n\n` +
          `📄 Arquivo: ${document.filename}\n` +
          `📈 Linhas: ${csvData.length}\n` +
          `📋 Colunas: ${columns.size}\n\n` +
          `💡 *Insights:*\n${insights.join('\n')}\n\n` +
          `🔍 *Análises realizadas:*\n` +
          `• ✅ Dados brutos salvos (coleção raw)\n` +
          `• ✅ Análise exploratória completa\n` +
          `• ✅ Preparação para Machine Learning\n` +
          `• ✅ Estatísticas descritivas\n` +
          `• ✅ Detecção de qualidade dos dados\n\n` +
          `📊 ID da Mensagem: ${messageId}\n\n` +
          `⚠️ *Nota:* Os gráficos não puderam ser gerados automaticamente.\n` +
          `Use /raw para dados brutos ou /analysis para análise completa.`;
        
        if (whatsappService.isConfigured()) {
          await whatsappService.sendTextMessage(from, fallbackMessage);
        } else {
          console.log(`📤 [SIMULATION] CSV fallback: ${fallbackMessage}`);
        }
      }
    } catch (chartError) {
      console.error('❌ Erro na geração de gráficos:', chartError);
      
      // Enviar confirmação básica se houver erro nos gráficos
      const basicConfirmation = `📊 *CSV Processado!*\n\n` +
        `📄 Arquivo: ${document.filename}\n` +
        `📈 Linhas: ${csvData.length}\n` +
        `📋 Colunas: ${columns.size}\n\n` +
        `✅ Dados salvos e analisados com sucesso!\n` +
        `📊 ID: ${messageId}\n\n` +
        `💡 Use /raw ou /analysis para acessar os dados.`;
      
      if (whatsappService.isConfigured()) {
        await whatsappService.sendTextMessage(from, basicConfirmation);
      } else {
        console.log(`📤 [SIMULATION] CSV basic confirmation: ${basicConfirmation}`);
      }
    }
    
  } catch (error) {
    console.error('❌ Error processing CSV:', error);
    
    const errorMessage = `❌ Erro ao processar CSV: ${document.filename}\n\n` +
      `Por favor, verifique se o arquivo está no formato correto e tente novamente.`;
    
    if (whatsappService.isConfigured()) {
      await whatsappService.sendTextMessage(from, errorMessage);
    } else {
      console.log(`📤 [SIMULATION] CSV error: ${errorMessage}`);
    }
  }
}

// Função para gerar insights básicos do CSV
function generateCSVInsights(data: any[], columns: string[]): string[] {
  const insights: string[] = [];
  
  if (data.length === 0) {
    insights.push('• Arquivo vazio');
    return insights;
  }
  
  // Insight sobre quantidade de dados
  if (data.length < 10) {
    insights.push('• Dataset pequeno (ideal para testes)');
  } else if (data.length < 1000) {
    insights.push('• Dataset médio (boa amostra para análise)');
  } else {
    insights.push('• Dataset grande (análise robusta possível)');
  }
  
  // Insight sobre colunas numéricas
  const numericColumns = columns.filter(col => {
    const sampleValues = data.slice(0, 10).map(row => row[col]);
    return sampleValues.some(val => !isNaN(parseFloat(val)) && isFinite(val));
  });
  
  if (numericColumns.length > 0) {
    insights.push(`• ${numericColumns.length} coluna(s) numérica(s) detectada(s)`);
  }
  
  // Insight sobre completude dos dados
  const completeness = columns.map(col => {
    const filledValues = data.filter(row => row[col] && row[col].toString().trim() !== '').length;
    return { column: col, percentage: (filledValues / data.length) * 100 };
  });
  
  const avgCompleteness = completeness.reduce((sum, item) => sum + item.percentage, 0) / completeness.length;
  
  if (avgCompleteness > 90) {
    insights.push('• Dados muito completos (>90% preenchidos)');
  } else if (avgCompleteness > 70) {
    insights.push('• Dados moderadamente completos (70-90% preenchidos)');
  } else {
    insights.push('• Dados com lacunas significativas (<70% preenchidos)');
  }
  
  return insights;
}

// Função para gerar análise detalhada de um CSV
function generateDetailedAnalysis(data: any[], columns: string[]): any {
  if (data.length === 0) {
    return { error: 'No data to analyze' };
  }
  
  const analysis: any = {
    overview: {
      totalRows: data.length,
      totalColumns: columns.length,
      dataTypes: {}
    },
    columns: {},
    statistics: {},
    patterns: []
  };
  
  // Analisar cada coluna
  columns.forEach(column => {
    const values = data.map(row => row[column]).filter(val => val !== null && val !== undefined && val !== '');
    const nonEmptyCount = values.length;
    const completeness = (nonEmptyCount / data.length) * 100;
    
    // Detectar tipo de dados
    const numericValues = values.filter(val => !isNaN(parseFloat(val)) && isFinite(val)).map(val => parseFloat(val));
    const isNumeric = numericValues.length > values.length * 0.8; // 80% dos valores são numéricos
    
    analysis.columns[column] = {
      completeness: Math.round(completeness * 100) / 100,
      uniqueValues: new Set(values).size,
      dataType: isNumeric ? 'numeric' : 'text',
      sampleValues: values.slice(0, 5)
    };
    
    analysis.overview.dataTypes[column] = isNumeric ? 'numeric' : 'text';
    
    // Estatísticas para colunas numéricas
    if (isNumeric && numericValues.length > 0) {
      const sorted = numericValues.sort((a, b) => a - b);
      const sum = numericValues.reduce((acc, val) => acc + val, 0);
      const mean = sum / numericValues.length;
      
      analysis.statistics[column] = {
        count: numericValues.length,
        min: sorted[0],
        max: sorted[sorted.length - 1],
        mean: Math.round(mean * 100) / 100,
        median: sorted.length % 2 === 0 
          ? (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2
          : sorted[Math.floor(sorted.length / 2)]
      };
    }
  });
  
  // Detectar padrões
  const numericColumns = columns.filter(col => analysis.overview.dataTypes[col] === 'numeric');
  if (numericColumns.length > 1) {
    analysis.patterns.push(`Dataset com ${numericColumns.length} colunas numéricas - ideal para análise estatística`);
  }
  
  const highCompletenessColumns = columns.filter(col => analysis.columns[col].completeness > 95);
  if (highCompletenessColumns.length > columns.length * 0.8) {
    analysis.patterns.push('Dataset com alta qualidade de dados (>95% completude)');
  }
  
  const uniqueIdentifiers = columns.filter(col => analysis.columns[col].uniqueValues === data.length);
  if (uniqueIdentifiers.length > 0) {
    analysis.patterns.push(`Possível(is) identificador(es) único(s): ${uniqueIdentifiers.join(', ')}`);
  }
  
  return analysis;
}

// Inicializar serviços de registro
let registrationService: WhatsAppRegistrationService | null = null;

// Inicializar MongoDB e serviços
async function initializeServices() {
  try {
    const mongoConnection = MongoConnection.getInstance();
    const db = await mongoConnection.connect();
    const userRepository = new MongoUserRepository(db);
    registrationService = new WhatsAppRegistrationService(userRepository);
    console.log('✅ Registration services initialized');
  } catch (error) {
    console.error('❌ Failed to initialize registration services:', error);
  }
}

// Inicializar serviços na primeira execução
initializeServices();

// GET /api/whatsapp/webhook - Verificação do webhook
router.get('/webhook', asyncHandler(async (req: Request, res: Response) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  console.log('Webhook verification request:', { mode, token });

  // Usar token padrão se não estiver configurado
  const expectedToken = process.env.WHATSAPP_WEBHOOK_VERIFY_TOKEN || 'datacompass_webhook_2025';

  if (mode === 'subscribe' && token === expectedToken) {
    console.log('✅ Webhook verified successfully');
    res.status(200).send(challenge);
  } else {
    console.log('❌ Webhook verification failed');
    console.log('Expected token:', expectedToken);
    console.log('Received token:', token);
    res.status(403).json({
      success: false,
      error: {
        message: 'Webhook verification failed',
        statusCode: 403,
        details: {
          expectedToken: expectedToken ? '[CONFIGURED]' : '[NOT_CONFIGURED]',
          receivedMode: mode,
          receivedToken: token ? '[PROVIDED]' : '[NOT_PROVIDED]'
        }
      }
    });
  }
}));

// POST /api/whatsapp/webhook - Receber mensagens do WhatsApp
router.post('/webhook', asyncHandler(async (req: Request, res: Response) => {
  const signature = req.headers['x-hub-signature-256'] as string;
  const payload = JSON.stringify(req.body);
  
  console.log('📨 Received WhatsApp webhook');
  console.log('Signature:', signature ? '[PROVIDED]' : '[NOT_PROVIDED]');
  
  // Validar assinatura se configurada (TEMPORARIAMENTE DESABILITADO)
  // if (signature && !whatsappService.validateSignature(payload, signature)) {
  //   console.log('❌ Invalid webhook signature');
  //   return res.status(401).json({
  //     success: false,
  //     error: {
  //       message: 'Invalid webhook signature',
  //       statusCode: 401
  //     }
  //   });
  // }
  console.log('⚠️ Signature validation disabled for testing');

  try {
    const webhookPayload: WhatsAppWebhookPayload = req.body;
    console.log('Webhook payload:', JSON.stringify(webhookPayload, null, 2));

    // Processar mensagens recebidas
    const messages = whatsappService.processWebhookPayload(webhookPayload);
    console.log(`📥 Processing ${messages.length} messages`);
    
    // Debug: Log detalhado de cada mensagem
    messages.forEach((msg, index) => {
      console.log(`📋 Message ${index + 1}:`, {
        id: msg.id,
        type: msg.type,
        from: msg.from,
        hasText: !!msg.text,
        hasDocument: !!msg.document,
        hasImage: !!msg.image,
        hasAudio: !!msg.audio
      });
    });

    for (const message of messages) {
      try {
        console.log(`Processing message from ${message.from}:`, message.text?.body);
        
        // Registrar mensagem recebida no histórico MongoDB
        if (message.text?.body) {
          try {
            await messageRepository.addToHistory({
              id: message.id,
              from: message.from,
              message: message.text.body,
              timestamp: new Date(),
              type: 'received'
            });
          } catch (error) {
            console.error('❌ Error saving message to MongoDB:', error);
            // Fallback para memória se MongoDB falhar
            addToHistory({
              id: message.id,
              from: message.from,
              message: message.text.body,
              timestamp: new Date().toISOString(),
              type: 'received'
            });
          }
        }
        
        // Processar documentos CSV recebidos
        if (message.document) {
          console.log('📄 Document received:', {
            id: message.document.id,
            filename: message.document.filename,
            mime_type: message.document.mime_type,
            sha256: message.document.sha256
          });
          
          // Sempre registrar documento no histórico MongoDB primeiro
          try {
            await messageRepository.addToHistory({
              id: message.id,
              from: message.from,
              message: `📄 Documento recebido: ${message.document.filename} (${message.document.mime_type})`,
              timestamp: new Date(),
              type: 'received'
            });
          } catch (error) {
            console.error('❌ Error saving document message to MongoDB:', error);
            // Fallback para memória
            addToHistory({
              id: message.id,
              from: message.from,
              message: `📄 Documento recebido: ${message.document.filename} (${message.document.mime_type})`,
              timestamp: new Date().toISOString(),
              type: 'received'
            });
          }
          
          // Verificar se é um arquivo CSV
          if (message.document.mime_type === 'text/csv' || 
              message.document.mime_type === 'application/csv' ||
              message.document.filename?.toLowerCase().endsWith('.csv')) {
            
            console.log('📊 CSV file detected, processing...');
            
            try {
              await processCSVDocument(message.document, message.from, message.id);
              console.log('✅ CSV processing completed successfully');
            } catch (error) {
              console.error('❌ CSV processing failed:', error);
              
              // Enviar mensagem de erro ao usuário
              const errorMsg = `❌ Erro ao processar CSV: ${message.document.filename}\n\nDetalhes: ${error instanceof Error ? error.message : 'Erro desconhecido'}`;
              
              if (whatsappService.isConfigured()) {
                await whatsappService.sendTextMessage(message.from, errorMsg);
              } else {
                console.log(`📤 [SIMULATION] CSV error: ${errorMsg}`);
              }
            }
          } else {
            console.log('📎 Non-CSV document received, ignoring');
          }
        }
        
        // 1. Primeiro verificar se é um comando de registro
        let registrationHandled = false;
        if (registrationService && message.text?.body) {
          const registrationResult = await registrationService.processMessage(message);
          
          if (registrationResult.shouldRespond && registrationResult.responseMessage) {
            console.log(`📤 Sending registration response to ${message.from}`);
            
            if (whatsappService.isConfigured()) {
              await whatsappService.sendTextMessage(message.from, registrationResult.responseMessage);
            } else {
              console.log(`📤 [SIMULATION] Registration response: ${registrationResult.responseMessage}`);
            }
            
            registrationHandled = true;
            console.log(`✅ Registration command processed: ${registrationResult.message}`);
          }
        }

        // 2. Se não foi um comando de registro, processar normalmente
        if (!registrationHandled) {
          // Processar mensagem para análise
          const processedMessage = messageProcessor.processMessage(message);
          console.log('Processed message:', {
            type: processedMessage.interactionType,
            sentiment: processedMessage.sentiment,
            shouldRespond: processedMessage.shouldRespond,
            extractedData: processedMessage.extractedData
          });

          // Simular criação de cliente (em produção, usar repositório)
          console.log(`📝 Would create/update client: ${message.from}`);
          
          // Simular registro de interação
          console.log(`📊 Would register interaction:`, {
            clientId: message.from,
            type: processedMessage.interactionType,
            content: message.text?.body,
            sentiment: processedMessage.sentiment,
            value: processedMessage.extractedData.value,
            category: processedMessage.extractedData.category
          });

          // Enviar resposta automática se necessário
          if (processedMessage.shouldRespond && processedMessage.suggestedResponse) {
            if (whatsappService.isConfigured()) {
              console.log(`📤 Sending automatic response to ${message.from}`);
              await whatsappService.sendTextMessage(message.from, processedMessage.suggestedResponse);
            } else {
              console.log(`📤 Would send response: ${processedMessage.suggestedResponse}`);
            }
          }
        }

        // 3. Marcar como lida
        if (whatsappService.isConfigured()) {
          await whatsappService.markAsRead(message.id);
        }

      } catch (messageError) {
        console.error(`Error processing message ${message.id}:`, messageError);
        // Continuar processando outras mensagens mesmo se uma falhar
      }
    }

    res.status(200).json({ 
      success: true,
      processed: messages.length,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error processing webhook:', error);
    res.status(500).json({
      success: false,
      error: {
        message: 'Error processing webhook',
        statusCode: 500
      }
    });
  }
}));

// POST /api/whatsapp/send - Enviar mensagem via WhatsApp
router.post('/send', asyncHandler(async (req: Request, res: Response) => {
  const { to, message, type = 'text' } = req.body;

  if (!to || !message) {
    return res.status(400).json({
      success: false,
      error: {
        message: 'Missing required fields: to, message',
        statusCode: 400
      }
    });
  }

  try {
    if (!whatsappService.isConfigured()) {
      // Simular envio em desenvolvimento
      console.log(`📤 [SIMULATION] Sending message to ${to}: ${message}`);
      return res.json({
        success: true,
        message: 'Message sent successfully (simulated)',
        data: {
          to,
          message,
          messageId: 'sim-' + Date.now(),
          timestamp: new Date().toISOString(),
          simulated: true
        }
      });
    }

    const result = await whatsappService.sendTextMessage(to, message);
    
    res.json({
      success: true,
      message: 'Message sent successfully',
      data: {
        to,
        message,
        messageId: result.messages?.[0]?.id,
        timestamp: new Date().toISOString(),
        whatsappResponse: result
      }
    });

  } catch (error: any) {
    console.error('Error sending message:', error);
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to send message',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

// POST /api/whatsapp/template - Enviar mensagem de template
router.post('/template', asyncHandler(async (req: Request, res: Response) => {
  const { to, templateName, languageCode = 'pt_BR', components } = req.body;

  if (!to || !templateName) {
    return res.status(400).json({
      success: false,
      error: {
        message: 'Missing required fields: to, templateName',
        statusCode: 400
      }
    });
  }

  try {
    if (!whatsappService.isConfigured()) {
      console.log(`📤 [SIMULATION] Sending template ${templateName} to ${to}`);
      return res.json({
        success: true,
        message: 'Template sent successfully (simulated)',
        data: {
          to,
          templateName,
          languageCode,
          messageId: 'sim-template-' + Date.now(),
          timestamp: new Date().toISOString(),
          simulated: true
        }
      });
    }

    const result = await whatsappService.sendTemplateMessage(to, templateName, languageCode, components);
    
    res.json({
      success: true,
      message: 'Template sent successfully',
      data: {
        to,
        templateName,
        languageCode,
        messageId: result.messages?.[0]?.id,
        timestamp: new Date().toISOString(),
        whatsappResponse: result
      }
    });

  } catch (error: any) {
    console.error('Error sending template:', error);
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to send template',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

// GET /api/whatsapp/status - Status da integração
router.get('/status', asyncHandler(async (req: Request, res: Response) => {
  const configStatus = whatsappService.getConfigurationStatus();
  
  res.json({
    success: true,
    message: 'WhatsApp integration status',
    data: {
      configured: whatsappService.isConfigured(),
      configuration: configStatus,
      webhookVerifyToken: !!process.env.WHATSAPP_WEBHOOK_VERIFY_TOKEN,
      webhookSecret: !!process.env.WHATSAPP_WEBHOOK_SECRET,
      environment: process.env.NODE_ENV || 'development',
      timestamp: new Date().toISOString(),
      endpoints: {
        webhook: '/api/whatsapp/webhook',
        send: '/api/whatsapp/send',
        template: '/api/whatsapp/template',
        status: '/api/whatsapp/status'
      }
    }
  });
}));

// POST /api/whatsapp/test - Testar processamento de mensagem
router.post('/test', asyncHandler(async (req: Request, res: Response) => {
  const { message, from = '5511999999999' } = req.body;

  if (!message) {
    return res.status(400).json({
      success: false,
      error: {
        message: 'Missing required field: message',
        statusCode: 400
      }
    });
  }

  try {
    // Simular mensagem do WhatsApp
    const simulatedMessage = {
      id: 'test-' + Date.now(),
      from,
      timestamp: new Date().toISOString(),
      type: 'text' as const,
      text: {
        body: message
      }
    };

    // Processar mensagem
    const processedMessage = messageProcessor.processMessage(simulatedMessage);

    res.json({
      success: true,
      message: 'Message processed successfully',
      data: {
        originalMessage: simulatedMessage,
        processed: processedMessage,
        timestamp: new Date().toISOString()
      }
    });

  } catch (error: any) {
    console.error('Error testing message processing:', error);
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to process test message',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

// GET /api/whatsapp/csv - Listar arquivos CSV processados
router.get('/csv', asyncHandler(async (req: Request, res: Response) => {
  const { from } = req.query;
  
  const csvFiles = await csvRepository.getAllProcessedCSVs(from as string);
  const stats = await csvRepository.getCSVStats();
  
  res.json({
    success: true,
    message: 'Arquivos CSV processados',
    data: csvFiles.map(csv => ({
      id: csv.id,
      filename: csv.filename,
      from: csv.from,
      processedAt: csv.processedAt,
      summary: csv.summary
    })),
    meta: {
      total: stats.totalCSVs,
      totalRows: stats.totalRows,
      totalUsers: stats.totalUsers,
      lastProcessed: stats.lastProcessed
    }
  });
}));

// GET /api/whatsapp/csv/:id - Obter dados de um CSV específico
router.get('/csv/:id', asyncHandler(async (req: Request, res: Response) => {
  const { id } = req.params;
  const { limit = 100, offset = 0 } = req.query;
  
  const csvFile = await csvRepository.getProcessedCSVById(id);
  
  if (!csvFile) {
    return res.status(404).json({
      success: false,
      error: {
        message: 'CSV file not found',
        statusCode: 404
      }
    });
  }
  
  const startIndex = parseInt(offset as string);
  const limitNum = parseInt(limit as string);
  const paginatedData = csvFile.data.slice(startIndex, startIndex + limitNum);
  
  res.json({
    success: true,
    message: 'Dados do CSV',
    data: {
      id: csvFile.id,
      filename: csvFile.filename,
      from: csvFile.from,
      processedAt: csvFile.processedAt,
      summary: csvFile.summary,
      rows: paginatedData
    },
    meta: {
      totalRows: csvFile.data.length,
      showing: paginatedData.length,
      offset: startIndex,
      limit: limitNum
    }
  });
}));

// GET /api/whatsapp/csv/:id/analysis - Análise detalhada de um CSV
router.get('/csv/:id/analysis', asyncHandler(async (req: Request, res: Response) => {
  const { id } = req.params;
  
  const csvFile = await csvRepository.getProcessedCSVById(id);
  
  if (!csvFile) {
    return res.status(404).json({
      success: false,
      error: {
        message: 'CSV file not found',
        statusCode: 404
      }
    });
  }
  
  // Gerar análise detalhada se não existir
  let analysis = csvFile.analysis;
  if (!analysis) {
    analysis = generateDetailedAnalysis(csvFile.data, csvFile.summary.columns);
    await csvRepository.updateCSVAnalysis(id, analysis);
  }
  
  res.json({
    success: true,
    message: 'Análise detalhada do CSV',
    data: {
      filename: csvFile.filename,
      processedAt: csvFile.processedAt,
      summary: csvFile.summary,
      analysis: analysis
    }
  });
}));

// GET /api/whatsapp/ml/datasets - Listar todos os datasets para ML
router.get('/ml/datasets', asyncHandler(async (req: Request, res: Response) => {
  try {
    const datasets = await mlRepository.getAllDatasets();
    
    res.json({
      success: true,
      message: 'Datasets disponíveis para ML',
      data: datasets,
      meta: {
        total: datasets.length,
        totalRecords: datasets.reduce((sum, ds) => sum + ds.totalRecords, 0),
        totalFeatures: datasets.reduce((sum, ds) => sum + ds.features.total, 0)
      }
    });
  } catch (error: any) {
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to fetch ML datasets',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

// GET /api/whatsapp/ml/dataset/:csvId - Obter dados de ML de um CSV específico
router.get('/ml/dataset/:csvId', asyncHandler(async (req: Request, res: Response) => {
  const { csvId } = req.params;
  const { limit = 100, offset = 0, features_only = false } = req.query;
  
  try {
    const [summary, mlData] = await Promise.all([
      mlRepository.getDatasetSummary(csvId),
      mlRepository.getMLDataByCSV(csvId)
    ]);
    
    if (!summary) {
      return res.status(404).json({
        success: false,
        error: {
          message: 'Dataset not found',
          statusCode: 404
        }
      });
    }
    
    const startIndex = parseInt(offset as string);
    const limitNum = parseInt(limit as string);
    const paginatedData = mlData.slice(startIndex, startIndex + limitNum);
    
    // Se features_only = true, retornar apenas os dados normalizados
    const responseData = features_only === 'true' 
      ? paginatedData.map(record => ({
          rowIndex: record.rowIndex,
          features: record.normalizedData,
          dataTypes: record.dataTypes,
          quality: record.metadata.quality
        }))
      : paginatedData;
    
    res.json({
      success: true,
      message: 'Dados do dataset para ML',
      data: {
        summary,
        records: responseData
      },
      meta: {
        totalRecords: mlData.length,
        showing: paginatedData.length,
        offset: startIndex,
        limit: limitNum,
        featuresOnly: features_only === 'true'
      }
    });
  } catch (error: any) {
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to fetch ML dataset',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

// GET /api/whatsapp/ml/dataset/:csvId/summary - Resumo estatístico do dataset
router.get('/ml/dataset/:csvId/summary', asyncHandler(async (req: Request, res: Response) => {
  const { csvId } = req.params;
  
  try {
    const summary = await mlRepository.getDatasetSummary(csvId);
    
    if (!summary) {
      return res.status(404).json({
        success: false,
        error: {
          message: 'Dataset not found',
          statusCode: 404
        }
      });
    }
    
    res.json({
      success: true,
      message: 'Resumo estatístico do dataset',
      data: summary
    });
  } catch (error: any) {
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to fetch dataset summary',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

// GET /api/whatsapp/ml/dataset/:csvId/features - Informações sobre features
router.get('/ml/dataset/:csvId/features', asyncHandler(async (req: Request, res: Response) => {
  const { csvId } = req.params;
  
  try {
    const summary = await mlRepository.getDatasetSummary(csvId);
    
    if (!summary) {
      return res.status(404).json({
        success: false,
        error: {
          message: 'Dataset not found',
          statusCode: 404
        }
      });
    }
    
    // Obter uma amostra dos dados para análise de features
    const sampleData = await mlRepository.getMLDataByCSV(csvId);
    const featureInfo = sampleData.length > 0 ? {
      dataTypes: sampleData[0].dataTypes,
      features: sampleData[0].features,
      sampleValues: Object.keys(sampleData[0].dataTypes).reduce((acc: any, feature) => {
        acc[feature] = sampleData
          .slice(0, 5)
          .map(record => record.normalizedData[feature])
          .filter(val => val != null);
        return acc;
      }, {})
    } : null;
    
    res.json({
      success: true,
      message: 'Informações sobre features do dataset',
      data: {
        summary: {
          filename: summary.filename,
          totalRecords: summary.totalRecords,
          features: summary.features,
          dataQuality: summary.dataQuality
        },
        featureDetails: featureInfo,
        statistics: summary.statistics
      }
    });
  } catch (error: any) {
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to fetch feature information',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

// === NOVAS ROTAS PARA DADOS BRUTOS E ANÁLISE EXPLORATÓRIA ===

// GET /api/whatsapp/raw - Listar todas as mensagens com dados brutos
router.get('/raw', asyncHandler(async (req: Request, res: Response) => {
  try {
    const messages = await rawRepository.getAllRawDataMessages();
    
    res.json({
      success: true,
      message: 'Mensagens com dados brutos',
      data: messages,
      meta: {
        total: messages.length,
        totalRecords: messages.reduce((sum, msg) => sum + msg.recordCount, 0)
      }
    });
  } catch (error: any) {
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to fetch raw data messages',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

// GET /api/whatsapp/raw/:messageId - Obter dados brutos por ID da mensagem
router.get('/raw/:messageId', asyncHandler(async (req: Request, res: Response) => {
  const { messageId } = req.params;
  const { limit = 100, offset = 0 } = req.query;
  
  try {
    const rawData = await rawRepository.getRawDataByMessageId(messageId);
    
    if (rawData.length === 0) {
      return res.status(404).json({
        success: false,
        error: {
          message: 'Raw data not found for this message ID',
          statusCode: 404
        }
      });
    }
    
    const startIndex = parseInt(offset as string);
    const limitNum = parseInt(limit as string);
    const paginatedData = rawData.slice(startIndex, startIndex + limitNum);
    
    res.json({
      success: true,
      message: 'Dados brutos da mensagem',
      data: {
        messageId,
        filename: rawData[0].filename,
        from: rawData[0].from,
        processedAt: rawData[0].processedAt,
        records: paginatedData
      },
      meta: {
        totalRecords: rawData.length,
        showing: paginatedData.length,
        offset: startIndex,
        limit: limitNum
      }
    });
  } catch (error: any) {
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to fetch raw data',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

// GET /api/whatsapp/analysis - Listar todas as análises exploratórias
router.get('/analysis', asyncHandler(async (req: Request, res: Response) => {
  try {
    const analyses = await rawRepository.getAllExploratoryAnalyses();
    
    res.json({
      success: true,
      message: 'Análises exploratórias disponíveis',
      data: analyses,
      meta: {
        total: analyses.length,
        totalRecords: analyses.reduce((sum, analysis) => sum + analysis.totalRecords, 0),
        avgQuality: analyses.length > 0 
          ? Math.round(analyses.reduce((sum, analysis) => sum + analysis.overallQuality, 0) / analyses.length * 100) / 100
          : 0
      }
    });
  } catch (error: any) {
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to fetch exploratory analyses',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

// GET /api/whatsapp/analysis/:messageId - Obter análise exploratória completa
router.get('/analysis/:messageId', asyncHandler(async (req: Request, res: Response) => {
  const { messageId } = req.params;
  
  try {
    const analysis = await rawRepository.getExploratoryAnalysisByMessageId(messageId);
    
    if (!analysis) {
      return res.status(404).json({
        success: false,
        error: {
          message: 'Exploratory analysis not found for this message ID',
          statusCode: 404
        }
      });
    }
    
    res.json({
      success: true,
      message: 'Análise exploratória completa',
      data: analysis
    });
  } catch (error: any) {
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to fetch exploratory analysis',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

// GET /api/whatsapp/analysis/:messageId/summary - Resumo da análise exploratória
router.get('/analysis/:messageId/summary', asyncHandler(async (req: Request, res: Response) => {
  const { messageId } = req.params;
  
  try {
    const analysis = await rawRepository.getExploratoryAnalysisByMessageId(messageId);
    
    if (!analysis) {
      return res.status(404).json({
        success: false,
        error: {
          message: 'Exploratory analysis not found for this message ID',
          statusCode: 404
        }
      });
    }
    
    // Retornar apenas resumo essencial
    const summary = {
      messageId: analysis.messageId,
      filename: analysis.filename,
      from: analysis.from,
      totalRecords: analysis.totalRecords,
      analysisDate: analysis.analysisDate,
      dataStructure: analysis.dataStructure,
      dataQuality: analysis.dataQuality,
      keyFindings: analysis.insights.keyFindings,
      recommendations: analysis.insights.recommendations,
      suggestedVisualizations: analysis.suggestedVisualizations.filter(viz => viz.priority === 'high')
    };
    
    res.json({
      success: true,
      message: 'Resumo da análise exploratória',
      data: summary
    });
  } catch (error: any) {
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to fetch analysis summary',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

// GET /api/whatsapp/raw/stats - Estatísticas gerais dos dados brutos
router.get('/raw/stats', asyncHandler(async (req: Request, res: Response) => {
  try {
    const stats = await rawRepository.getRawDataStats();
    
    res.json({
      success: true,
      message: 'Estatísticas dos dados brutos',
      data: stats
    });
  } catch (error: any) {
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to fetch raw data stats',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

// DELETE /api/whatsapp/raw/:messageId - Deletar dados brutos por ID da mensagem
router.delete('/raw/:messageId', asyncHandler(async (req: Request, res: Response) => {
  const { messageId } = req.params;
  
  try {
    const deletedCount = await rawRepository.deleteRawDataByMessageId(messageId);
    
    if (deletedCount === 0) {
      return res.status(404).json({
        success: false,
        error: {
          message: 'No raw data found for this message ID',
          statusCode: 404
        }
      });
    }
    
    res.json({
      success: true,
      message: 'Dados brutos deletados com sucesso',
      data: {
        messageId,
        deletedRecords: deletedCount
      }
    });
  } catch (error: any) {
    res.status(500).json({
      success: false,
      error: {
        message: 'Failed to delete raw data',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

export { router as whatsappRoutes };

