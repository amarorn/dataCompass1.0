#!/bin/bash

# Script para executar deploy assim que o acesso EKS for configurado
echo "🚀 Deploy DataCompass - Aguardando Acesso EKS"
echo "=============================================="

# Função para testar acesso
test_access() {
    kubectl get nodes > /dev/null 2>&1
    return $?
}

# Aguardar acesso (máximo 30 tentativas = 5 minutos)
echo "⏳ Aguardando configuração de acesso ao EKS..."
for i in {1..30}; do
    if test_access; then
        echo "✅ Acesso ao EKS detectado!"
        break
    fi
    echo "Tentativa $i/30 - Aguardando acesso..."
    sleep 10
done

# Verificar se conseguiu acesso
if ! test_access; then
    echo "❌ Timeout: Acesso ao EKS não foi configurado"
    echo "💡 Configure manualmente via AWS Console e execute: ./deploy.sh"
    exit 1
fi

echo ""
echo "🎯 Iniciando deploy do DataCompass..."
echo ""

# Executar deploy
./deploy.sh

echo ""
echo "🎉 Deploy concluído!"
echo "🌐 Teste os domínios:"
echo "- API: http://api.ultimatesystems.io"
echo "- Dashboard: http://dashboard.ultimatesystems.io"
