#!/bin/bash

# Script para fazer commit de toda a configuração no repositório GitHub
# DataCompass 1.0 - WhatsApp Analytics Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
REPO_URL="https://github.com/amarorn/dataCompass1.0.git"
REPO_NAME="dataCompass1.0"

main() {
    log_info "🚀 Iniciando commit para o repositório GitHub..."
    
    # Check if git is installed
    if ! command -v git &> /dev/null; then
        log_error "Git não está instalado. Por favor, instale o Git primeiro."
        exit 1
    fi
    
    # Check if we're in the right directory
    if [ ! -f "package.json" ] || [ ! -d "k8s" ]; then
        log_error "Este script deve ser executado no diretório raiz do projeto."
        exit 1
    fi
    
    log_info "📁 Verificando estrutura do projeto..."
    
    # List important files/directories
    echo "Arquivos e diretórios que serão commitados:"
    echo "✅ src/ - Código fonte da aplicação"
    echo "✅ k8s/ - Manifests Kubernetes"
    echo "✅ infrastructure/ - Terraform e scripts"
    echo "✅ .github/workflows/ - CI/CD pipelines"
    echo "✅ Dockerfile - Containerização"
    echo "✅ Makefile - Comandos de automação"
    echo "✅ docs/ - Documentação"
    echo "✅ README.md - Documentação principal"
    echo ""
    
    # Check if this is already a git repository
    if [ -d ".git" ]; then
        log_info "📦 Repositório Git já existe. Fazendo commit das mudanças..."
        
        # Add all files
        git add .
        
        # Check if there are changes to commit
        if git diff --staged --quiet; then
            log_warning "Nenhuma mudança para commit."
            exit 0
        fi
        
        # Commit changes
        git commit -m "feat: add complete Kubernetes and CI/CD configuration

- Add Docker containerization with multi-stage builds
- Add Kubernetes manifests for production deployment
- Add Terraform infrastructure as code for AWS EKS
- Add GitHub Actions CI/CD pipeline
- Add comprehensive documentation
- Add automation scripts and Makefile
- Add WhatsApp Business API integration
- Add analytics and insights system
- Add security best practices and monitoring"
        
        log_success "✅ Commit realizado com sucesso!"
        
        # Push to remote
        log_info "📤 Fazendo push para o repositório remoto..."
        git push origin main || git push origin master
        
        log_success "🎉 Push realizado com sucesso!"
        
    else
        log_info "🔧 Inicializando novo repositório Git..."
        
        # Initialize git repository
        git init
        
        # Add remote origin
        git remote add origin "$REPO_URL"
        
        # Create main branch
        git checkout -b main
        
        # Add all files
        git add .
        
        # Initial commit
        git commit -m "feat: initial commit - DataCompass 1.0 WhatsApp Analytics Platform

Complete implementation including:
- Node.js + TypeScript backend with Clean Architecture
- WhatsApp Business API integration with webhook processing
- Intelligent message processing with sentiment analysis
- Client analytics and insights system
- Docker containerization with security best practices
- Kubernetes deployment manifests for AWS EKS
- Terraform infrastructure as code
- GitHub Actions CI/CD pipeline
- Comprehensive documentation and automation scripts

Features:
✅ WhatsApp webhook processing with HMAC validation
✅ Sentiment analysis and message categorization
✅ Client segmentation and engagement scoring
✅ Auto-scaling Kubernetes deployment
✅ Infrastructure as code with Terraform
✅ Automated CI/CD with GitHub Actions
✅ Security scanning and monitoring
✅ Cost optimization with spot instances
✅ Zero-downtime deployments
✅ Comprehensive documentation"
        
        log_success "✅ Commit inicial realizado!"
        
        # Push to remote
        log_info "📤 Fazendo push inicial para o repositório remoto..."
        git push -u origin main
        
        log_success "🎉 Push inicial realizado com sucesso!"
    fi
    
    log_info "📋 Próximos passos:"
    echo ""
    echo "1. 🔐 Configurar secrets no GitHub:"
    echo "   - Vá para Settings > Secrets and variables > Actions"
    echo "   - Adicione: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY"
    echo ""
    echo "2. 🏗️ Configurar infraestrutura AWS:"
    echo "   - Execute: make terraform-init"
    echo "   - Execute: make terraform-apply"
    echo ""
    echo "3. 🔑 Configurar secrets do Kubernetes:"
    echo "   - Execute: make setup-secrets"
    echo ""
    echo "4. 🚀 Deploy da aplicação:"
    echo "   - Execute: make k8s-deploy"
    echo "   - Ou faça push para main para deploy automático"
    echo ""
    echo "5. 📊 Monitorar deployment:"
    echo "   - GitHub Actions: https://github.com/amarorn/dataCompass1.0/actions"
    echo "   - Kubernetes: make k8s-status"
    echo ""
    
    log_success "🎉 Configuração completa commitada com sucesso!"
    log_info "🔗 Repositório: https://github.com/amarorn/dataCompass1.0"
}

# Run main function
main "$@"

