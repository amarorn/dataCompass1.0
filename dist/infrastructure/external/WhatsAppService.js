"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.WhatsAppService = void 0;
const crypto_1 = __importDefault(require("crypto"));
const axios_1 = __importDefault(require("axios"));
class WhatsAppService {
    constructor() {
        this.apiVersion = 'v21.0';
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
    validateSignature(payload, signature) {
        if (!this.webhookSecret) {
            console.warn('Webhook secret not configured, skipping signature validation');
            return true; // Em desenvolvimento, permitir sem validação
        }
        try {
            const expectedSignature = crypto_1.default
                .createHmac('sha256', this.webhookSecret)
                .update(payload)
                .digest('hex');
            const receivedSignature = signature.replace('sha256=', '');
            return crypto_1.default.timingSafeEqual(Buffer.from(expectedSignature, 'hex'), Buffer.from(receivedSignature, 'hex'));
        }
        catch (error) {
            console.error('Error validating webhook signature:', error);
            return false;
        }
    }
    /**
     * Processa o payload do webhook
     */
    processWebhookPayload(payload) {
        const messages = [];
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
    async sendTextMessage(to, message) {
        if (!this.accessToken || !this.phoneNumberId) {
            throw new Error('WhatsApp credentials not configured');
        }
        const payload = {
            messaging_product: 'whatsapp',
            to: to.replace(/\D/g, ''), // Remove caracteres não numéricos
            type: 'text',
            text: {
                body: message
            }
        };
        try {
            const response = await axios_1.default.post(`${this.baseUrl}/${this.phoneNumberId}/messages`, payload, {
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`,
                    'Content-Type': 'application/json'
                }
            });
            console.log('Message sent successfully:', response.data);
            return response.data;
        }
        catch (error) {
            console.error('Error sending WhatsApp message:', error.response?.data || error.message);
            throw error;
        }
    }
    /**
     * Envia uma mensagem de template via WhatsApp
     */
    async sendTemplateMessage(to, templateName, languageCode = 'pt_BR', components) {
        if (!this.accessToken || !this.phoneNumberId) {
            throw new Error('WhatsApp credentials not configured');
        }
        const payload = {
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
            const response = await axios_1.default.post(`${this.baseUrl}/${this.phoneNumberId}/messages`, payload, {
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`,
                    'Content-Type': 'application/json'
                }
            });
            console.log('Template message sent successfully:', response.data);
            return response.data;
        }
        catch (error) {
            console.error('Error sending WhatsApp template:', error.response?.data || error.message);
            throw error;
        }
    }
    /**
     * Marca uma mensagem como lida
     */
    async markAsRead(messageId) {
        if (!this.accessToken || !this.phoneNumberId) {
            throw new Error('WhatsApp credentials not configured');
        }
        try {
            const response = await axios_1.default.post(`${this.baseUrl}/${this.phoneNumberId}/messages`, {
                messaging_product: 'whatsapp',
                status: 'read',
                message_id: messageId
            }, {
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`,
                    'Content-Type': 'application/json'
                }
            });
            return response.data;
        }
        catch (error) {
            console.error('Error marking message as read:', error.response?.data || error.message);
            throw error;
        }
    }
    /**
     * Obtém informações do perfil de um contato
     */
    async getContactProfile(phoneNumber) {
        if (!this.accessToken) {
            throw new Error('WhatsApp access token not configured');
        }
        try {
            const response = await axios_1.default.get(`${this.baseUrl}/${phoneNumber.replace(/\D/g, '')}`, {
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`
                }
            });
            return response.data;
        }
        catch (error) {
            console.error('Error getting contact profile:', error.response?.data || error.message);
            throw error;
        }
    }
    /**
     * Verifica se as credenciais estão configuradas
     */
    isConfigured() {
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
    getConfigurationStatus() {
        return {
            accessToken: !!this.accessToken,
            phoneNumberId: !!this.phoneNumberId,
            webhookSecret: !!this.webhookSecret
        };
    }
}
exports.WhatsAppService = WhatsAppService;
//# sourceMappingURL=WhatsAppService.js.map