# DataCompass 2.0 - Python Version with PyWA

## 🎯 Visão Geral

Refatoração completa do DataCompass 1.0 em Python usando PyWA (Python WhatsApp), mantendo todas as funcionalidades originais e adicionando melhorias de performance e escalabilidade.

## 🏗️ Arquitetura da Solução

### Stack Tecnológico

- **Backend**: Python 3.11+ com FastAPI
- **WhatsApp Integration**: PyWA (Python WhatsApp)
- **Database**: MongoDB com Motor (async driver)
- **Arquitetura**: Clean Architecture + Domain-Driven Design
- **Containerização**: Docker + Multi-stage builds
- **Orquestração**: Kubernetes (Amazon EKS)
- **Cloud**: Amazon Web Services (AWS)

### Principais Melhorias

1. **Performance Assíncrona**: Uso de async/await para melhor performance
2. **Type Hints**: Tipagem forte com Pydantic
3. **PyWA Integration**: Biblioteca oficial para WhatsApp Business API
4. **Machine Learning Nativo**: Integração direta com scikit-learn e pandas
5. **WebSockets**: Suporte para comunicação em tempo real

## 🚀 Funcionalidades Mantidas

### 📱 Integração WhatsApp
- ✅ Webhook para recebimento de mensagens
- ✅ Validação de assinatura HMAC-SHA256
- ✅ Envio de mensagens automáticas
- ✅ Templates de mensagens personalizados
- ✅ Status da integração em tempo real
- ✅ Suporte a mídia (imagens, documentos, áudio)

### 🤖 Processamento Inteligente
- ✅ Análise de Sentimento com ML nativo
- ✅ Detecção de Tipos de Interação
- ✅ Extração de Dados e Entidades
- ✅ Respostas Automáticas Contextuais
- ✅ Processamento de CSV via WhatsApp

### 📊 Sistema de Analytics
- ✅ Segmentação de Clientes
- ✅ Score de Engajamento
- ✅ Previsão de Churn
- ✅ Insights Personalizados
- ✅ Análise Exploratória de Dados

## 📁 Estrutura do Projeto

```
python_version/
├── src/
│   ├── domain/              # Camada de domínio
│   │   ├── entities/        # Entidades de negócio
│   │   ├── repositories/    # Interfaces de repositórios
│   │   └── services/        # Serviços de domínio
│   ├── application/         # Camada de aplicação
│   │   └── services/        # Casos de uso
│   ├── infrastructure/      # Camada de infraestrutura
│   │   ├── database/        # Implementação MongoDB
│   │   ├── whatsapp/        # Integração PyWA
│   │   └── external/        # Serviços externos
│   ├── presentation/        # Camada de apresentação
│   │   ├── api/            # Endpoints FastAPI
│   │   ├── middlewares/    # Middlewares
│   │   └── websockets/     # WebSocket handlers
│   └── main.py             # Ponto de entrada
├── tests/                   # Testes
├── scripts/                 # Scripts auxiliares
├── k8s/                     # Configurações Kubernetes
├── Dockerfile              # Containerização
├── requirements.txt        # Dependências Python
├── .env.example           # Variáveis de ambiente
└── README.md              # Este arquivo
```

## 🚀 Quick Start

### Pré-requisitos

- Python 3.11+
- MongoDB 6.0+
- Docker (opcional)
- WhatsApp Business API credentials

### 1. Instalação Local

```bash
# Clone o repositório
cd python_version

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar ambiente
cp .env.example .env
# Editar .env com suas configurações

# Executar aplicação
python src/main.py
```

### 2. Executar com Docker

```bash
# Build da imagem
docker build -t datacompass-python .

# Executar container
docker run -p 3000:3000 --env-file .env datacompass-python
```

### 3. Deploy no Kubernetes

```bash
# Aplicar configurações
kubectl apply -f k8s/

# Verificar status
kubectl get pods -n whatsapp-analytics
```

## 🔗 Endpoints da API

### Health Check
- `GET /health` - Status da aplicação
- `GET /api/health/ready` - Readiness probe
- `GET /api/health/live` - Liveness probe

### WhatsApp Integration
- `GET /api/whatsapp/webhook` - Verificação do webhook
- `POST /api/whatsapp/webhook` - Recebimento de mensagens
- `POST /api/whatsapp/send` - Envio de mensagens
- `POST /api/whatsapp/template` - Envio de templates
- `GET /api/whatsapp/status` - Status da integração

### Analytics
- `GET /api/analytics/dashboard` - Dashboard de analytics
- `GET /api/analytics/insights` - Insights personalizados
- `GET /api/analytics/clients` - Análise de clientes
- `POST /api/analytics/exploratory` - Análise exploratória

### Clients
- `GET /api/clients` - Listar clientes
- `GET /api/clients/{id}` - Detalhes do cliente
- `POST /api/clients` - Criar cliente
- `PUT /api/clients/{id}` - Atualizar cliente
- `DELETE /api/clients/{id}` - Remover cliente

### WebSocket
- `WS /ws/messages` - Stream de mensagens em tempo real
- `WS /ws/analytics` - Analytics em tempo real

## 🔧 Comandos Úteis

```bash
# Desenvolvimento
make dev              # Executar em desenvolvimento
make test             # Executar testes
make lint             # Verificar código
make format           # Formatar código

# Docker
make docker-build     # Build da imagem
make docker-run       # Executar container
make docker-push      # Push para registry

# Kubernetes
make k8s-deploy       # Deploy no Kubernetes
make k8s-status       # Status do deployment
make k8s-logs         # Logs da aplicação
```

## 🔐 Configuração PyWA

### Inicialização do WhatsApp Client

```python
from pywa import WhatsApp

wa = WhatsApp(
    phone_id=WHATSAPP_PHONE_NUMBER_ID,
    token=WHATSAPP_TOKEN,
    server=PYWA_SERVER_URL,
    webhook_endpoint=PYWA_WEBHOOK_ENDPOINT,
    verify_token=WHATSAPP_WEBHOOK_VERIFY_TOKEN,
    app_id=WHATSAPP_APP_ID,
    app_secret=WHATSAPP_APP_SECRET,
    business_account_id=WHATSAPP_BUSINESS_ID,
    callback_url=PYWA_CALLBACK_URL
)
```

## 📊 Monitoramento

### Métricas
- Prometheus metrics em `/metrics`
- Custom metrics para WhatsApp messages
- Performance metrics com FastAPI

### Logging
- Structured logging com JSON
- Log levels configuráveis
- Integração com ELK Stack

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License.

---

**DataCompass 2.0 Python** - Refatoração completa com PyWA 🚀
