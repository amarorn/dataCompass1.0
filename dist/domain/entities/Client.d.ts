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
export declare enum ClientSegment {
    VIP = "VIP",
    FREQUENT = "FREQUENT",
    OCCASIONAL = "OCCASIONAL",
    INACTIVE = "INACTIVE"
}
export declare enum ChurnRisk {
    LOW = "LOW",
    MEDIUM = "MEDIUM",
    HIGH = "HIGH",
    CRITICAL = "CRITICAL"
}
export declare class Client {
    private _id;
    private _whatsappNumber;
    private _name?;
    private _email?;
    private _age?;
    private _city?;
    private _profession?;
    private _income?;
    private _segment;
    private _engagementScore;
    private _churnRisk;
    private _createdAt;
    private _updatedAt;
    constructor(props: ClientProps);
    get id(): string;
    get whatsappNumber(): string;
    get name(): string | undefined;
    get email(): string | undefined;
    get age(): number | undefined;
    get city(): string | undefined;
    get profession(): string | undefined;
    get income(): number | undefined;
    get segment(): ClientSegment;
    get engagementScore(): number;
    get churnRisk(): ChurnRisk;
    get createdAt(): Date;
    get updatedAt(): Date;
    updateProfile(data: Partial<ClientProps>): void;
    updateSegment(segment: ClientSegment): void;
    updateEngagementScore(score: number): void;
    updateChurnRisk(risk: ChurnRisk): void;
    isVip(): boolean;
    isHighRisk(): boolean;
    hasCompleteProfile(): boolean;
    private validateWhatsappNumber;
    toJSON(): ClientProps;
}
//# sourceMappingURL=Client.d.ts.map