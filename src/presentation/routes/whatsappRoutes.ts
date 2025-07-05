import { Router, Request, Response } from 'express';
import { asyncHandler } from '../middlewares/errorHandler';
import { WhatsAppService, WhatsAppWebhookPayload } from '../../infrastructure/external/WhatsAppService';
import { MessageProcessorService } from '../../application/services/MessageProcessorService';
import { Client } from '../../domain/entities/Client';
import { Interaction } from '../../domain/entities/Interaction';

const router = Router();
const whatsappService = new WhatsAppService();
const messageProcessor = new MessageProcessorService();

// GET /api/whatsapp/webhook - Verificação do webhook
router.get('/webhook', asyncHandler(async (req: Request, res: Response) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  console.log('Webhook verification request:', { mode, token });

  if (mode === 'subscribe' && token === process.env.WHATSAPP_WEBHOOK_VERIFY_TOKEN) {
    console.log('✅ Webhook verified successfully');
    res.status(200).send(challenge);
  } else {
    console.log('❌ Webhook verification failed');
    res.status(403).json({
      success: false,
      error: {
        message: 'Webhook verification failed',
        statusCode: 403,
        details: {
          expectedToken: process.env.WHATSAPP_WEBHOOK_VERIFY_TOKEN ? '[CONFIGURED]' : '[NOT_CONFIGURED]',
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
  
  // Validar assinatura se configurada
  if (signature && !whatsappService.validateSignature(payload, signature)) {
    console.log('❌ Invalid webhook signature');
    return res.status(401).json({
      success: false,
      error: {
        message: 'Invalid webhook signature',
        statusCode: 401
      }
    });
  }

  try {
    const webhookPayload: WhatsAppWebhookPayload = req.body;
    console.log('Webhook payload:', JSON.stringify(webhookPayload, null, 2));

    // Processar mensagens recebidas
    const messages = whatsappService.processWebhookPayload(webhookPayload);
    console.log(`📥 Processing ${messages.length} messages`);

    for (const message of messages) {
      try {
        console.log(`Processing message from ${message.from}:`, message.text?.body);
        
        // Processar mensagem
        const processedMessage = messageProcessor.processMessage(message);
        console.log('Processed message:', {
          type: processedMessage.interactionType,
          sentiment: processedMessage.sentiment,
          shouldRespond: processedMessage.shouldRespond,
          extractedData: processedMessage.extractedData
        });

        // Marcar como lida
        if (whatsappService.isConfigured()) {
          await whatsappService.markAsRead(message.id);
        }

        // Aqui seria implementada a lógica para:
        // 1. Buscar ou criar cliente
        // 2. Registrar interação
        // 3. Gerar insights
        // 4. Enviar resposta automática

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

export { router as whatsappRoutes };

