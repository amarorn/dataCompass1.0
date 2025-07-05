import { Insight, InsightType, InsightPriority } from '@domain/entities/Insight';
export interface IInsightRepository {
    create(insight: Insight): Promise<Insight>;
    findById(id: string): Promise<Insight | null>;
    update(insight: Insight): Promise<Insight>;
    delete(id: string): Promise<void>;
    findByClientId(clientId: string, page?: number, limit?: number): Promise<Insight[]>;
    findActiveByClientId(clientId: string): Promise<Insight[]>;
    findActionableByClientId(clientId: string): Promise<Insight[]>;
    findGlobalInsights(page?: number, limit?: number): Promise<Insight[]>;
    findActiveGlobalInsights(): Promise<Insight[]>;
    findByType(type: InsightType, page?: number, limit?: number): Promise<Insight[]>;
    findByPriority(priority: InsightPriority, page?: number, limit?: number): Promise<Insight[]>;
    findActionable(page?: number, limit?: number): Promise<Insight[]>;
    findExpired(): Promise<Insight[]>;
    findCritical(): Promise<Insight[]>;
    findHighConfidence(minConfidence: number): Promise<Insight[]>;
    findByDateRange(startDate: Date, endDate: Date): Promise<Insight[]>;
    findRecentInsights(days: number): Promise<Insight[]>;
    deleteExpired(): Promise<number>;
    deleteByClientId(clientId: string): Promise<number>;
    count(): Promise<number>;
    countByClient(clientId: string): Promise<number>;
    countByType(): Promise<Record<string, number>>;
    countByPriority(): Promise<Record<string, number>>;
    getAverageConfidence(): Promise<number>;
    search(query: string): Promise<Insight[]>;
    findByFilters(filters: InsightFilters): Promise<Insight[]>;
}
export interface InsightFilters {
    clientId?: string;
    type?: InsightType;
    priority?: InsightPriority;
    actionable?: boolean;
    minConfidence?: number;
    maxConfidence?: number;
    startDate?: Date;
    endDate?: Date;
    includeExpired?: boolean;
}
//# sourceMappingURL=IInsightRepository.d.ts.map