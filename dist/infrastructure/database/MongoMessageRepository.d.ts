export interface MessageDocument {
    _id?: string;
    id: string;
    from?: string;
    to?: string;
    message: string;
    timestamp: Date;
    type: 'sent' | 'received';
}
export declare class MongoMessageRepository {
    private connection;
    constructor();
    /**
     * Adicionar mensagem ao histórico
     */
    addToHistory(messageData: Omit<MessageDocument, '_id'>): Promise<string>;
    /**
     * Buscar histórico completo
     */
    getHistory(): Promise<MessageDocument[]>;
    /**
     * Buscar mensagens recebidas
     */
    getReceivedMessages(): Promise<MessageDocument[]>;
    /**
     * Buscar mensagens enviadas
     */
    getSentMessages(): Promise<MessageDocument[]>;
    /**
     * Buscar mensagens de um usuário específico
     */
    getUserMessages(phoneNumber: string): Promise<MessageDocument[]>;
    /**
     * Obter estatísticas das mensagens
     */
    getMessageStats(): Promise<{
        total: number;
        received: number;
        sent: number;
        lastReceived: Date | null;
        lastSent: Date | null;
    }>;
    /**
     * Limpar mensagens antigas (mais de X dias)
     */
    cleanOldMessages(daysToKeep?: number): Promise<number>;
}
//# sourceMappingURL=MongoMessageRepository.d.ts.map