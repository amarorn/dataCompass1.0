"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const helmet_1 = __importDefault(require("helmet"));
const morgan_1 = __importDefault(require("morgan"));
const dotenv_1 = __importDefault(require("dotenv"));
// Carregar variáveis de ambiente
dotenv_1.default.config();
// Importar rotas
const clientRoutes_1 = require("./presentation/routes/clientRoutes");
const analyticsRoutes_1 = require("./presentation/routes/analyticsRoutes");
const whatsappRoutes_1 = require("./presentation/routes/whatsappRoutes");
const userRoutes_1 = require("./presentation/routes/userRoutes");
// Importar middlewares
const errorHandler_1 = require("./presentation/middlewares/errorHandler");
const notFoundHandler_1 = require("./presentation/middlewares/notFoundHandler");
class App {
    constructor() {
        this.app = (0, express_1.default)();
        this.port = parseInt(process.env.PORT || '3000');
        this.initializeMiddlewares();
        this.initializeRoutes();
        this.initializeErrorHandling();
    }
    initializeMiddlewares() {
        // Segurança
        this.app.use((0, helmet_1.default)());
        // CORS - permitir todas as origens para desenvolvimento
        this.app.use((0, cors_1.default)({
            origin: '*',
            methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
            allowedHeaders: ['Content-Type', 'Authorization']
        }));
        // Logging
        this.app.use((0, morgan_1.default)('combined'));
        // Parse JSON
        this.app.use(express_1.default.json({ limit: '10mb' }));
        this.app.use(express_1.default.urlencoded({ extended: true }));
    }
    initializeRoutes() {
        // Health check
        this.app.get('/health', (req, res) => {
            res.status(200).json({
                status: 'OK',
                timestamp: new Date().toISOString(),
                service: 'WhatsApp Analytics API'
            });
        });
        // API routes
        this.app.use('/api/clients', clientRoutes_1.clientRoutes);
        this.app.use('/api/analytics', analyticsRoutes_1.analyticsRoutes);
        this.app.use('/api/whatsapp', whatsappRoutes_1.whatsappRoutes);
        this.app.use('/api/users', userRoutes_1.userRoutes);
    }
    initializeErrorHandling() {
        this.app.use(notFoundHandler_1.notFoundHandler);
        this.app.use(errorHandler_1.errorHandler);
    }
    listen() {
        this.app.listen(this.port, '0.0.0.0', () => {
            console.log(`🚀 Server running on http://0.0.0.0:${this.port}`);
            console.log(`📱 WhatsApp Analytics API v1.0.0`);
            console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
        });
    }
}
// Inicializar aplicação
const app = new App();
app.listen();
exports.default = app;
//# sourceMappingURL=index.js.map