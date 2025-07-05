import { Client } from '@domain/entities/Client';

export interface IClientRepository {
  // Operações básicas CRUD
  create(client: Client): Promise<Client>;
  findById(id: string): Promise<Client | null>;
  findByWhatsappNumber(whatsappNumber: string): Promise<Client | null>;
  update(client: Client): Promise<Client>;
  delete(id: string): Promise<void>;

  // Consultas específicas
  findAll(page?: number, limit?: number): Promise<Client[]>;
  findBySegment(segment: string): Promise<Client[]>;
  findByChurnRisk(risk: string): Promise<Client[]>;
  findByCity(city: string): Promise<Client[]>;
  findByProfession(profession: string): Promise<Client[]>;

  // Consultas para análise
  findHighValueClients(minIncome?: number): Promise<Client[]>;
  findInactiveClients(daysSinceLastInteraction: number): Promise<Client[]>;
  findClientsWithLowEngagement(maxScore: number): Promise<Client[]>;
  
  // Estatísticas
  count(): Promise<number>;
  countBySegment(): Promise<Record<string, number>>;
  countByChurnRisk(): Promise<Record<string, number>>;
  getAverageEngagementScore(): Promise<number>;
  getAverageIncome(): Promise<number>;

  // Busca avançada
  search(query: string): Promise<Client[]>;
  findByFilters(filters: ClientFilters): Promise<Client[]>;
}

export interface ClientFilters {
  segment?: string;
  churnRisk?: string;
  city?: string;
  profession?: string;
  minAge?: number;
  maxAge?: number;
  minIncome?: number;
  maxIncome?: number;
  minEngagementScore?: number;
  maxEngagementScore?: number;
  createdAfter?: Date;
  createdBefore?: Date;
}

