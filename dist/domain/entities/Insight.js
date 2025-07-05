"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Insight = exports.InsightPriority = exports.InsightType = void 0;
const uuid_1 = require("uuid");
var InsightType;
(function (InsightType) {
    InsightType["SEGMENTATION"] = "SEGMENTATION";
    InsightType["CHURN_PREDICTION"] = "CHURN_PREDICTION";
    InsightType["RECOMMENDATION"] = "RECOMMENDATION";
    InsightType["TREND_ANALYSIS"] = "TREND_ANALYSIS";
    InsightType["BEHAVIOR_PATTERN"] = "BEHAVIOR_PATTERN";
    InsightType["SATISFACTION_SCORE"] = "SATISFACTION_SCORE";
    InsightType["ENGAGEMENT_ANALYSIS"] = "ENGAGEMENT_ANALYSIS";
})(InsightType || (exports.InsightType = InsightType = {}));
var InsightPriority;
(function (InsightPriority) {
    InsightPriority["LOW"] = "LOW";
    InsightPriority["MEDIUM"] = "MEDIUM";
    InsightPriority["HIGH"] = "HIGH";
    InsightPriority["CRITICAL"] = "CRITICAL";
})(InsightPriority || (exports.InsightPriority = InsightPriority = {}));
class Insight {
    constructor(props) {
        this._id = props.id || (0, uuid_1.v4)();
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
    get id() { return this._id; }
    get clientId() { return this._clientId; }
    get type() { return this._type; }
    get title() { return this._title; }
    get description() { return this._description; }
    get data() { return this._data; }
    get confidence() { return this._confidence; }
    get priority() { return this._priority; }
    get actionable() { return this._actionable; }
    get expiresAt() { return this._expiresAt; }
    get createdAt() { return this._createdAt; }
    // Métodos de negócio
    updatePriority(priority) {
        this._priority = priority;
    }
    updateConfidence(confidence) {
        this._confidence = this.validateConfidence(confidence);
    }
    addData(key, value) {
        this._data[key] = value;
    }
    isExpired() {
        if (!this._expiresAt)
            return false;
        return new Date() > this._expiresAt;
    }
    isCritical() {
        return this._priority === InsightPriority.CRITICAL;
    }
    isHighConfidence() {
        return this._confidence >= 0.8;
    }
    isClientSpecific() {
        return this._clientId !== undefined;
    }
    isGlobal() {
        return this._clientId === undefined;
    }
    getConfidencePercentage() {
        return Math.round(this._confidence * 100);
    }
    // Validações
    validateTitle(title) {
        if (!title || title.trim().length === 0) {
            throw new Error('Insight title cannot be empty');
        }
        if (title.length > 100) {
            throw new Error('Insight title cannot exceed 100 characters');
        }
        return title.trim();
    }
    validateDescription(description) {
        if (!description || description.trim().length === 0) {
            throw new Error('Insight description cannot be empty');
        }
        if (description.length > 500) {
            throw new Error('Insight description cannot exceed 500 characters');
        }
        return description.trim();
    }
    validateConfidence(confidence) {
        if (confidence < 0 || confidence > 1) {
            throw new Error('Confidence must be between 0 and 1');
        }
        return confidence;
    }
    // Métodos estáticos para criação
    static createChurnPrediction(clientId, churnProbability, factors) {
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
    static createRecommendation(clientId, products, confidence) {
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
    static createSegmentation(clientId, segment, characteristics) {
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
    toJSON() {
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
exports.Insight = Insight;
//# sourceMappingURL=Insight.js.map