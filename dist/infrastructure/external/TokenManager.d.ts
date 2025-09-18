export interface TokenInfo {
    access_token: string;
    token_type: string;
    expires_in?: number;
}
export declare class TokenManager {
    private currentToken;
    private refreshTokenValue?;
    private appId;
    private appSecret;
    private expiryTime?;
    constructor();
    /**
     * Verifica se o token atual está próximo do vencimento
     */
    isTokenExpiringSoon(): boolean;
    /**
     * Obtém informações sobre o token atual
     */
    getTokenInfo(): Promise<any>;
    /**
     * Converte token de curta duração em longa duração
     */
    exchangeForLongLivedToken(): Promise<string>;
    /**
     * Obtém o token atual (renovando se necessário)
     */
    getCurrentToken(): Promise<string>;
    /**
     * Força a renovação do token
     */
    refreshTokenMethod(): Promise<string>;
    /**
     * Verifica se o token atual é válido
     */
    validateToken(): Promise<boolean>;
}
//# sourceMappingURL=TokenManager.d.ts.map