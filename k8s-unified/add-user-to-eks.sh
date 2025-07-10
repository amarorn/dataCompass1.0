#!/bin/bash

# Script para adicionar usuário ao EKS via AWS CLI
# Alternativa quando não temos acesso direto ao kubectl

echo "🔧 Adicionando usuário datacompass-ci-cd ao EKS cluster"
echo "======================================================"

# Verificar se temos acesso ao EKS
if ! aws eks describe-cluster --name whatsapp-analytics-production --region us-east-1 > /dev/null 2>&1; then
    echo "❌ Sem acesso ao cluster EKS"
    exit 1
fi

echo "✅ Cluster EKS acessível"

# Tentar usar eksctl se disponível
if command -v eksctl > /dev/null 2>&1; then
    echo "🔧 Usando eksctl para adicionar usuário..."
    eksctl create iamidentitymapping \
        --cluster whatsapp-analytics-production \
        --region us-east-1 \
        --arn arn:aws:iam::028425947301:user/datacompass-ci-cd \
        --group system:masters \
        --username datacompass-ci-cd
    
    if [ $? -eq 0 ]; then
        echo "✅ Usuário adicionado com sucesso via eksctl!"
        echo "🔄 Aguardando propagação..."
        sleep 10
        
        echo "🧪 Testando acesso..."
        if kubectl get nodes > /dev/null 2>&1; then
            echo "✅ Acesso ao EKS funcionando!"
            echo "🚀 Agora você pode executar: ./deploy.sh"
        else
            echo "⚠️ Ainda aguardando propagação. Tente novamente em alguns minutos."
        fi
    else
        echo "❌ Falha ao adicionar usuário via eksctl"
    fi
else
    echo "❌ eksctl não disponível"
    echo "💡 Solução: Execute este comando em um ambiente com eksctl instalado"
    echo "   ou use o AWS Console para adicionar o usuário ao aws-auth ConfigMap"
fi
