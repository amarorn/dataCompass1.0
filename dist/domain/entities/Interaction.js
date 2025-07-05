"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Interaction = exports.SentimentType = exports.InteractionType = void 0;
const uuid_1 = require("uuid");
var InteractionType;
(function (InteractionType) {
    InteractionType["PURCHASE"] = "PURCHASE";
    InteractionType["FEEDBACK"] = "FEEDBACK";
    InteractionType["QUESTION"] = "QUESTION";
    InteractionType["COMPLAINT"] = "COMPLAINT";
    InteractionType["PROFILE_UPDATE"] = "PROFILE_UPDATE";
    InteractionType["GENERAL"] = "GENERAL";
})(InteractionType || (exports.InteractionType = InteractionType = {}));
var SentimentType;
(function (SentimentType) {
    SentimentType["POSITIVE"] = "POSITIVE";
    SentimentType["NEUTRAL"] = "NEUTRAL";
    SentimentType["NEGATIVE"] = "NEGATIVE";
})(SentimentType || (exports.SentimentType = SentimentType = {}));
class Interaction {
    constructor(props) {
        this._id = props.id || (0, uuid_1.v4)();
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
    get id() { return this._id; }
    get clientId() { return this._clientId; }
    get type() { return this._type; }
    get content() { return this._content; }
    get value() { return this._value; }
    get category() { return this._category; }
    get sentiment() { return this._sentiment; }
    get metadata() { return this._metadata; }
    get createdAt() { return this._createdAt; }
    // Métodos de negócio
    updateSentiment(sentiment) {
        this._sentiment = sentiment;
    }
    addMetadata(key, value) {
        this._metadata[key] = value;
    }
    isPurchase() {
        return this._type === InteractionType.PURCHASE;
    }
    isComplaint() {
        return this._type === InteractionType.COMPLAINT;
    }
    isPositive() {
        return this._sentiment === SentimentType.POSITIVE;
    }
    isNegative() {
        return this._sentiment === SentimentType.NEGATIVE;
    }
    hasValue() {
        return this._value !== undefined && this._value > 0;
    }
    getValueOrZero() {
        return this._value || 0;
    }
    // Validações
    validateContent(content) {
        if (!content || content.trim().length === 0) {
            throw new Error('Interaction content cannot be empty');
        }
        if (content.length > 1000) {
            throw new Error('Interaction content cannot exceed 1000 characters');
        }
        return content.trim();
    }
    // Métodos estáticos para criação
    static createPurchase(clientId, content, value, category) {
        return new Interaction({
            clientId,
            type: InteractionType.PURCHASE,
            content,
            value,
            category,
            sentiment: SentimentType.POSITIVE
        });
    }
    static createFeedback(clientId, content, sentiment) {
        return new Interaction({
            clientId,
            type: InteractionType.FEEDBACK,
            content,
            sentiment
        });
    }
    static createComplaint(clientId, content) {
        return new Interaction({
            clientId,
            type: InteractionType.COMPLAINT,
            content,
            sentiment: SentimentType.NEGATIVE
        });
    }
    static createQuestion(clientId, content) {
        return new Interaction({
            clientId,
            type: InteractionType.QUESTION,
            content,
            sentiment: SentimentType.NEUTRAL
        });
    }
    // Serialização
    toJSON() {
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
exports.Interaction = Interaction;
//# sourceMappingURL=Interaction.js.map