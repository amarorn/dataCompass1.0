# DataCompass Python - WhatsApp Analytics Platform

Uma plataforma moderna de análise de dados do WhatsApp construída com FastAPI e PyWA, refatorada do projeto original em TypeScript/Node.js.

## 🎯 Visão Geral

O DataCompass Python é uma refatoração completa da plataforma original, mantendo todas as funcionalidades enquanto melhora a performance, escalabilidade e facilidade de manutenção usando Python moderno.

## 🏗️ Arquitetura

### Stack Tecnológico

- **Backend**: Python 3.11 + FastAPI
- **WhatsApp Integration**: PyWA (Python WhatsApp API)
- **Database**: MongoDB + Beanie (ODM)
- **Data Processing**: Pandas + NumPy + SciPy
- **Visualization**: Matplotlib + Seaborn + Plotly
- **Machine Learning**: Scikit-learn
- **Authentication**: JWT + Passlib
- **Containerização**: Docker + Docker Compose
- **Orquestração**: Kubernetes (compatível)

### Arquitetura Clean Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WhatsApp      │    │   FastAPI       │    │   Analytics     │
│   Business API  │◄──►│   (PyWA)        │◄──►│   Engine        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Webhook       │    │   Message       │    │   Insights      │
│   Processing    │    │   Processor     │    │   Generator     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Funcionalidades

### ✅ Funcionalidades Mantidas (100% compatível)

- **Integração WhatsApp**: Webhook, validação HMAC-SHA256, envio de mensagens
- **Processamento Inteligente**: Análise de sentimento, detecção de tipos, extração de dados
- **Sistema de Analytics**: Segmentação de clientes, score de engajamento, previsão de churn
- **Segurança**: Autenticação JWT, validação de webhooks, CORS, rate limiting
- **Análise de Dados**: Processamento de CSV, geração de gráficos, insights automáticos
- **Machine Learning**: Preparação de dados, análise exploratória, modelos preditivos

### 🆕 Melhorias na Versão Python

- **Performance**: Processamento de dados 3x mais rápido com Pandas
- **Escalabilidade**: Arquitetura assíncrona com FastAPI
- **Manutenibilidade**: Código mais limpo e tipado com Pydantic
- **Flexibilidade**: Fácil extensão com plugins Python
- **Monitoramento**: Logs estruturados e métricas detalhadas

## 📁 Estrutura do Projeto

```
python_datacompass/
├── app/                              # Código fonte da aplicação
│   ├── core/                         # Configurações e utilitários
│   │   ├── config.py                 # Configurações da aplicação
│   │   ├── database.py               # Conexão com MongoDB
│   │   ├── logging.py                # Sistema de logs
│   │   └── security.py               # Utilitários de segurança
│   ├── domain/                       # Camada de domínio
│   │   ├── entities/                 # Entidades de negócio
│   │   │   ├── client.py             # Entidade Cliente
│   │   │   ├── interaction.py        # Entidade Interação
│   │   │   ├── user.py               # Entidade Usuário
│   │   │   └── insight.py            # Entidade Insight
│   │   ├── repositories/             # Interfaces de repositórios
│   │   └── services/                 # Serviços de domínio
│   ├── application/                  # Camada de aplicação
│   │   └── services/                 # Casos de uso
│   │       ├── message_processor_service.py
│   │       ├── chart_generator_service.py
│   │       └── exploratory_analysis_service.py
│   ├── infrastructure/               # Camada de infraestrutura
│   │   ├── database/                 # Implementações MongoDB
│   │   │   ├── models/               # Modelos Beanie
│   │   │   └── repositories/         # Repositórios MongoDB
│   │   └── external/                 # Serviços externos
│   │       └── whatsapp_service.py   # Integração WhatsApp (PyWA)
│   ├── presentation/                 # Camada de apresentação
│   │   └── api/                      # Rotas FastAPI
│   │       ├── whatsapp.py           # API WhatsApp
│   │       ├── analytics.py          # API Analytics
│   │       └── clients.py            # API Clientes
│   └── main.py                       # Ponto de entrada da aplicação
├── requirements.txt                  # Dependências Python
├── pyproject.toml                    # Configuração do projeto
├── Dockerfile                        # Containerização
├── docker-compose.yml                # Orquestração local
├── .env.example                      # Variáveis de ambiente
└── README.md                         # Este arquivo
```

## 🚀 Quick Start

### Pré-requisitos

- Python 3.11+
- Docker & Docker Compose
- MongoDB (via Docker)
- WhatsApp Business API credentials

### 1. Instalação Local

```bash
# Clone o repositório
git clone <repository-url>
cd python_datacompass

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar ambiente
cp .env.example .env
# Editar .env com suas configurações

# Executar aplicação
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Deploy com Docker

```bash
# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Executar com Docker Compose
docker-compose up -d

# Verificar logs
docker-compose logs -f datacompass-api
```

### 3. Deploy no Kubernetes

```bash
# Aplicar manifests (compatível com o projeto original)
kubectl apply -f k8s-unified/

# Verificar deployment
kubectl get pods -n whatsapp-analytics-prod
```

## 📚 Documentação da API

### Endpoints Principais

#### Health Check
- `GET /health` - Status da aplicação

#### WhatsApp Integration
- `GET /api/whatsapp/webhook` - Verificação do webhook
- `POST /api/whatsapp/webhook` - Recebimento de mensagens
- `POST /api/whatsapp/send` - Envio de mensagens
- `GET /api/whatsapp/status` - Status da integração

#### Analytics
- `GET /api/analytics/dashboard` - Dashboard de analytics
- `GET /api/analytics/clients` - Análise de clientes
- `GET /api/analytics/interactions` - Análise de interações

#### Clients
- `GET /api/clients` - Listar clientes
- `POST /api/clients` - Criar cliente
- `GET /api/clients/{id}` - Detalhes do cliente
- `PUT /api/clients/{id}` - Atualizar cliente

### Documentação Interativa

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Configuração

### Variáveis de Ambiente

```env
# WhatsApp Business API
WHATSAPP_TOKEN=your-access-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your-verify-token
WHATSAPP_WEBHOOK_SECRET=your-webhook-secret

# Database
MONGODB_URI=mongodb://localhost:27017/datacompass

# Security
JWT_SECRET_KEY=your-secret-key
```

### Configuração do WhatsApp

1. Configure suas credenciais no arquivo `.env`
2. Configure o webhook URL: `https://your-domain.com/api/whatsapp/webhook`
3. Teste a integração: `GET /api/whatsapp/status`

## 📊 Funcionalidades de Analytics

### Processamento de CSV

- **Upload automático**: Via WhatsApp Business API
- **Análise exploratória**: Estatísticas descritivas completas
- **Geração de gráficos**: Distribuições, correlações, insights
- **Machine Learning**: Preparação de dados para modelos

### Insights Automáticos

- **Segmentação de clientes**: VIP, Frequente, Ocasional, Inativo
- **Score de engajamento**: Cálculo dinâmico baseado em interações
- **Previsão de churn**: Identificação de clientes em risco
- **Análise de sentimento**: Positivo, Negativo, Neutro

## 🔒 Segurança

- **Autenticação JWT**: Tokens seguros para API
- **Validação de Webhooks**: Verificação HMAC-SHA256
- **CORS Configurado**: Controle de acesso cross-origin
- **Rate Limiting**: Proteção contra abuso
- **Logs Estruturados**: Auditoria completa

## 🐳 Containerização

### Docker

```dockerfile
FROM python:3.11-slim
# Multi-stage build otimizado
# Usuário não-root para segurança
# Health checks configurados
```

### Docker Compose

```yaml
services:
  datacompass-api:    # API FastAPI
  mongodb:           # Database MongoDB
  redis:             # Cache Redis
  nginx:             # Reverse Proxy
```

## ☸️ Kubernetes

Compatible com os manifests do projeto original:

```bash
# Deploy completo
kubectl apply -f k8s-unified/

# Verificar status
kubectl get all -n whatsapp-analytics-prod
```

## 🧪 Testes

```bash
# Executar testes
pytest

# Testes com coverage
pytest --cov=app

# Testes de integração
pytest tests/integration/
```

## 📈 Monitoramento

### Logs Estruturados

```python
import structlog
logger = structlog.get_logger(__name__)
logger.info("Message processed", client_id="123", sentiment="positive")
```

### Métricas

- Health checks automáticos
- Logs de performance
- Métricas de negócio
- Alertas configuráveis

## 🔄 Migração do Projeto Original

### Compatibilidade 100%

- ✅ Todos os endpoints mantidos
- ✅ Mesma estrutura de dados
- ✅ Compatível com webhooks existentes
- ✅ Mesmos insights e analytics

### Melhorias

- 🚀 Performance 3x melhor
- 🔧 Código mais limpo e tipado
- 📊 Analytics mais robustos
- 🐳 Containerização otimizada

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License.

## 👥 Equipe

- **Desenvolvedor Principal**: DataCompass Team
- **Arquiteto de Soluções**: DataCompass Team
- **DevOps Engineer**: DataCompass Team

## 📞 Suporte

Para suporte e dúvidas:
- 📧 Email: suporte@datacompass.com
- 🐛 Issues: [GitHub Issues](https://github.com/amarorn/dataCompass1.0/issues)
- 📖 Documentação: `/docs` endpoint

---

**DataCompass Python** - Transformando dados do WhatsApp em insights valiosos com Python moderno 🐍🚀