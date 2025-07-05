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
export declare class WhatsAppService {
    private readonly accessToken;
    private readonly phoneNumberId;
    private readonly webhookSecret;
    private readonly apiVersion;
    private readonly baseUrl;
    constructor();
    /**
     * Valida a assinatura do webhook do WhatsApp
     */
    validateSignature(payload: string, signature: string): boolean;
    /**
     * Processa o payload do webhook
     */
    processWebhookPayload(payload: WhatsAppWebhookPayload): WhatsAppMessage[];
    /**
     * Envia uma mensagem de texto via WhatsApp
     */
    sendTextMessage(to: string, message: string): Promise<any>;
    /**
     * Envia uma mensagem de template via WhatsApp
     */
    sendTemplateMessage(to: string, templateName: string, languageCode?: string, components?: any[]): Promise<any>;
    /**
     * Marca uma mensagem como lida
     */
    markAsRead(messageId: string): Promise<any>;
    /**
     * Obtém informações do perfil de um contato
     */
    getContactProfile(phoneNumber: string): Promise<any>;
    /**
     * Verifica se as credenciais estão configuradas
     */
    isConfigured(): boolean;
    /**
     * Obtém status da configuração
     */
    getConfigurationStatus(): {
        accessToken: boolean;
        phoneNumberId: boolean;
        webhookSecret: boolean;
    };
}
//# sourceMappingURL=WhatsAppService.d.ts.map