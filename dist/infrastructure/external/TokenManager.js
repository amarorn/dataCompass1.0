"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.TokenManager = void 0;
const axios_1 = __importDefault(require("axios"));
class TokenManager {
    constructor() {
        this.currentToken = process.env.WHATSAPP_TOKEN || '';
        this.appId = process.env.FACEBOOK_APP_ID || '';
        this.appSecret = process.env.FACEBOOK_APP_SECRET || '';
    }
    /**
     * Verifica se o token atual está próximo do vencimento
     */
    isTokenExpiringSoon() {
        if (!this.expiryTime)
            return false;
        const now = new Date();
        const timeUntilExpiry = this.expiryTime.getTime() - now.getTime();
        const hoursUntilExpiry = timeUntilExpiry / (1000 * 60 * 60);
        // Renovar se restam menos de 24 horas
        return hoursUntilExpiry < 24;
    }
    /**
     * Obtém informações sobre o token atual
     */
    async getTokenInfo() {
        try {
            const response = await axios_1.default.get(`https://graph.facebook.com/v18.0/me?access_token=${this.currentToken}`);
            return response.data;
        }
        catch (error) {
            console.error('Erro ao obter informações do token:', error);
            throw error;
        }
    }
    /**
     * Converte token de curta duração em longa duração
     */
    async exchangeForLongLivedToken() {
        if (!this.appId || !this.appSecret) {
            throw new Error('APP_ID e APP_SECRET são necessários para renovação automática');
        }
        try {
            const response = await axios_1.default.get(`https://graph.facebook.com/v18.0/oauth/access_token`, {
                params: {
                    grant_type: 'fb_exchange_token',
                    client_id: this.appId,
                    client_secret: this.appSecret,
                    fb_exchange_token: this.currentToken
                }
            });
            const tokenInfo = response.data;
            this.currentToken = tokenInfo.access_token;
            // Calcular tempo de expiração (60 dias para long-lived token)
            if (tokenInfo.expires_in) {
                this.expiryTime = new Date(Date.now() + (tokenInfo.expires_in * 1000));
            }
            console.log('✅ Token renovado com sucesso!');
            console.log(`🕒 Nova expiração: ${this.expiryTime?.toISOString()}`);
            return this.currentToken;
        }
        catch (error) {
            console.error('❌ Erro ao renovar token:', error.response?.data || error.message);
            throw error;
        }
    }
    /**
     * Obtém o token atual (renovando se necessário)
     */
    async getCurrentToken() {
        if (this.isTokenExpiringSoon()) {
            console.log('🔄 Token expirando em breve, renovando...');
            await this.exchangeForLongLivedToken();
        }
        return this.currentToken;
    }
    /**
     * Força a renovação do token
     */
    async refreshTokenMethod() {
        return await this.exchangeForLongLivedToken();
    }
    /**
     * Verifica se o token atual é válido
     */
    async validateToken() {
        try {
            await this.getTokenInfo();
            return true;
        }
        catch (error) {
            return false;
        }
    }
}
exports.TokenManager = TokenManager;
//# sourceMappingURL=TokenManager.js.map