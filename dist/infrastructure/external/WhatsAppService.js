"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.WhatsAppService = void 0;
const crypto_1 = __importDefault(require("crypto"));
const axios_1 = __importDefault(require("axios"));
const form_data_1 = __importDefault(require("form-data"));
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
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
     * Envia uma mensagem de texto (alias para sendTextMessage)
     */
    async sendMessage(to, message) {
        return this.sendTextMessage(to, message);
    }
    /**
     * Envia um documento/arquivo via WhatsApp
     */
    async sendDocument(to, filePath, caption) {
        if (!this.accessToken || !this.phoneNumberId) {
            console.error('WhatsApp credentials not configured');
            return false;
        }
        try {
            // Verificar se o arquivo existe
            if (!fs_1.default.existsSync(filePath)) {
                console.error(`Arquivo não encontrado: ${filePath}`);
                return false;
            }
            const fileName = path_1.default.basename(filePath);
            const isImage = this.isImageFile(filePath);
            console.log(`📎 Enviando ${isImage ? 'imagem' : 'documento'}: ${fileName} para ${to}`);
            // Primeiro, fazer upload do arquivo
            const uploadResult = await this.uploadMedia(filePath);
            if (!uploadResult.success || !uploadResult.mediaId) {
                console.error('Falha no upload do arquivo:', uploadResult.error);
                return false;
            }
            // Criar payload baseado no tipo de arquivo
            let payload;
            if (isImage) {
                // Para imagens PNG/JPEG usar type: 'image'
                payload = {
                    messaging_product: 'whatsapp',
                    to: to.replace(/\D/g, ''),
                    type: 'image',
                    image: {
                        id: uploadResult.mediaId,
                        caption: caption || ''
                    }
                };
            }
            else {
                // Para outros arquivos usar type: 'document'
                payload = {
                    messaging_product: 'whatsapp',
                    to: to.replace(/\D/g, ''),
                    type: 'document',
                    document: {
                        id: uploadResult.mediaId,
                        caption: caption || '',
                        filename: fileName
                    }
                };
            }
            const response = await axios_1.default.post(`${this.baseUrl}/${this.phoneNumberId}/messages`, payload, {
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`,
                    'Content-Type': 'application/json'
                }
            });
            console.log(`✅ ${isImage ? 'Imagem' : 'Documento'} enviado com sucesso:`, response.data);
            return true;
        }
        catch (error) {
            console.error('❌ Erro ao enviar arquivo:', error.response?.data || error.message);
            return false;
        }
    }
    /**
     * Faz upload de um arquivo para o WhatsApp
     */
    async uploadMedia(filePath) {
        try {
            const formData = new form_data_1.default();
            formData.append('file', fs_1.default.createReadStream(filePath));
            formData.append('type', this.getMimeType(filePath));
            formData.append('messaging_product', 'whatsapp');
            const response = await axios_1.default.post(`${this.baseUrl}/${this.phoneNumberId}/media`, formData, {
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`,
                    ...formData.getHeaders()
                }
            });
            if (response.data && response.data.id) {
                console.log(`✅ Upload concluído, Media ID: ${response.data.id}`);
                return {
                    success: true,
                    mediaId: response.data.id
                };
            }
            else {
                return {
                    success: false,
                    error: 'Resposta inválida do upload'
                };
            }
        }
        catch (error) {
            console.error('❌ Erro no upload:', error.response?.data || error.message);
            return {
                success: false,
                error: error.response?.data?.error?.message || error.message
            };
        }
    }
    /**
     * Verifica se o arquivo é uma imagem
     */
    isImageFile(filePath) {
        const ext = path_1.default.extname(filePath).toLowerCase();
        const imageExtensions = ['.png', '.jpg', '.jpeg', '.gif'];
        return imageExtensions.includes(ext);
    }
    /**
     * Determina o MIME type baseado na extensão do arquivo
     */
    getMimeType(filePath) {
        const ext = path_1.default.extname(filePath).toLowerCase();
        const mimeTypes = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.txt': 'text/plain',
            '.csv': 'text/csv'
        };
        return mimeTypes[ext] || 'application/octet-stream';
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