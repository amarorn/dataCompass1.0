#!/bin/bash

# DataCompass Python - Kubernetes Deployment Script
# This script deploys the DataCompass Python application to Kubernetes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="datacompass-python"
APP_NAME="datacompass-python"
DOCKER_IMAGE="datacompass-python:latest"
DOCKER_REGISTRY="your-registry.com"  # Change this to your Docker registry

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
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if we can connect to Kubernetes cluster
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

build_and_push_image() {
    log_info "Building Docker image..."
    
    # Build the Docker image
    docker build -t ${DOCKER_IMAGE} .
    
    # Tag for registry
    docker tag ${DOCKER_IMAGE} ${DOCKER_REGISTRY}/${DOCKER_IMAGE}
    
    # Push to registry
    log_info "Pushing image to registry..."
    docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}
    
    log_success "Docker image built and pushed successfully"
}

update_image_reference() {
    log_info "Updating image reference in Kubernetes manifests..."
    
    # Update the image reference in the deployment
    sed -i "s|image: datacompass-python:latest|image: ${DOCKER_REGISTRY}/datacompass-python:latest|g" app-deployment.yaml
    
    log_success "Image reference updated"
}

deploy_to_kubernetes() {
    log_info "Deploying to Kubernetes..."
    
    # Apply all manifests
    kubectl apply -k .
    
    # Wait for deployment to be ready
    log_info "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/${APP_NAME}-app -n ${NAMESPACE}
    
    log_success "Deployment completed successfully"
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check if pods are running
    kubectl get pods -n ${NAMESPACE}
    
    # Check if services are created
    kubectl get services -n ${NAMESPACE}
    
    # Check if ingress is created
    kubectl get ingress -n ${NAMESPACE}
    
    log_success "Deployment verification completed"
}

show_access_info() {
    log_info "Deployment completed! Here's how to access your application:"
    
    echo ""
    echo "📋 Access Information:"
    echo "====================="
    
    # Get ingress information
    INGRESS_HOST=$(kubectl get ingress ${APP_NAME}-ingress -n ${NAMESPACE} -o jsonpath='{.spec.rules[0].host}' 2>/dev/null || echo "Not configured")
    INGRESS_IP=$(kubectl get ingress ${APP_NAME}-ingress -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "Not available")
    
    echo "🌐 Application URL: https://${INGRESS_HOST}"
    echo "📊 API Documentation: https://${INGRESS_HOST}/docs"
    echo "❤️  Health Check: https://${INGRESS_HOST}/health"
    echo "📱 WhatsApp Webhook: https://${INGRESS_HOST}/api/whatsapp/webhook"
    
    echo ""
    echo "🔧 Useful Commands:"
    echo "==================="
    echo "kubectl get pods -n ${NAMESPACE}"
    echo "kubectl logs -f deployment/${APP_NAME}-app -n ${NAMESPACE}"
    echo "kubectl describe ingress ${APP_NAME}-ingress -n ${NAMESPACE}"
    
    echo ""
    echo "📈 Monitoring:"
    echo "=============="
    echo "kubectl port-forward svc/prometheus-service 9090:9090 -n ${NAMESPACE}"
    echo "kubectl port-forward svc/grafana-service 3000:3000 -n ${NAMESPACE}"
}

cleanup() {
    log_warning "Cleaning up resources..."
    kubectl delete -k .
    log_success "Cleanup completed"
}

# Main script
main() {
    echo "🚀 DataCompass Python - Kubernetes Deployment"
    echo "=============================================="
    echo ""
    
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            build_and_push_image
            update_image_reference
            deploy_to_kubernetes
            verify_deployment
            show_access_info
            ;;
        "cleanup")
            cleanup
            ;;
        "verify")
            verify_deployment
            ;;
        "info")
            show_access_info
            ;;
        *)
            echo "Usage: $0 {deploy|cleanup|verify|info}"
            echo ""
            echo "Commands:"
            echo "  deploy   - Build and deploy the application (default)"
            echo "  cleanup  - Remove all resources"
            echo "  verify   - Verify the deployment"
            echo "  info     - Show access information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"