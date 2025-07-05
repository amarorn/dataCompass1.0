"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Client = exports.ChurnRisk = exports.ClientSegment = void 0;
const uuid_1 = require("uuid");
var ClientSegment;
(function (ClientSegment) {
    ClientSegment["VIP"] = "VIP";
    ClientSegment["FREQUENT"] = "FREQUENT";
    ClientSegment["OCCASIONAL"] = "OCCASIONAL";
    ClientSegment["INACTIVE"] = "INACTIVE";
})(ClientSegment || (exports.ClientSegment = ClientSegment = {}));
var ChurnRisk;
(function (ChurnRisk) {
    ChurnRisk["LOW"] = "LOW";
    ChurnRisk["MEDIUM"] = "MEDIUM";
    ChurnRisk["HIGH"] = "HIGH";
    ChurnRisk["CRITICAL"] = "CRITICAL";
})(ChurnRisk || (exports.ChurnRisk = ChurnRisk = {}));
class Client {
    constructor(props) {
        this._id = props.id || (0, uuid_1.v4)();
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
    get id() { return this._id; }
    get whatsappNumber() { return this._whatsappNumber; }
    get name() { return this._name; }
    get email() { return this._email; }
    get age() { return this._age; }
    get city() { return this._city; }
    get profession() { return this._profession; }
    get income() { return this._income; }
    get segment() { return this._segment; }
    get engagementScore() { return this._engagementScore; }
    get churnRisk() { return this._churnRisk; }
    get createdAt() { return this._createdAt; }
    get updatedAt() { return this._updatedAt; }
    // Métodos de negócio
    updateProfile(data) {
        if (data.name !== undefined)
            this._name = data.name;
        if (data.email !== undefined)
            this._email = data.email;
        if (data.age !== undefined)
            this._age = data.age;
        if (data.city !== undefined)
            this._city = data.city;
        if (data.profession !== undefined)
            this._profession = data.profession;
        if (data.income !== undefined)
            this._income = data.income;
        this._updatedAt = new Date();
    }
    updateSegment(segment) {
        this._segment = segment;
        this._updatedAt = new Date();
    }
    updateEngagementScore(score) {
        if (score < 0 || score > 100) {
            throw new Error('Engagement score must be between 0 and 100');
        }
        this._engagementScore = score;
        this._updatedAt = new Date();
    }
    updateChurnRisk(risk) {
        this._churnRisk = risk;
        this._updatedAt = new Date();
    }
    isVip() {
        return this._segment === ClientSegment.VIP;
    }
    isHighRisk() {
        return this._churnRisk === ChurnRisk.HIGH || this._churnRisk === ChurnRisk.CRITICAL;
    }
    hasCompleteProfile() {
        return !!(this._name && this._email && this._age && this._city && this._profession);
    }
    // Validações
    validateWhatsappNumber(number) {
        const cleanNumber = number.replace(/\D/g, '');
        if (cleanNumber.length < 10 || cleanNumber.length > 15) {
            throw new Error('Invalid WhatsApp number format');
        }
        return cleanNumber;
    }
    // Serialização
    toJSON() {
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
exports.Client = Client;
//# sourceMappingURL=Client.js.map