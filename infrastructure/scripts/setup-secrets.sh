#!/bin/bash

# WhatsApp Analytics - Kubernetes Secrets Setup Script
# This script helps configure secrets for the application

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
NAMESPACE_PROD="whatsapp-analytics-prod"
NAMESPACE_STAGING="whatsapp-analytics-staging"
SECRET_NAME="whatsapp-analytics-secrets"

prompt_for_secret() {
    local var_name=$1
    local description=$2
    local is_sensitive=${3:-true}
    
    if [ "$is_sensitive" = true ]; then
        echo -n "Enter $description: "
        read -s value
        echo
    else
        echo -n "Enter $description: "
        read value
    fi
    
    echo "$value"
}

create_secret_for_namespace() {
    local namespace=$1
    
    log_info "Creating secrets for namespace: $namespace"
    
    # Prompt for all required secrets
    log_info "Please provide the following configuration values:"
    
    JWT_SECRET=$(prompt_for_secret "JWT_SECRET" "JWT Secret (strong random string)")
    WHATSAPP_TOKEN=$(prompt_for_secret "WHATSAPP_TOKEN" "WhatsApp Business API Token")
    WHATSAPP_PHONE_NUMBER_ID=$(prompt_for_secret "WHATSAPP_PHONE_NUMBER_ID" "WhatsApp Phone Number ID" false)
    WHATSAPP_WEBHOOK_VERIFY_TOKEN=$(prompt_for_secret "WHATSAPP_WEBHOOK_VERIFY_TOKEN" "WhatsApp Webhook Verify Token")
    WHATSAPP_WEBHOOK_SECRET=$(prompt_for_secret "WHATSAPP_WEBHOOK_SECRET" "WhatsApp Webhook Secret")
    DATABASE_URL=$(prompt_for_secret "DATABASE_URL" "Database URL (PostgreSQL connection string)")
    
    # Create the secret
    kubectl create secret generic "$SECRET_NAME" \
        --namespace="$namespace" \
        --from-literal=jwt-secret="$JWT_SECRET" \
        --from-literal=whatsapp-token="$WHATSAPP_TOKEN" \
        --from-literal=whatsapp-phone-number-id="$WHATSAPP_PHONE_NUMBER_ID" \
        --from-literal=whatsapp-webhook-verify-token="$WHATSAPP_WEBHOOK_VERIFY_TOKEN" \
        --from-literal=whatsapp-webhook-secret="$WHATSAPP_WEBHOOK_SECRET" \
        --from-literal=database-url="$DATABASE_URL" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Secrets created for namespace: $namespace"
}

create_secret_from_env() {
    local namespace=$1
    local env_file=${2:-.env}
    
    if [ ! -f "$env_file" ]; then
        log_error "Environment file $env_file not found"
        return 1
    fi
    
    log_info "Creating secrets from $env_file for namespace: $namespace"
    
    # Read environment file and create secret
    kubectl create secret generic "$SECRET_NAME" \
        --namespace="$namespace" \
        --from-env-file="$env_file" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Secrets created from $env_file for namespace: $namespace"
}

update_secret() {
    local namespace=$1
    local key=$2
    local value=$3
    
    log_info "Updating secret key '$key' in namespace: $namespace"
    
    # Update specific key in the secret
    kubectl patch secret "$SECRET_NAME" \
        --namespace="$namespace" \
        --type='merge' \
        -p="{\"data\":{\"$key\":\"$(echo -n "$value" | base64 -w 0)\"}}"
    
    log_success "Secret key '$key' updated in namespace: $namespace"
}

list_secrets() {
    local namespace=$1
    
    log_info "Listing secrets in namespace: $namespace"
    
    if kubectl get secret "$SECRET_NAME" --namespace="$namespace" &> /dev/null; then
        echo "Secret '$SECRET_NAME' exists in namespace '$namespace'"
        echo "Keys:"
        kubectl get secret "$SECRET_NAME" --namespace="$namespace" -o jsonpath='{.data}' | jq -r 'keys[]' 2>/dev/null || {
            kubectl get secret "$SECRET_NAME" --namespace="$namespace" -o yaml | grep -A 20 "data:" | grep "  " | cut -d: -f1 | sed 's/^  //'
        }
    else
        log_warning "Secret '$SECRET_NAME' does not exist in namespace '$namespace'"
    fi
}

delete_secret() {
    local namespace=$1
    
    log_warning "Deleting secret '$SECRET_NAME' from namespace: $namespace"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete secret "$SECRET_NAME" --namespace="$namespace" || {
            log_warning "Secret does not exist or already deleted"
        }
        log_success "Secret deleted from namespace: $namespace"
    else
        log_info "Deletion cancelled"
    fi
}

generate_github_secrets() {
    log_info "Generating GitHub Secrets configuration..."
    
    echo "Add the following secrets to your GitHub repository:"
    echo "Repository Settings > Secrets and variables > Actions > New repository secret"
    echo
    echo "Required secrets:"
    echo "- AWS_ACCESS_KEY_ID: Your AWS access key ID"
    echo "- AWS_SECRET_ACCESS_KEY: Your AWS secret access key"
    echo "- SLACK_WEBHOOK_URL: (Optional) Slack webhook for notifications"
    echo
    echo "Make sure your AWS user has the following permissions:"
    echo "- EKS cluster access"
    echo "- ECR push/pull permissions"
    echo "- S3 access for Terraform state"
    echo "- DynamoDB access for Terraform locking"
}

show_help() {
    echo "WhatsApp Analytics - Kubernetes Secrets Setup"
    echo
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    echo "Commands:"
    echo "  create-prod              Create secrets for production namespace"
    echo "  create-staging           Create secrets for staging namespace"
    echo "  create-from-env [FILE]   Create secrets from environment file"
    echo "  update KEY VALUE         Update a specific secret key"
    echo "  list [NAMESPACE]         List secrets in namespace"
    echo "  delete [NAMESPACE]       Delete secrets from namespace"
    echo "  github-secrets           Show GitHub secrets configuration"
    echo "  help                     Show this help message"
    echo
    echo "Examples:"
    echo "  $0 create-prod"
    echo "  $0 create-from-env .env.production"
    echo "  $0 update whatsapp-token 'new-token-value'"
    echo "  $0 list whatsapp-analytics-prod"
}

main() {
    case "${1:-help}" in
        "create-prod")
            create_secret_for_namespace "$NAMESPACE_PROD"
            ;;
        "create-staging")
            create_secret_for_namespace "$NAMESPACE_STAGING"
            ;;
        "create-from-env")
            namespace="${3:-$NAMESPACE_PROD}"
            create_secret_from_env "$namespace" "$2"
            ;;
        "update")
            if [ $# -lt 3 ]; then
                log_error "Usage: $0 update KEY VALUE [NAMESPACE]"
                exit 1
            fi
            namespace="${4:-$NAMESPACE_PROD}"
            update_secret "$namespace" "$2" "$3"
            ;;
        "list")
            namespace="${2:-$NAMESPACE_PROD}"
            list_secrets "$namespace"
            ;;
        "delete")
            namespace="${2:-$NAMESPACE_PROD}"
            delete_secret "$namespace"
            ;;
        "github-secrets")
            generate_github_secrets
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    log_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Run main function
main "$@"

