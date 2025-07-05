# DataCompass 1.0 - WhatsApp Analytics Platform

## 🎯 Visão Geral

O DataCompass 1.0 é uma plataforma completa de análise de dados de clientes via WhatsApp, desenvolvida com arquitetura moderna e deploy automatizado no Kubernetes da AWS.

## 🏗️ Arquitetura da Solução

### Stack Tecnológico

- **Backend**: Node.js + TypeScript + Express
- **Arquitetura**: Clean Architecture + SOLID Principles
- **Containerização**: Docker + Multi-stage builds
- **Orquestração**: Kubernetes (Amazon EKS)
- **Infraestrutura**: Terraform (Infrastructure as Code)
- **CI/CD**: GitHub Actions
- **Cloud**: Amazon Web Services (AWS)

### Componentes Principais

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WhatsApp      │    │   API Gateway   │    │   Analytics     │
│   Business API  │◄──►│   (Express)     │◄──►│   Engine        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Webhook       │    │   Message       │    │   Insights      │
│   Processing    │    │   Processor     │    │   Generator     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Funcionalidades

### 📱 Integração WhatsApp
- ✅ Webhook para recebimento de mensagens
- ✅ Validação de assinatura HMAC-SHA256
- ✅ Envio de mensagens automáticas
- ✅ Templates de mensagens personalizados
- ✅ Status da integração em tempo real

### 🤖 Processamento Inteligente
- ✅ **Análise de Sentimento**: Positivo, Negativo, Neutro
- ✅ **Detecção de Tipos**: Compras, Reclamações, Feedback, Perguntas
- ✅ **Extração de Dados**: Valores monetários, categorias, entidades
- ✅ **Respostas Automáticas**: Contextuais e personalizadas

### 📊 Sistema de Analytics
- ✅ **Segmentação de Clientes**: VIP, Frequente, Ocasional, Inativo
- ✅ **Score de Engajamento**: Cálculo dinâmico baseado em interações
- ✅ **Previsão de Churn**: Identificação de clientes em risco
- ✅ **Insights Personalizados**: Recomendações baseadas em dados
- ✅ **Padrões Comportamentais**: Análise de tendências

### 🔒 Segurança e Compliance
- ✅ **Autenticação JWT**: Tokens seguros para API
- ✅ **Validação de Webhooks**: Verificação de assinatura
- ✅ **CORS Configurado**: Controle de acesso cross-origin
- ✅ **Rate Limiting**: Proteção contra abuso
- ✅ **Secrets Management**: Configuração segura de credenciais

## 🏭 Infraestrutura e Deploy

### ☸️ Kubernetes (Amazon EKS)
- **Cluster**: Multi-AZ com auto-scaling
- **Nodes**: Spot instances para redução de custos
- **Load Balancer**: Application Load Balancer (ALB)
- **Auto Scaling**: Horizontal Pod Autoscaler (HPA)
- **Monitoring**: Health checks e probes

### 🐳 Containerização
- **Docker**: Multi-stage builds otimizados
- **Registry**: Amazon ECR com lifecycle policies
- **Security**: Imagens escaneadas com Trivy
- **Size**: Imagens otimizadas para produção

### 🔄 CI/CD Pipeline
- **Build**: Automatizado com GitHub Actions
- **Test**: Testes unitários e de integração
- **Security**: Scanning de vulnerabilidades
- **Deploy**: Zero-downtime deployments
- **Rollback**: Automático em caso de falha

### 🏗️ Infrastructure as Code
- **Terraform**: Provisionamento de recursos AWS
- **Modules**: Componentes reutilizáveis
- **State**: Gerenciamento remoto com S3 + DynamoDB
- **Environments**: Staging e Production isolados

## 📁 Estrutura do Projeto

```
dataCompass1.0/
├── src/                          # Código fonte da aplicação
│   ├── domain/                   # Camada de domínio
│   │   ├── entities/            # Entidades de negócio
│   │   ├── repositories/        # Interfaces de repositórios
│   │   └── services/            # Serviços de domínio
│   ├── application/             # Camada de aplicação
│   │   └── services/            # Casos de uso
│   ├── infrastructure/          # Camada de infraestrutura
│   │   └── external/            # Integrações externas
│   └── presentation/            # Camada de apresentação
│       ├── routes/              # Rotas da API
│       └── middlewares/         # Middlewares
├── k8s/                         # Manifests Kubernetes
│   ├── base/                    # Configurações base
│   └── overlays/                # Configurações por ambiente
├── infrastructure/              # Infraestrutura como código
│   ├── terraform/               # Configurações Terraform
│   └── scripts/                 # Scripts de automação
├── .github/workflows/           # CI/CD Pipelines
├── docs/                        # Documentação
├── Dockerfile                   # Containerização
├── Makefile                     # Comandos de automação
└── README.md                    # Este arquivo
```

## 🚀 Quick Start

### Pré-requisitos

- Node.js 20+
- Docker
- AWS CLI
- kubectl
- Terraform
- Helm

### 1. Instalação Local

```bash
# Clone o repositório
git clone https://github.com/amarorn/dataCompass1.0.git
cd dataCompass1.0

# Instalar dependências
npm install

# Configurar ambiente
cp .env.example .env
# Editar .env com suas configurações

# Executar em desenvolvimento
npm run dev
```

### 2. Deploy no Kubernetes

```bash
# Setup completo automatizado
make setup-all

# Ou passo a passo
make terraform-init
make terraform-apply
make setup-secrets
make k8s-deploy
```

### 3. Via CI/CD

```bash
# 1. Configurar secrets no GitHub
# 2. Push para o repositório
git push origin main

# 3. Monitorar deploy no GitHub Actions
```

## 📚 Documentação

- **[Guia de Deploy Kubernetes](docs/kubernetes-deployment-guide.md)** - Instruções completas de deploy
- **[API Documentation](docs/api-documentation.md)** - Documentação da API
- **[WhatsApp Integration](docs/whatsapp-integration.md)** - Configuração do WhatsApp
- **[Architecture Guide](docs/architecture.md)** - Arquitetura detalhada

## 🔧 Comandos Úteis

```bash
# Desenvolvimento
make dev              # Executar em desenvolvimento
make build            # Build da aplicação
make test             # Executar testes

# Docker
make docker-build     # Build da imagem Docker
make docker-run       # Executar container localmente
make docker-push      # Push para ECR

# Kubernetes
make k8s-deploy       # Deploy no Kubernetes
make k8s-status       # Status do deployment
make k8s-logs         # Logs da aplicação

# Infraestrutura
make terraform-plan   # Planejar mudanças
make terraform-apply  # Aplicar mudanças
```

## 🔗 Endpoints da API

### Health Check
- `GET /health` - Status da aplicação

### WhatsApp Integration
- `GET /api/whatsapp/webhook` - Verificação do webhook
- `POST /api/whatsapp/webhook` - Recebimento de mensagens
- `POST /api/whatsapp/send` - Envio de mensagens
- `GET /api/whatsapp/status` - Status da integração

### Analytics
- `GET /api/analytics/dashboard` - Dashboard de analytics
- `GET /api/analytics/insights` - Insights personalizados
- `GET /api/analytics/clients` - Análise de clientes

### Clients
- `GET /api/clients` - Listar clientes
- `GET /api/clients/:id` - Detalhes do cliente
- `POST /api/clients` - Criar cliente

## 🔐 Configuração de Secrets

### Kubernetes Secrets
```bash
# Configurar secrets automaticamente
./infrastructure/scripts/setup-secrets.sh create-prod
```

### GitHub Secrets
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `SLACK_WEBHOOK_URL` (opcional)

### Variáveis de Ambiente
```env
# WhatsApp Business API
WHATSAPP_TOKEN=your-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your-verify-token
WHATSAPP_WEBHOOK_SECRET=your-webhook-secret

# Application
JWT_SECRET=your-jwt-secret
DATABASE_URL=your-database-url
NODE_ENV=production
```

## 📊 Monitoramento

### Health Checks
```bash
# Verificar saúde da aplicação
curl https://your-domain.com/health

# Status do WhatsApp
curl https://your-domain.com/api/whatsapp/status
```

### Kubernetes
```bash
# Status dos pods
kubectl get pods -n whatsapp-analytics-prod

# Logs da aplicação
kubectl logs -f deployment/whatsapp-analytics-api -n whatsapp-analytics-prod

# Métricas de recursos
kubectl top pods -n whatsapp-analytics-prod
```

## 🔄 CI/CD Pipeline

### Workflow Principal
1. **Build & Test** - Compilação e testes
2. **Security Scan** - Análise de vulnerabilidades
3. **Docker Build** - Criação da imagem
4. **Deploy Staging** - Deploy automático para staging
5. **Deploy Production** - Deploy para produção (main branch)
6. **Notifications** - Notificações via Slack

### Ambientes
- **Development** - Branch feature/*
- **Staging** - Branch develop
- **Production** - Branch main

## 💰 Otimização de Custos

### Estratégias Implementadas
- **Spot Instances** - Até 90% de economia
- **Cluster Autoscaler** - Escala para zero quando não usado
- **Resource Limits** - Otimização de recursos
- **ECR Lifecycle** - Limpeza automática de imagens antigas

### Estimativa de Custos (Mensal)
- **EKS Cluster**: ~$73
- **EC2 Instances**: ~$50-150 (dependendo do uso)
- **Load Balancer**: ~$20
- **ECR Storage**: ~$5
- **Total Estimado**: ~$150-250/mês

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Equipe

- **Desenvolvedor Principal**: [Seu Nome]
- **DevOps Engineer**: [Seu Nome]
- **Arquiteto de Soluções**: [Seu Nome]

## 📞 Suporte

Para suporte e dúvidas:
- 📧 Email: suporte@datacompass.com
- 💬 Slack: #datacompass-support
- 🐛 Issues: [GitHub Issues](https://github.com/amarorn/dataCompass1.0/issues)

---

**DataCompass 1.0** - Transformando dados do WhatsApp em insights valiosos 🚀

