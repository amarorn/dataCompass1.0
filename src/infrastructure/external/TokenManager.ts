import axios from 'axios';

export interface TokenInfo {
  access_token: string;
  token_type: string;
  expires_in?: number;
}

export class TokenManager {
  private currentToken: string;
  private refreshTokenValue?: string;
  private appId: string;
  private appSecret: string;
  private expiryTime?: Date;

  constructor() {
    this.currentToken = process.env.WHATSAPP_TOKEN || '';
    this.appId = process.env.FACEBOOK_APP_ID || '';
    this.appSecret = process.env.FACEBOOK_APP_SECRET || '';
  }

  /**
   * Verifica se o token atual está próximo do vencimento
   */
  public isTokenExpiringSoon(): boolean {
    if (!this.expiryTime) return false;
    
    const now = new Date();
    const timeUntilExpiry = this.expiryTime.getTime() - now.getTime();
    const hoursUntilExpiry = timeUntilExpiry / (1000 * 60 * 60);
    
    // Renovar se restam menos de 24 horas
    return hoursUntilExpiry < 24;
  }

  /**
   * Obtém informações sobre o token atual
   */
  public async getTokenInfo(): Promise<any> {
    try {
      const response = await axios.get(
        `https://graph.facebook.com/v18.0/me?access_token=${this.currentToken}`
      );
      return response.data;
    } catch (error) {
      console.error('Erro ao obter informações do token:', error);
      throw error;
    }
  }

  /**
   * Converte token de curta duração em longa duração
   */
  public async exchangeForLongLivedToken(): Promise<string> {
    if (!this.appId || !this.appSecret) {
      throw new Error('APP_ID e APP_SECRET são necessários para renovação automática');
    }

    try {
      const response = await axios.get(
        `https://graph.facebook.com/v18.0/oauth/access_token`,
        {
          params: {
            grant_type: 'fb_exchange_token',
            client_id: this.appId,
            client_secret: this.appSecret,
            fb_exchange_token: this.currentToken
          }
        }
      );

      const tokenInfo: TokenInfo = response.data;
      this.currentToken = tokenInfo.access_token;
      
      // Calcular tempo de expiração (60 dias para long-lived token)
      if (tokenInfo.expires_in) {
        this.expiryTime = new Date(Date.now() + (tokenInfo.expires_in * 1000));
      }

      console.log('✅ Token renovado com sucesso!');
      console.log(`🕒 Nova expiração: ${this.expiryTime?.toISOString()}`);
      
      return this.currentToken;
    } catch (error: any) {
      console.error('❌ Erro ao renovar token:', error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Obtém o token atual (renovando se necessário)
   */
  public async getCurrentToken(): Promise<string> {
    if (this.isTokenExpiringSoon()) {
      console.log('🔄 Token expirando em breve, renovando...');
      await this.exchangeForLongLivedToken();
    }
    
    return this.currentToken;
  }

  /**
   * Força a renovação do token
   */
  public async refreshTokenMethod(): Promise<string> {
    return await this.exchangeForLongLivedToken();
  }

  /**
   * Verifica se o token atual é válido
   */
  public async validateToken(): Promise<boolean> {
    try {
      await this.getTokenInfo();
      return true;
    } catch (error) {
      return false;
    }
  }
}
