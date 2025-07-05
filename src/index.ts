import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import dotenv from 'dotenv';

// Carregar variáveis de ambiente
dotenv.config();

// Importar rotas
import { clientRoutes } from './presentation/routes/clientRoutes';
import { analyticsRoutes } from './presentation/routes/analyticsRoutes';
import { whatsappRoutes } from './presentation/routes/whatsappRoutes';

// Importar middlewares
import { errorHandler } from './presentation/middlewares/errorHandler';
import { notFoundHandler } from './presentation/middlewares/notFoundHandler';

class App {
  public app: express.Application;
  private port: number;

  constructor() {
    this.app = express();
    this.port = parseInt(process.env.PORT || '3000');
    this.initializeMiddlewares();
    this.initializeRoutes();
    this.initializeErrorHandling();
  }

  private initializeMiddlewares(): void {
    // Segurança
    this.app.use(helmet());
    
    // CORS - permitir todas as origens para desenvolvimento
    this.app.use(cors({
      origin: '*',
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
      allowedHeaders: ['Content-Type', 'Authorization']
    }));

    // Logging
    this.app.use(morgan('combined'));

    // Parse JSON
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true }));
  }

  private initializeRoutes(): void {
    // Health check
    this.app.get('/health', (req, res) => {
      res.status(200).json({
        status: 'OK',
        timestamp: new Date().toISOString(),
        service: 'WhatsApp Analytics API'
      });
    });

    // API routes
    this.app.use('/api/clients', clientRoutes);
    this.app.use('/api/analytics', analyticsRoutes);
    this.app.use('/api/whatsapp', whatsappRoutes);
  }

  private initializeErrorHandling(): void {
    this.app.use(notFoundHandler);
    this.app.use(errorHandler);
  }

  public listen(): void {
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

export default app;

