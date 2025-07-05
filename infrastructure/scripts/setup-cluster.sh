#!/bin/bash

# WhatsApp Analytics - EKS Cluster Setup Script
# This script automates the creation of the EKS cluster and required infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="whatsapp-analytics"
ENVIRONMENT="production"
AWS_REGION="us-east-1"
TERRAFORM_DIR="$(dirname "$0")/../terraform"

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

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if Terraform is installed
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install it first."
        exit 1
    fi
    
    # Check if kustomize is installed
    if ! command -v kustomize &> /dev/null; then
        log_warning "kustomize is not installed. Installing..."
        curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
        sudo mv kustomize /usr/local/bin/
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    log_success "All prerequisites met!"
}

setup_terraform_backend() {
    log_info "Setting up Terraform backend..."
    
    # Create S3 bucket for Terraform state
    BUCKET_NAME="${PROJECT_NAME}-terraform-state-$(date +%s)"
    
    aws s3 mb "s3://${BUCKET_NAME}" --region "${AWS_REGION}" || {
        log_warning "Bucket creation failed or bucket already exists"
    }
    
    # Enable versioning
    aws s3api put-bucket-versioning \
        --bucket "${BUCKET_NAME}" \
        --versioning-configuration Status=Enabled
    
    # Create DynamoDB table for state locking
    aws dynamodb create-table \
        --table-name "${PROJECT_NAME}-terraform-locks" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
        --region "${AWS_REGION}" || {
        log_warning "DynamoDB table creation failed or table already exists"
    }
    
    log_success "Terraform backend configured with bucket: ${BUCKET_NAME}"
    
    # Update terraform configuration
    cat > "${TERRAFORM_DIR}/backend.tf" << EOF
terraform {
  backend "s3" {
    bucket         = "${BUCKET_NAME}"
    key            = "${PROJECT_NAME}/terraform.tfstate"
    region         = "${AWS_REGION}"
    dynamodb_table = "${PROJECT_NAME}-terraform-locks"
    encrypt        = true
  }
}
EOF
}

deploy_infrastructure() {
    log_info "Deploying infrastructure with Terraform..."
    
    cd "${TERRAFORM_DIR}"
    
    # Initialize Terraform
    terraform init
    
    # Create terraform.tfvars if it doesn't exist
    if [ ! -f "terraform.tfvars" ]; then
        cat > terraform.tfvars << EOF
aws_region   = "${AWS_REGION}"
environment  = "${ENVIRONMENT}"
project_name = "${PROJECT_NAME}"

# Customize these values as needed
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
EOF
        log_info "Created terraform.tfvars file. Please review and customize it."
    fi
    
    # Plan
    terraform plan -out=tfplan
    
    # Ask for confirmation
    read -p "Do you want to apply this plan? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Apply
        terraform apply tfplan
        log_success "Infrastructure deployed successfully!"
    else
        log_info "Deployment cancelled."
        exit 0
    fi
    
    cd - > /dev/null
}

configure_kubectl() {
    log_info "Configuring kubectl..."
    
    # Update kubeconfig
    aws eks update-kubeconfig \
        --region "${AWS_REGION}" \
        --name "${PROJECT_NAME}-${ENVIRONMENT}"
    
    # Test connection
    kubectl cluster-info
    
    log_success "kubectl configured successfully!"
}

install_cluster_addons() {
    log_info "Installing cluster addons..."
    
    # Install AWS Load Balancer Controller
    curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.5.4/docs/install/iam_policy.json
    
    aws iam create-policy \
        --policy-name AWSLoadBalancerControllerIAMPolicy \
        --policy-document file://iam_policy.json || {
        log_warning "IAM policy already exists"
    }
    
    # Create service account
    eksctl create iamserviceaccount \
        --cluster="${PROJECT_NAME}-${ENVIRONMENT}" \
        --namespace=kube-system \
        --name=aws-load-balancer-controller \
        --role-name AmazonEKSLoadBalancerControllerRole \
        --attach-policy-arn=arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/AWSLoadBalancerControllerIAMPolicy \
        --approve || {
        log_warning "Service account already exists"
    }
    
    # Install with Helm
    helm repo add eks https://aws.github.io/eks-charts
    helm repo update
    
    helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
        -n kube-system \
        --set clusterName="${PROJECT_NAME}-${ENVIRONMENT}" \
        --set serviceAccount.create=false \
        --set serviceAccount.name=aws-load-balancer-controller || {
        log_warning "AWS Load Balancer Controller already installed"
    }
    
    log_success "Cluster addons installed!"
}

create_namespaces() {
    log_info "Creating Kubernetes namespaces..."
    
    kubectl create namespace whatsapp-analytics-prod || {
        log_warning "Namespace already exists"
    }
    
    kubectl create namespace whatsapp-analytics-staging || {
        log_warning "Namespace already exists"
    }
    
    log_success "Namespaces created!"
}

main() {
    log_info "Starting WhatsApp Analytics EKS cluster setup..."
    
    check_prerequisites
    setup_terraform_backend
    deploy_infrastructure
    configure_kubectl
    install_cluster_addons
    create_namespaces
    
    log_success "EKS cluster setup completed successfully!"
    log_info "Next steps:"
    echo "1. Configure your secrets in Kubernetes"
    echo "2. Update your GitHub repository secrets"
    echo "3. Push your code to trigger the CI/CD pipeline"
    echo "4. Monitor the deployment in the GitHub Actions"
}

# Run main function
main "$@"

