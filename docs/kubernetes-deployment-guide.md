# Guia de Deploy no Kubernetes AWS (EKS)

## 📋 Visão Geral

Este guia fornece instruções completas para fazer deploy da aplicação WhatsApp Analytics no Amazon EKS (Elastic Kubernetes Service) com automação completa via CI/CD.

## 🏗️ Arquitetura da Solução

### Componentes Principais

1. **Amazon EKS** - Cluster Kubernetes gerenciado
2. **Amazon ECR** - Registry de imagens Docker
3. **Application Load Balancer** - Balanceador de carga
4. **Auto Scaling** - Escalabilidade automática
5. **GitHub Actions** - CI/CD Pipeline
6. **Terraform** - Infraestrutura como código

### Estrutura do Projeto

```
whatsapp-analytics-api/
├── Dockerfile                     # Containerização da aplicação
├── .dockerignore                  # Arquivos ignorados no build
├── k8s/                          # Manifests Kubernetes
│   ├── base/                     # Configurações base
│   │   ├── deployment.yaml       # Deployment da aplicação
│   │   ├── service.yaml          # Service interno
│   │   ├── configmap.yaml        # Configurações não-sensíveis
│   │   ├── secret.yaml           # Template de secrets
│   │   ├── ingress.yaml          # Exposição externa
│   │   ├── hpa.yaml              # Auto-scaling
│   │   └── kustomization.yaml    # Kustomize base
│   └── overlays/                 # Configurações por ambiente
│       ├── production/           # Ambiente de produção
│       └── staging/              # Ambiente de staging
├── infrastructure/               # Infraestrutura como código
│   ├── terraform/               # Configurações Terraform
│   │   ├── main.tf              # Configuração principal
│   │   ├── variables.tf         # Variáveis
│   │   ├── vpc.tf               # Configuração VPC
│   │   ├── eks.tf               # Cluster EKS
│   │   ├── ecr.tf               # Registry ECR
│   │   └── outputs.tf           # Outputs
│   └── scripts/                 # Scripts de automação
│       ├── setup-cluster.sh     # Setup do cluster
│       └── setup-secrets.sh     # Configuração de secrets
└── .github/workflows/           # CI/CD Pipelines
    ├── ci-cd.yml               # Pipeline principal
    └── infrastructure.yml      # Gerenciamento de infraestrutura
```

## 🚀 Pré-requisitos

### Ferramentas Necessárias

1. **AWS CLI** (v2.x)
   ```bash
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```

2. **Terraform** (v1.6+)
   ```bash
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   ```

3. **kubectl** (v1.28+)
   ```bash
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
   sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
   ```

4. **eksctl** (v0.150+)
   ```bash
   curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
   sudo mv /tmp/eksctl /usr/local/bin
   ```

5. **Helm** (v3.x)
   ```bash
   curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
   ```

6. **Kustomize** (v5.x)
   ```bash
   curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
   sudo mv kustomize /usr/local/bin/
   ```

### Configuração AWS

1. **Configurar credenciais AWS:**
   ```bash
   aws configure
   ```

2. **Verificar acesso:**
   ```bash
   aws sts get-caller-identity
   ```

3. **Permissões necessárias:**
   - EKS Full Access
   - EC2 Full Access
   - VPC Full Access
   - IAM Full Access
   - ECR Full Access
   - S3 Full Access
   - DynamoDB Full Access

## 🔧 Setup da Infraestrutura

### 1. Configuração Inicial

1. **Clone o repositório:**
   ```bash
   git clone <repository-url>
   cd whatsapp-analytics-api
   ```

2. **Torne os scripts executáveis:**
   ```bash
   chmod +x infrastructure/scripts/*.sh
   ```

### 2. Deploy Automatizado

Execute o script de setup completo:

```bash
./infrastructure/scripts/setup-cluster.sh
```

Este script irá:
- ✅ Verificar pré-requisitos
- ✅ Configurar backend do Terraform
- ✅ Criar infraestrutura AWS
- ✅ Configurar kubectl
- ✅ Instalar addons do cluster
- ✅ Criar namespaces

### 3. Deploy Manual (Alternativo)

Se preferir fazer o deploy manual:

#### 3.1 Configurar Backend do Terraform

```bash
cd infrastructure/terraform

# Criar bucket S3 para state
aws s3 mb s3://whatsapp-analytics-terraform-state-$(date +%s)

# Criar tabela DynamoDB para locking
aws dynamodb create-table \
  --table-name whatsapp-analytics-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

#### 3.2 Configurar Variáveis

Crie o arquivo `terraform.tfvars`:

```hcl
aws_region   = "us-east-1"
environment  = "production"
project_name = "whatsapp-analytics"

cluster_version = "1.28"
domain_name     = "whatsapp-analytics.com"

node_groups = {
  general = {
    instance_types = ["t3.medium"]
    min_size       = 2
    max_size       = 10
    desired_size   = 3
    capacity_type  = "ON_DEMAND"
    disk_size      = 20
  }
  spot = {
    instance_types = ["t3.medium", "t3a.medium"]
    min_size       = 0
    max_size       = 5
    desired_size   = 2
    capacity_type  = "SPOT"
    disk_size      = 20
  }
}
```

#### 3.3 Deploy da Infraestrutura

```bash
# Inicializar Terraform
terraform init

# Planejar mudanças
terraform plan

# Aplicar mudanças
terraform apply
```

#### 3.4 Configurar kubectl

```bash
aws eks update-kubeconfig --region us-east-1 --name whatsapp-analytics-production
```

## 🔐 Configuração de Secrets

### 1. Configuração Automática

Use o script de configuração de secrets:

```bash
./infrastructure/scripts/setup-secrets.sh create-prod
```

### 2. Configuração Manual

#### 2.1 Criar Secrets do Kubernetes

```bash
kubectl create secret generic whatsapp-analytics-secrets \
  --namespace=whatsapp-analytics-prod \
  --from-literal=jwt-secret="your-jwt-secret" \
  --from-literal=whatsapp-token="your-whatsapp-token" \
  --from-literal=whatsapp-phone-number-id="your-phone-number-id" \
  --from-literal=whatsapp-webhook-verify-token="your-verify-token" \
  --from-literal=whatsapp-webhook-secret="your-webhook-secret" \
  --from-literal=database-url="postgresql://user:pass@host:5432/db"
```

#### 2.2 Configurar Secrets do GitHub

No GitHub, vá para **Settings > Secrets and variables > Actions** e adicione:

- `AWS_ACCESS_KEY_ID`: Sua AWS Access Key ID
- `AWS_SECRET_ACCESS_KEY`: Sua AWS Secret Access Key
- `SLACK_WEBHOOK_URL`: (Opcional) Webhook do Slack para notificações

## 🚢 Deploy da Aplicação

### 1. Via CI/CD (Recomendado)

1. **Push para o repositório:**
   ```bash
   git add .
   git commit -m "feat: setup kubernetes deployment"
   git push origin main
   ```

2. **Monitorar o pipeline:**
   - Acesse GitHub Actions
   - Acompanhe o workflow "CI/CD Pipeline"

### 2. Deploy Manual

#### 2.1 Build e Push da Imagem

```bash
# Login no ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build da imagem
docker build -t whatsapp-analytics-api .

# Tag da imagem
docker tag whatsapp-analytics-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/whatsapp-analytics-api:latest

# Push da imagem
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/whatsapp-analytics-api:latest
```

#### 2.2 Deploy no Kubernetes

```bash
cd k8s/overlays/production

# Atualizar imagem no kustomization
kustomize edit set image whatsapp-analytics-api=<account-id>.dkr.ecr.us-east-1.amazonaws.com/whatsapp-analytics-api:latest

# Aplicar manifests
kubectl apply -k .
```

#### 2.3 Verificar Deploy

```bash
# Verificar pods
kubectl get pods -n whatsapp-analytics-prod

# Verificar serviços
kubectl get services -n whatsapp-analytics-prod

# Verificar ingress
kubectl get ingress -n whatsapp-analytics-prod

# Logs da aplicação
kubectl logs -f deployment/whatsapp-analytics-api -n whatsapp-analytics-prod
```

## 🔍 Monitoramento e Troubleshooting

### Comandos Úteis

```bash
# Status do cluster
kubectl cluster-info

# Nodes do cluster
kubectl get nodes

# Pods em todos os namespaces
kubectl get pods --all-namespaces

# Eventos do cluster
kubectl get events --sort-by=.metadata.creationTimestamp

# Logs de um pod específico
kubectl logs <pod-name> -n <namespace>

# Executar shell em um pod
kubectl exec -it <pod-name> -n <namespace> -- /bin/sh

# Port forward para teste local
kubectl port-forward service/whatsapp-analytics-api-service 8080:80 -n whatsapp-analytics-prod
```

### Health Checks

```bash
# Verificar health da aplicação
curl -f https://your-domain.com/health

# Verificar status do WhatsApp
curl -f https://your-domain.com/api/whatsapp/status

# Teste de processamento
curl -X POST https://your-domain.com/api/whatsapp/test \
  -H "Content-Type: application/json" \
  -d '{"message": "Teste de mensagem"}'
```

### Logs e Debugging

```bash
# Logs do deployment
kubectl logs deployment/whatsapp-analytics-api -n whatsapp-analytics-prod --tail=100

# Logs do ingress controller
kubectl logs -n kube-system deployment/aws-load-balancer-controller

# Descrever recursos para debugging
kubectl describe pod <pod-name> -n whatsapp-analytics-prod
kubectl describe service whatsapp-analytics-api-service -n whatsapp-analytics-prod
kubectl describe ingress whatsapp-analytics-ingress -n whatsapp-analytics-prod
```

## 📊 Escalabilidade e Performance

### Auto Scaling

O HPA (Horizontal Pod Autoscaler) está configurado para:
- **Mínimo**: 2 pods
- **Máximo**: 10 pods
- **CPU Target**: 70%
- **Memory Target**: 80%

### Monitoramento de Recursos

```bash
# Uso de recursos dos pods
kubectl top pods -n whatsapp-analytics-prod

# Uso de recursos dos nodes
kubectl top nodes

# Status do HPA
kubectl get hpa -n whatsapp-analytics-prod
```

### Ajuste de Recursos

Para ajustar recursos, edite o arquivo `k8s/overlays/production/deployment-patch.yaml`:

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

## 🔄 Atualizações e Rollbacks

### Rolling Updates

```bash
# Atualizar imagem
kubectl set image deployment/whatsapp-analytics-api whatsapp-analytics-api=<new-image> -n whatsapp-analytics-prod

# Verificar status do rollout
kubectl rollout status deployment/whatsapp-analytics-api -n whatsapp-analytics-prod

# Histórico de rollouts
kubectl rollout history deployment/whatsapp-analytics-api -n whatsapp-analytics-prod
```

### Rollbacks

```bash
# Rollback para versão anterior
kubectl rollout undo deployment/whatsapp-analytics-api -n whatsapp-analytics-prod

# Rollback para versão específica
kubectl rollout undo deployment/whatsapp-analytics-api --to-revision=2 -n whatsapp-analytics-prod
```

## 🔒 Segurança

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: whatsapp-analytics-netpol
  namespace: whatsapp-analytics-prod
spec:
  podSelector:
    matchLabels:
      app: whatsapp-analytics-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: TCP
      port: 3000
  egress:
  - {}
```

### Pod Security Standards

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: whatsapp-analytics-prod
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

## 🗄️ Backup e Disaster Recovery

### Backup de Secrets

```bash
# Backup de secrets
kubectl get secret whatsapp-analytics-secrets -n whatsapp-analytics-prod -o yaml > secrets-backup.yaml

# Backup de configmaps
kubectl get configmap whatsapp-analytics-config -n whatsapp-analytics-prod -o yaml > configmap-backup.yaml
```

### Backup do Estado do Terraform

```bash
# Download do state
terraform state pull > terraform-state-backup.json

# Upload do state (se necessário)
terraform state push terraform-state-backup.json
```

## 💰 Otimização de Custos

### Spot Instances

O cluster está configurado com node groups spot para reduzir custos:

```hcl
spot = {
  instance_types = ["t3.medium", "t3a.medium"]
  capacity_type  = "SPOT"
  min_size       = 0
  max_size       = 5
  desired_size   = 2
}
```

### Cluster Autoscaler

```bash
# Verificar status do cluster autoscaler
kubectl logs -f deployment/cluster-autoscaler -n kube-system
```

### Monitoramento de Custos

- Use AWS Cost Explorer
- Configure alertas de billing
- Monitore uso de recursos com kubectl top

## 🚨 Troubleshooting Comum

### Pod não inicia

```bash
# Verificar eventos
kubectl describe pod <pod-name> -n whatsapp-analytics-prod

# Verificar logs
kubectl logs <pod-name> -n whatsapp-analytics-prod

# Verificar recursos
kubectl top pod <pod-name> -n whatsapp-analytics-prod
```

### Ingress não funciona

```bash
# Verificar ingress
kubectl describe ingress whatsapp-analytics-ingress -n whatsapp-analytics-prod

# Verificar AWS Load Balancer Controller
kubectl logs -n kube-system deployment/aws-load-balancer-controller

# Verificar security groups
aws ec2 describe-security-groups --group-ids <sg-id>
```

### Problemas de conectividade

```bash
# Testar conectividade interna
kubectl run test-pod --image=busybox -it --rm -- /bin/sh

# Dentro do pod de teste
nslookup whatsapp-analytics-api-service.whatsapp-analytics-prod.svc.cluster.local
wget -qO- http://whatsapp-analytics-api-service.whatsapp-analytics-prod.svc.cluster.local/health
```

## 📚 Recursos Adicionais

- [Amazon EKS Documentation](https://docs.aws.amazon.com/eks/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Kustomize Documentation](https://kustomize.io/)

## 🆘 Suporte

Para problemas ou dúvidas:

1. Verifique os logs da aplicação
2. Consulte a documentação do Kubernetes
3. Verifique os eventos do cluster
4. Abra uma issue no repositório do projeto

