#!/bin/bash

# Deploy script for DataCompass with ultimatesystems.io domain
# This script deploys the infrastructure and application with custom domain configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN_NAME="ultimatesystems.io"
AWS_REGION="us-east-1"
CLUSTER_NAME="whatsapp-analytics-production"
NAMESPACE="whatsapp-analytics-prod"

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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if required tools are installed
    for tool in terraform kubectl helm aws; do
        if ! command -v $tool &> /dev/null; then
            log_error "$tool is not installed. Please install it first."
            exit 1
        fi
    done
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please run 'aws configure'."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Deploy Terraform infrastructure
deploy_terraform() {
    log_info "Deploying Terraform infrastructure..."
    
    cd infrastructure/terraform
    
    # Initialize Terraform
    terraform init
    
    # Plan the deployment
    terraform plan \
        -var="domain_name=${DOMAIN_NAME}" \
        -var="aws_region=${AWS_REGION}" \
        -var="environment=production" \
        -out=tfplan
    
    # Apply the plan
    terraform apply tfplan
    
    # Get outputs
    CERTIFICATE_ARN=$(terraform output -raw certificate_arn)
    ALB_DNS_NAME=$(terraform output -raw alb_dns_name)
    HOSTED_ZONE_ID=$(terraform output -raw hosted_zone_id)
    
    log_success "Terraform infrastructure deployed successfully"
    log_info "Certificate ARN: $CERTIFICATE_ARN"
    log_info "ALB DNS Name: $ALB_DNS_NAME"
    log_info "Hosted Zone ID: $HOSTED_ZONE_ID"
    
    cd ../..
}

# Update Kubernetes configurations
update_k8s_configs() {
    log_info "Updating Kubernetes configurations..."
    
    # Update Ingress with certificate ARN
    sed -i "s/CERTIFICATE_ARN_PLACEHOLDER/${CERTIFICATE_ARN}/g" k8s/base/ingress.yaml
    sed -i "s/CERTIFICATE_ARN_PLACEHOLDER/${CERTIFICATE_ARN}/g" k8s/overlays/production/ingress-patch.yaml
    
    log_success "Kubernetes configurations updated"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    log_info "Deploying to Kubernetes..."
    
    # Update kubeconfig
    aws eks update-kubeconfig --region $AWS_REGION --name $CLUSTER_NAME
    
    # Create namespace if it doesn't exist
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply base configurations
    kubectl apply -k k8s/overlays/production -n $NAMESPACE
    
    # Wait for deployment to be ready
    kubectl rollout status deployment/whatsapp-analytics-api -n $NAMESPACE --timeout=300s
    
    log_success "Kubernetes deployment completed"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check if pods are running
    kubectl get pods -n $NAMESPACE
    
    # Check ingress
    kubectl get ingress -n $NAMESPACE
    
    # Test health endpoint
    log_info "Testing health endpoints..."
    
    for subdomain in "" "api." "administrativo." "dashboard."; do
        url="https://${subdomain}${DOMAIN_NAME}/health"
        log_info "Testing $url"
        
        # Wait for DNS propagation and SSL certificate
        for i in {1..10}; do
            if curl -s -f -k "$url" > /dev/null; then
                log_success "$url is responding"
                break
            else
                log_warning "Attempt $i: $url not ready yet, waiting 30s..."
                sleep 30
            fi
        done
    done
}

# Setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Deploy Prometheus and Grafana if enabled
    if kubectl get namespace monitoring &> /dev/null; then
        log_info "Monitoring namespace already exists"
    else
        kubectl create namespace monitoring
        
        # Add Prometheus Helm repo
        helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
        helm repo update
        
        # Install Prometheus
        helm install prometheus prometheus-community/kube-prometheus-stack \
            --namespace monitoring \
            --set grafana.adminPassword=admin123 \
            --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
    fi
    
    log_success "Monitoring setup completed"
}

# Main deployment function
main() {
    log_info "Starting DataCompass deployment with domain: $DOMAIN_NAME"
    
    check_prerequisites
    deploy_terraform
    update_k8s_configs
    deploy_kubernetes
    verify_deployment
    setup_monitoring
    
    log_success "Deployment completed successfully!"
    log_info "Your application is now available at:"
    log_info "  - Main site: https://$DOMAIN_NAME"
    log_info "  - API: https://api.$DOMAIN_NAME"
    log_info "  - Admin: https://administrativo.$DOMAIN_NAME"
    log_info "  - Dashboard: https://dashboard.$DOMAIN_NAME"
    
    log_warning "Note: DNS propagation may take up to 48 hours to complete globally."
    log_warning "SSL certificates will be automatically provisioned and may take a few minutes."
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "terraform-only")
        check_prerequisites
        deploy_terraform
        ;;
    "k8s-only")
        check_prerequisites
        deploy_kubernetes
        verify_deployment
        ;;
    "verify")
        verify_deployment
        ;;
    "monitoring")
        setup_monitoring
        ;;
    *)
        echo "Usage: $0 [deploy|terraform-only|k8s-only|verify|monitoring]"
        echo "  deploy        - Full deployment (default)"
        echo "  terraform-only - Deploy only Terraform infrastructure"
        echo "  k8s-only      - Deploy only Kubernetes resources"
        echo "  verify        - Verify existing deployment"
        echo "  monitoring    - Setup monitoring stack"
        exit 1
        ;;
esac

