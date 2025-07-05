import { v4 as uuidv4 } from 'uuid';

export interface InsightProps {
  id?: string;
  clientId?: string;
  type: InsightType;
  title: string;
  description: string;
  data: Record<string, any>;
  confidence: number;
  priority: InsightPriority;
  actionable: boolean;
  expiresAt?: Date;
  createdAt?: Date;
}

export enum InsightType {
  SEGMENTATION = 'SEGMENTATION',
  CHURN_PREDICTION = 'CHURN_PREDICTION',
  RECOMMENDATION = 'RECOMMENDATION',
  TREND_ANALYSIS = 'TREND_ANALYSIS',
  BEHAVIOR_PATTERN = 'BEHAVIOR_PATTERN',
  SATISFACTION_SCORE = 'SATISFACTION_SCORE',
  ENGAGEMENT_ANALYSIS = 'ENGAGEMENT_ANALYSIS'
}

export enum InsightPriority {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

export class Insight {
  private _id: string;
  private _clientId?: string;
  private _type: InsightType;
  private _title: string;
  private _description: string;
  private _data: Record<string, any>;
  private _confidence: number;
  private _priority: InsightPriority;
  private _actionable: boolean;
  private _expiresAt?: Date;
  private _createdAt: Date;

  constructor(props: InsightProps) {
    this._id = props.id || uuidv4();
    this._clientId = props.clientId;
    this._type = props.type;
    this._title = this.validateTitle(props.title);
    this._description = this.validateDescription(props.description);
    this._data = props.data;
    this._confidence = this.validateConfidence(props.confidence);
    this._priority = props.priority;
    this._actionable = props.actionable;
    this._expiresAt = props.expiresAt;
    this._createdAt = props.createdAt || new Date();
  }

  // Getters
  get id(): string { return this._id; }
  get clientId(): string | undefined { return this._clientId; }
  get type(): InsightType { return this._type; }
  get title(): string { return this._title; }
  get description(): string { return this._description; }
  get data(): Record<string, any> { return this._data; }
  get confidence(): number { return this._confidence; }
  get priority(): InsightPriority { return this._priority; }
  get actionable(): boolean { return this._actionable; }
  get expiresAt(): Date | undefined { return this._expiresAt; }
  get createdAt(): Date { return this._createdAt; }

  // Métodos de negócio
  public updatePriority(priority: InsightPriority): void {
    this._priority = priority;
  }

  public updateConfidence(confidence: number): void {
    this._confidence = this.validateConfidence(confidence);
  }

  public addData(key: string, value: any): void {
    this._data[key] = value;
  }

  public isExpired(): boolean {
    if (!this._expiresAt) return false;
    return new Date() > this._expiresAt;
  }

  public isCritical(): boolean {
    return this._priority === InsightPriority.CRITICAL;
  }

  public isHighConfidence(): boolean {
    return this._confidence >= 0.8;
  }

  public isClientSpecific(): boolean {
    return this._clientId !== undefined;
  }

  public isGlobal(): boolean {
    return this._clientId === undefined;
  }

  public getConfidencePercentage(): number {
    return Math.round(this._confidence * 100);
  }

  // Validações
  private validateTitle(title: string): string {
    if (!title || title.trim().length === 0) {
      throw new Error('Insight title cannot be empty');
    }
    if (title.length > 100) {
      throw new Error('Insight title cannot exceed 100 characters');
    }
    return title.trim();
  }

  private validateDescription(description: string): string {
    if (!description || description.trim().length === 0) {
      throw new Error('Insight description cannot be empty');
    }
    if (description.length > 500) {
      throw new Error('Insight description cannot exceed 500 characters');
    }
    return description.trim();
  }

  private validateConfidence(confidence: number): number {
    if (confidence < 0 || confidence > 1) {
      throw new Error('Confidence must be between 0 and 1');
    }
    return confidence;
  }

  // Métodos estáticos para criação
  public static createChurnPrediction(
    clientId: string,
    churnProbability: number,
    factors: string[]
  ): Insight {
    const priority = churnProbability > 0.7 ? InsightPriority.CRITICAL :
                    churnProbability > 0.5 ? InsightPriority.HIGH :
                    churnProbability > 0.3 ? InsightPriority.MEDIUM : InsightPriority.LOW;

    return new Insight({
      clientId,
      type: InsightType.CHURN_PREDICTION,
      title: `Risco de Churn: ${Math.round(churnProbability * 100)}%`,
      description: `Cliente com ${Math.round(churnProbability * 100)}% de probabilidade de churn. Fatores: ${factors.join(', ')}`,
      data: { churnProbability, factors },
      confidence: churnProbability,
      priority,
      actionable: true,
      expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) // 30 dias
    });
  }

  public static createRecommendation(
    clientId: string,
    products: string[],
    confidence: number
  ): Insight {
    return new Insight({
      clientId,
      type: InsightType.RECOMMENDATION,
      title: 'Recomendações Personalizadas',
      description: `Produtos recomendados baseados no perfil: ${products.join(', ')}`,
      data: { products, confidence },
      confidence,
      priority: InsightPriority.MEDIUM,
      actionable: true,
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7 dias
    });
  }

  public static createSegmentation(
    clientId: string,
    segment: string,
    characteristics: Record<string, any>
  ): Insight {
    return new Insight({
      clientId,
      type: InsightType.SEGMENTATION,
      title: `Segmento: ${segment}`,
      description: `Cliente classificado no segmento ${segment}`,
      data: { segment, characteristics },
      confidence: 0.9,
      priority: InsightPriority.LOW,
      actionable: false
    });
  }

  // Serialização
  public toJSON(): InsightProps {
    return {
      id: this._id,
      clientId: this._clientId,
      type: this._type,
      title: this._title,
      description: this._description,
      data: this._data,
      confidence: this._confidence,
      priority: this._priority,
      actionable: this._actionable,
      expiresAt: this._expiresAt,
      createdAt: this._createdAt
    };
  }
}

