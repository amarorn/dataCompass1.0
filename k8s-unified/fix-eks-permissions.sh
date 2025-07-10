#!/bin/bash

# Script para corrigir permissões EKS
# Este script deve ser executado por um usuário com permissões de administrador do cluster

echo "🔧 Corrigindo permissões EKS para usuário datacompass-ci-cd"
echo "=================================================="

# Verificar se kubectl funciona
if ! kubectl get nodes > /dev/null 2>&1; then
    echo "❌ kubectl não está funcionando. Execute este script com um usuário admin do cluster."
    exit 1
fi

echo "✅ kubectl funcionando. Adicionando usuário ao aws-auth ConfigMap..."

# Backup do configmap atual
kubectl get configmap aws-auth -n kube-system -o yaml > aws-auth-backup.yaml

# Adicionar usuário ao aws-auth
kubectl patch configmap aws-auth -n kube-system --patch '
data:
  mapUsers: |
    - userarn: arn:aws:iam::028425947301:user/datacompass-ci-cd
      username: datacompass-ci-cd
      groups:
        - system:masters
'

echo "✅ Usuário adicionado ao aws-auth ConfigMap"
echo "🔄 Aguarde alguns segundos para a propagação..."
sleep 10

echo "🧪 Testando acesso..."
if kubectl get nodes > /dev/null 2>&1; then
    echo "✅ Acesso ao EKS configurado com sucesso!"
else
    echo "❌ Ainda há problemas de acesso. Verifique as permissões IAM."
fi
