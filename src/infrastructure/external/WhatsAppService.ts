import crypto from 'crypto';
import axios from 'axios';

export interface WhatsAppMessage {
  id: string;
  from: string;
  timestamp: string;
  type: 'text' | 'image' | 'audio' | 'video' | 'document' | 'location';
  text?: {
    body: string;
  };
  image?: {
    id: string;
    mime_type: string;
    sha256: string;
  };
  audio?: {
    id: string;
    mime_type: string;
  };
  location?: {
    latitude: number;
    longitude: number;
    name?: string;
    address?: string;
  };
}

export interface WhatsAppWebhookPayload {
  object: string;
  entry: Array<{
    id: string;
    changes: Array<{
      value: {
        messaging_product: string;
        metadata: {
          display_phone_number: string;
          phone_number_id: string;
        };
        contacts?: Array<{
          profile: {
            name: string;
          };
          wa_id: string;
        }>;
        messages?: WhatsAppMessage[];
        statuses?: Array<{
          id: string;
          status: string;
          timestamp: string;
          recipient_id: string;
        }>;
      };
      field: string;
    }>;
  }>;
}

export interface SendMessageRequest {
  messaging_product: 'whatsapp';
  to: string;
  type: 'text' | 'template';
  text?: {
    body: string;
  };
  template?: {
    name: string;
    language: {
      code: string;
    };
    components?: any[];
  };
}

export class WhatsAppService {
  private readonly accessToken: string;
  private readonly phoneNumberId: string;
  private readonly webhookSecret: string;
  private readonly apiVersion: string = 'v21.0';
  private readonly baseUrl: string;

  constructor() {
    this.accessToken = process.env.WHATSAPP_TOKEN || '';
    this.phoneNumberId = process.env.WHATSAPP_PHONE_NUMBER_ID || '';
    this.webhookSecret = process.env.WHATSAPP_WEBHOOK_SECRET || '';
    this.baseUrl = `https://graph.facebook.com/${this.apiVersion}`;

    if (!this.accessToken) {
      console.warn('WHATSAPP_TOKEN not configured');
    }
    if (!this.phoneNumberId) {
      console.warn('WHATSAPP_PHONE_NUMBER_ID not configured');
    }
    if (!this.webhookSecret) {
      console.warn('WHATSAPP_WEBHOOK_SECRET not configured');
    }
  }

  /**
   * Valida a assinatura do webhook do WhatsApp
   */
  public validateSignature(payload: string, signature: string): boolean {
    if (!this.webhookSecret) {
      console.warn('Webhook secret not configured, skipping signature validation');
      return true; // Em desenvolvimento, permitir sem validação
    }

    try {
      const expectedSignature = crypto
        .createHmac('sha256', this.webhookSecret)
        .update(payload)
        .digest('hex');

      const receivedSignature = signature.replace('sha256=', '');
      
      return crypto.timingSafeEqual(
        Buffer.from(expectedSignature, 'hex'),
        Buffer.from(receivedSignature, 'hex')
      );
    } catch (error) {
      console.error('Error validating webhook signature:', error);
      return false;
    }
  }

  /**
   * Processa o payload do webhook
   */
  public processWebhookPayload(payload: WhatsAppWebhookPayload): WhatsAppMessage[] {
    const messages: WhatsAppMessage[] = [];

    if (payload.object !== 'whatsapp_business_account') {
      console.warn('Received webhook for unknown object:', payload.object);
      return messages;
    }

    payload.entry?.forEach(entry => {
      entry.changes?.forEach(change => {
        if (change.field === 'messages' && change.value.messages) {
          messages.push(...change.value.messages);
        }
      });
    });

    return messages;
  }

  /**
   * Envia uma mensagem de texto via WhatsApp
   */
  public async sendTextMessage(to: string, message: string): Promise<any> {
    if (!this.accessToken || !this.phoneNumberId) {
      throw new Error('WhatsApp credentials not configured');
    }

    const payload: SendMessageRequest = {
      messaging_product: 'whatsapp',
      to: to.replace(/\D/g, ''), // Remove caracteres não numéricos
      type: 'text',
      text: {
        body: message
      }
    };

    try {
      const response = await axios.post(
        `${this.baseUrl}/${this.phoneNumberId}/messages`,
        payload,
        {
          headers: {
            'Authorization': `Bearer ${this.accessToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      console.log('Message sent successfully:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Error sending WhatsApp message:', error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Envia uma mensagem de template via WhatsApp
   */
  public async sendTemplateMessage(
    to: string, 
    templateName: string, 
    languageCode: string = 'pt_BR',
    components?: any[]
  ): Promise<any> {
    if (!this.accessToken || !this.phoneNumberId) {
      throw new Error('WhatsApp credentials not configured');
    }

    const payload: SendMessageRequest = {
      messaging_product: 'whatsapp',
      to: to.replace(/\D/g, ''),
      type: 'template',
      template: {
        name: templateName,
        language: {
          code: languageCode
        },
        components: components || []
      }
    };

    try {
      const response = await axios.post(
        `${this.baseUrl}/${this.phoneNumberId}/messages`,
        payload,
        {
          headers: {
            'Authorization': `Bearer ${this.accessToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      console.log('Template message sent successfully:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Error sending WhatsApp template:', error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Marca uma mensagem como lida
   */
  public async markAsRead(messageId: string): Promise<any> {
    if (!this.accessToken || !this.phoneNumberId) {
      throw new Error('WhatsApp credentials not configured');
    }

    try {
      const response = await axios.post(
        `${this.baseUrl}/${this.phoneNumberId}/messages`,
        {
          messaging_product: 'whatsapp',
          status: 'read',
          message_id: messageId
        },
        {
          headers: {
            'Authorization': `Bearer ${this.accessToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      return response.data;
    } catch (error: any) {
      console.error('Error marking message as read:', error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Obtém informações do perfil de um contato
   */
  public async getContactProfile(phoneNumber: string): Promise<any> {
    if (!this.accessToken) {
      throw new Error('WhatsApp access token not configured');
    }

    try {
      const response = await axios.get(
        `${this.baseUrl}/${phoneNumber.replace(/\D/g, '')}`,
        {
          headers: {
            'Authorization': `Bearer ${this.accessToken}`
          }
        }
      );

      return response.data;
    } catch (error: any) {
      console.error('Error getting contact profile:', error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Verifica se as credenciais estão configuradas
   */
  public isConfigured(): boolean {
    // Verificar se os tokens são placeholders
    const isPlaceholderToken = this.accessToken.includes('your-') || this.accessToken.includes('token-here');
    const isPlaceholderPhoneId = this.phoneNumberId.includes('your-') || this.phoneNumberId.includes('id-here');
    
    if (isPlaceholderToken || isPlaceholderPhoneId) {
      console.log('🔧 WhatsApp tokens are placeholders, using simulation mode');
      return false; // Usar modo simulação
    }
    
    return !!(this.accessToken && this.phoneNumberId);
  }

  /**
   * Obtém status da configuração
   */
  public getConfigurationStatus(): {
    accessToken: boolean;
    phoneNumberId: boolean;
    webhookSecret: boolean;
  } {
    return {
      accessToken: !!this.accessToken,
      phoneNumberId: !!this.phoneNumberId,
      webhookSecret: !!this.webhookSecret
    };
  }
}

