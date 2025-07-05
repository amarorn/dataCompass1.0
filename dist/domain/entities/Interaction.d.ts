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
export declare enum InteractionType {
    PURCHASE = "PURCHASE",
    FEEDBACK = "FEEDBACK",
    QUESTION = "QUESTION",
    COMPLAINT = "COMPLAINT",
    PROFILE_UPDATE = "PROFILE_UPDATE",
    GENERAL = "GENERAL"
}
export declare enum SentimentType {
    POSITIVE = "POSITIVE",
    NEUTRAL = "NEUTRAL",
    NEGATIVE = "NEGATIVE"
}
export declare class Interaction {
    private _id;
    private _clientId;
    private _type;
    private _content;
    private _value?;
    private _category?;
    private _sentiment;
    private _metadata;
    private _createdAt;
    constructor(props: InteractionProps);
    get id(): string;
    get clientId(): string;
    get type(): InteractionType;
    get content(): string;
    get value(): number | undefined;
    get category(): string | undefined;
    get sentiment(): SentimentType;
    get metadata(): Record<string, any>;
    get createdAt(): Date;
    updateSentiment(sentiment: SentimentType): void;
    addMetadata(key: string, value: any): void;
    isPurchase(): boolean;
    isComplaint(): boolean;
    isPositive(): boolean;
    isNegative(): boolean;
    hasValue(): boolean;
    getValueOrZero(): number;
    private validateContent;
    static createPurchase(clientId: string, content: string, value: number, category?: string): Interaction;
    static createFeedback(clientId: string, content: string, sentiment: SentimentType): Interaction;
    static createComplaint(clientId: string, content: string): Interaction;
    static createQuestion(clientId: string, content: string): Interaction;
    toJSON(): InteractionProps;
}
//# sourceMappingURL=Interaction.d.ts.map