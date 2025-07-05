import { Interaction, InteractionType, SentimentType } from '@domain/entities/Interaction';
export interface IInteractionRepository {
    create(interaction: Interaction): Promise<Interaction>;
    findById(id: string): Promise<Interaction | null>;
    update(interaction: Interaction): Promise<Interaction>;
    delete(id: string): Promise<void>;
    findByClientId(clientId: string, page?: number, limit?: number): Promise<Interaction[]>;
    findRecentByClientId(clientId: string, days: number): Promise<Interaction[]>;
    findPurchasesByClientId(clientId: string): Promise<Interaction[]>;
    findComplaintsByClientId(clientId: string): Promise<Interaction[]>;
    findByType(type: InteractionType, page?: number, limit?: number): Promise<Interaction[]>;
    findBySentiment(sentiment: SentimentType, page?: number, limit?: number): Promise<Interaction[]>;
    findByCategory(category: string, page?: number, limit?: number): Promise<Interaction[]>;
    findByDateRange(startDate: Date, endDate: Date): Promise<Interaction[]>;
    findByClientAndDateRange(clientId: string, startDate: Date, endDate: Date): Promise<Interaction[]>;
    count(): Promise<number>;
    countByClient(clientId: string): Promise<number>;
    countByType(): Promise<Record<string, number>>;
    countBySentiment(): Promise<Record<string, number>>;
    countByCategory(): Promise<Record<string, number>>;
    getTotalValueByClient(clientId: string): Promise<number>;
    getAverageValueByClient(clientId: string): Promise<number>;
    getTotalValueByCategory(): Promise<Record<string, number>>;
    getTotalValueByDateRange(startDate: Date, endDate: Date): Promise<number>;
    getInteractionFrequencyByClient(clientId: string): Promise<number>;
    getLastInteractionByClient(clientId: string): Promise<Interaction | null>;
    getDaysSinceLastInteraction(clientId: string): Promise<number>;
    search(query: string): Promise<Interaction[]>;
    findByFilters(filters: InteractionFilters): Promise<Interaction[]>;
}
export interface InteractionFilters {
    clientId?: string;
    type?: InteractionType;
    sentiment?: SentimentType;
    category?: string;
    minValue?: number;
    maxValue?: number;
    startDate?: Date;
    endDate?: Date;
    hasValue?: boolean;
}
//# sourceMappingURL=IInteractionRepository.d.ts.map