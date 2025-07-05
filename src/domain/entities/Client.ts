import { v4 as uuidv4 } from 'uuid';

export interface ClientProps {
  id?: string;
  whatsappNumber: string;
  name?: string;
  email?: string;
  age?: number;
  city?: string;
  profession?: string;
  income?: number;
  segment?: ClientSegment;
  engagementScore?: number;
  churnRisk?: ChurnRisk;
  createdAt?: Date;
  updatedAt?: Date;
}

export enum ClientSegment {
  VIP = 'VIP',
  FREQUENT = 'FREQUENT',
  OCCASIONAL = 'OCCASIONAL',
  INACTIVE = 'INACTIVE'
}

export enum ChurnRisk {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

export class Client {
  private _id: string;
  private _whatsappNumber: string;
  private _name?: string;
  private _email?: string;
  private _age?: number;
  private _city?: string;
  private _profession?: string;
  private _income?: number;
  private _segment: ClientSegment;
  private _engagementScore: number;
  private _churnRisk: ChurnRisk;
  private _createdAt: Date;
  private _updatedAt: Date;

  constructor(props: ClientProps) {
    this._id = props.id || uuidv4();
    this._whatsappNumber = this.validateWhatsappNumber(props.whatsappNumber);
    this._name = props.name;
    this._email = props.email;
    this._age = props.age;
    this._city = props.city;
    this._profession = props.profession;
    this._income = props.income;
    this._segment = props.segment || ClientSegment.OCCASIONAL;
    this._engagementScore = props.engagementScore || 0;
    this._churnRisk = props.churnRisk || ChurnRisk.LOW;
    this._createdAt = props.createdAt || new Date();
    this._updatedAt = props.updatedAt || new Date();
  }

  // Getters
  get id(): string { return this._id; }
  get whatsappNumber(): string { return this._whatsappNumber; }
  get name(): string | undefined { return this._name; }
  get email(): string | undefined { return this._email; }
  get age(): number | undefined { return this._age; }
  get city(): string | undefined { return this._city; }
  get profession(): string | undefined { return this._profession; }
  get income(): number | undefined { return this._income; }
  get segment(): ClientSegment { return this._segment; }
  get engagementScore(): number { return this._engagementScore; }
  get churnRisk(): ChurnRisk { return this._churnRisk; }
  get createdAt(): Date { return this._createdAt; }
  get updatedAt(): Date { return this._updatedAt; }

  // Métodos de negócio
  public updateProfile(data: Partial<ClientProps>): void {
    if (data.name !== undefined) this._name = data.name;
    if (data.email !== undefined) this._email = data.email;
    if (data.age !== undefined) this._age = data.age;
    if (data.city !== undefined) this._city = data.city;
    if (data.profession !== undefined) this._profession = data.profession;
    if (data.income !== undefined) this._income = data.income;
    this._updatedAt = new Date();
  }

  public updateSegment(segment: ClientSegment): void {
    this._segment = segment;
    this._updatedAt = new Date();
  }

  public updateEngagementScore(score: number): void {
    if (score < 0 || score > 100) {
      throw new Error('Engagement score must be between 0 and 100');
    }
    this._engagementScore = score;
    this._updatedAt = new Date();
  }

  public updateChurnRisk(risk: ChurnRisk): void {
    this._churnRisk = risk;
    this._updatedAt = new Date();
  }

  public isVip(): boolean {
    return this._segment === ClientSegment.VIP;
  }

  public isHighRisk(): boolean {
    return this._churnRisk === ChurnRisk.HIGH || this._churnRisk === ChurnRisk.CRITICAL;
  }

  public hasCompleteProfile(): boolean {
    return !!(this._name && this._email && this._age && this._city && this._profession);
  }

  // Validações
  private validateWhatsappNumber(number: string): string {
    const cleanNumber = number.replace(/\D/g, '');
    if (cleanNumber.length < 10 || cleanNumber.length > 15) {
      throw new Error('Invalid WhatsApp number format');
    }
    return cleanNumber;
  }

  // Serialização
  public toJSON(): ClientProps {
    return {
      id: this._id,
      whatsappNumber: this._whatsappNumber,
      name: this._name,
      email: this._email,
      age: this._age,
      city: this._city,
      profession: this._profession,
      income: this._income,
      segment: this._segment,
      engagementScore: this._engagementScore,
      churnRisk: this._churnRisk,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt
    };
  }
}

