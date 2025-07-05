import { Insight, InsightType, InsightPriority } from '@domain/entities/Insight';

export interface IInsightRepository {
  // Operações básicas CRUD
  create(insight: Insight): Promise<Insight>;
  findById(id: string): Promise<Insight | null>;
  update(insight: Insight): Promise<Insight>;
  delete(id: string): Promise<void>;

  // Consultas por cliente
  findByClientId(clientId: string, page?: number, limit?: number): Promise<Insight[]>;
  findActiveByClientId(clientId: string): Promise<Insight[]>;
  findActionableByClientId(clientId: string): Promise<Insight[]>;

  // Consultas globais
  findGlobalInsights(page?: number, limit?: number): Promise<Insight[]>;
  findActiveGlobalInsights(): Promise<Insight[]>;

  // Consultas por tipo
  findByType(type: InsightType, page?: number, limit?: number): Promise<Insight[]>;
  findByPriority(priority: InsightPriority, page?: number, limit?: number): Promise<Insight[]>;

  // Consultas por status
  findActionable(page?: number, limit?: number): Promise<Insight[]>;
  findExpired(): Promise<Insight[]>;
  findCritical(): Promise<Insight[]>;
  findHighConfidence(minConfidence: number): Promise<Insight[]>;

  // Consultas temporais
  findByDateRange(startDate: Date, endDate: Date): Promise<Insight[]>;
  findRecentInsights(days: number): Promise<Insight[]>;

  // Limpeza
  deleteExpired(): Promise<number>;
  deleteByClientId(clientId: string): Promise<number>;

  // Estatísticas
  count(): Promise<number>;
  countByClient(clientId: string): Promise<number>;
  countByType(): Promise<Record<string, number>>;
  countByPriority(): Promise<Record<string, number>>;
  getAverageConfidence(): Promise<number>;

  // Busca avançada
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

