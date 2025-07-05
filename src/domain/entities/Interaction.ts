import { v4 as uuidv4 } from 'uuid';

export interface InteractionProps {
  id?: string;
  clientId: string;
  type: InteractionType;
  content: string;
  value?: number;
  category?: string;
  sentiment?: SentimentType;
  metadata?: Record<string, any>;
  createdAt?: Date;
}

export enum InteractionType {
  PURCHASE = 'PURCHASE',
  FEEDBACK = 'FEEDBACK',
  QUESTION = 'QUESTION',
  COMPLAINT = 'COMPLAINT',
  PROFILE_UPDATE = 'PROFILE_UPDATE',
  GENERAL = 'GENERAL'
}

export enum SentimentType {
  POSITIVE = 'POSITIVE',
  NEUTRAL = 'NEUTRAL',
  NEGATIVE = 'NEGATIVE'
}

export class Interaction {
  private _id: string;
  private _clientId: string;
  private _type: InteractionType;
  private _content: string;
  private _value?: number;
  private _category?: string;
  private _sentiment: SentimentType;
  private _metadata: Record<string, any>;
  private _createdAt: Date;

  constructor(props: InteractionProps) {
    this._id = props.id || uuidv4();
    this._clientId = props.clientId;
    this._type = props.type;
    this._content = this.validateContent(props.content);
    this._value = props.value;
    this._category = props.category;
    this._sentiment = props.sentiment || SentimentType.NEUTRAL;
    this._metadata = props.metadata || {};
    this._createdAt = props.createdAt || new Date();
  }

  // Getters
  get id(): string { return this._id; }
  get clientId(): string { return this._clientId; }
  get type(): InteractionType { return this._type; }
  get content(): string { return this._content; }
  get value(): number | undefined { return this._value; }
  get category(): string | undefined { return this._category; }
  get sentiment(): SentimentType { return this._sentiment; }
  get metadata(): Record<string, any> { return this._metadata; }
  get createdAt(): Date { return this._createdAt; }

  // Métodos de negócio
  public updateSentiment(sentiment: SentimentType): void {
    this._sentiment = sentiment;
  }

  public addMetadata(key: string, value: any): void {
    this._metadata[key] = value;
  }

  public isPurchase(): boolean {
    return this._type === InteractionType.PURCHASE;
  }

  public isComplaint(): boolean {
    return this._type === InteractionType.COMPLAINT;
  }

  public isPositive(): boolean {
    return this._sentiment === SentimentType.POSITIVE;
  }

  public isNegative(): boolean {
    return this._sentiment === SentimentType.NEGATIVE;
  }

  public hasValue(): boolean {
    return this._value !== undefined && this._value > 0;
  }

  public getValueOrZero(): number {
    return this._value || 0;
  }

  // Validações
  private validateContent(content: string): string {
    if (!content || content.trim().length === 0) {
      throw new Error('Interaction content cannot be empty');
    }
    if (content.length > 1000) {
      throw new Error('Interaction content cannot exceed 1000 characters');
    }
    return content.trim();
  }

  // Métodos estáticos para criação
  public static createPurchase(
    clientId: string,
    content: string,
    value: number,
    category?: string
  ): Interaction {
    return new Interaction({
      clientId,
      type: InteractionType.PURCHASE,
      content,
      value,
      category,
      sentiment: SentimentType.POSITIVE
    });
  }

  public static createFeedback(
    clientId: string,
    content: string,
    sentiment: SentimentType
  ): Interaction {
    return new Interaction({
      clientId,
      type: InteractionType.FEEDBACK,
      content,
      sentiment
    });
  }

  public static createComplaint(
    clientId: string,
    content: string
  ): Interaction {
    return new Interaction({
      clientId,
      type: InteractionType.COMPLAINT,
      content,
      sentiment: SentimentType.NEGATIVE
    });
  }

  public static createQuestion(
    clientId: string,
    content: string
  ): Interaction {
    return new Interaction({
      clientId,
      type: InteractionType.QUESTION,
      content,
      sentiment: SentimentType.NEUTRAL
    });
  }

  // Serialização
  public toJSON(): InteractionProps {
    return {
      id: this._id,
      clientId: this._clientId,
      type: this._type,
      content: this._content,
      value: this._value,
      category: this._category,
      sentiment: this._sentiment,
      metadata: this._metadata,
      createdAt: this._createdAt
    };
  }
}

