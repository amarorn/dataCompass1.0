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
export declare enum InsightType {
    SEGMENTATION = "SEGMENTATION",
    CHURN_PREDICTION = "CHURN_PREDICTION",
    RECOMMENDATION = "RECOMMENDATION",
    TREND_ANALYSIS = "TREND_ANALYSIS",
    BEHAVIOR_PATTERN = "BEHAVIOR_PATTERN",
    SATISFACTION_SCORE = "SATISFACTION_SCORE",
    ENGAGEMENT_ANALYSIS = "ENGAGEMENT_ANALYSIS"
}
export declare enum InsightPriority {
    LOW = "LOW",
    MEDIUM = "MEDIUM",
    HIGH = "HIGH",
    CRITICAL = "CRITICAL"
}
export declare class Insight {
    private _id;
    private _clientId?;
    private _type;
    private _title;
    private _description;
    private _data;
    private _confidence;
    private _priority;
    private _actionable;
    private _expiresAt?;
    private _createdAt;
    constructor(props: InsightProps);
    get id(): string;
    get clientId(): string | undefined;
    get type(): InsightType;
    get title(): string;
    get description(): string;
    get data(): Record<string, any>;
    get confidence(): number;
    get priority(): InsightPriority;
    get actionable(): boolean;
    get expiresAt(): Date | undefined;
    get createdAt(): Date;
    updatePriority(priority: InsightPriority): void;
    updateConfidence(confidence: number): void;
    addData(key: string, value: any): void;
    isExpired(): boolean;
    isCritical(): boolean;
    isHighConfidence(): boolean;
    isClientSpecific(): boolean;
    isGlobal(): boolean;
    getConfidencePercentage(): number;
    private validateTitle;
    private validateDescription;
    private validateConfidence;
    static createChurnPrediction(clientId: string, churnProbability: number, factors: string[]): Insight;
    static createRecommendation(clientId: string, products: string[], confidence: number): Insight;
    static createSegmentation(clientId: string, segment: string, characteristics: Record<string, any>): Insight;
    toJSON(): InsightProps;
}
//# sourceMappingURL=Insight.d.ts.map