#!/bin/bash

# Script de Deploy Automatizado - DataCompass
# Configuração unificada para Frontend e Backend

set -e

echo "🚀 Iniciando Deploy do DataCompass..."
echo "=================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logs coloridos
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

# Verificar se kubectl está configurado
log_info "Verificando configuração do kubectl..."
if ! kubectl cluster-info &> /dev/null; then
    log_error "kubectl não está configurado ou cluster não está acessível"
    exit 1
fi
log_success "kubectl configurado corretamente"

# Verificar namespace
log_info "Verificando namespace default..."
kubectl get namespace default &> /dev/null || {
    log_error "Namespace default não encontrado"
    exit 1
}

# Aplicar secrets primeiro
log_info "Aplicando secrets..."
kubectl apply -f secrets.yaml
log_success "Secrets aplicados"

# Aplicar deployments
log_info "Aplicando deployment do backend..."
kubectl apply -f backend-deployment.yaml
log_success "Backend deployment aplicado"

log_info "Aplicando deployment do frontend..."
kubectl apply -f frontend-deployment.yaml
log_success "Frontend deployment aplicado"

# Aplicar ingress
log_info "Aplicando ingress unificado..."
kubectl apply -f ingress-unified.yaml
log_success "Ingress aplicado"

# Aguardar pods ficarem prontos
log_info "Aguardando pods do backend ficarem prontos..."
kubectl wait --for=condition=ready pod -l app=datacompass-api --timeout=300s

log_info "Aguardando pods do frontend ficarem prontos..."
kubectl wait --for=condition=ready pod -l app=datacompass-frontend --timeout=300s

# Verificar status dos deployments
log_info "Verificando status dos deployments..."
echo ""
echo "=== STATUS DOS PODS ==="
kubectl get pods -l project=datacompass

echo ""
echo "=== STATUS DOS SERVICES ==="
kubectl get services -l project=datacompass

echo ""
echo "=== STATUS DO INGRESS ==="
kubectl get ingress datacompass-unified-ingress

echo ""
echo "=== ENDPOINTS DISPONÍVEIS ==="
echo "🌐 API Backend: http://api.ultimatesystems.io"
echo "🌐 Frontend Dashboard: http://dashboard.ultimatesystems.io"
echo "🌐 Domínio Principal: http://ultimatesystems.io"
echo "🌐 Painel Admin: http://administrativo.ultimatesystems.io"

echo ""
log_success "Deploy concluído com sucesso!"
echo "=================================="

# Teste básico de conectividade
log_info "Executando testes básicos..."
echo ""

# Teste interno do cluster
log_info "Testando conectividade interna..."
if kubectl exec -it deployment/datacompass-api -- curl -s http://datacompass-api-service/health > /dev/null; then
    log_success "✅ API interna respondendo"
else
    log_warning "⚠️ API interna não respondendo"
fi

echo ""
log_info "Para monitorar os logs:"
echo "Backend:  kubectl logs -f deployment/datacompass-api"
echo "Frontend: kubectl logs -f deployment/datacompass-frontend"

echo ""
log_info "Para verificar detalhes:"
echo "kubectl describe ingress datacompass-unified-ingress"
echo "kubectl get pods -o wide"

echo ""
log_success "🎉 DataCompass deployado com sucesso na AWS!"

