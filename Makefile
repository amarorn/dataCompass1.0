# WhatsApp Analytics API - Makefile
# Automation commands for development and deployment

.PHONY: help install build test docker-build docker-run k8s-deploy k8s-delete terraform-init terraform-plan terraform-apply terraform-destroy

# Default target
help:
	@echo "WhatsApp Analytics API - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install          Install dependencies"
	@echo "  build            Build TypeScript application"
	@echo "  dev              Run development server"
	@echo "  test             Run tests"
	@echo "  lint             Run linting"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build     Build Docker image"
	@echo "  docker-run       Run Docker container locally"
	@echo "  docker-push      Push image to ECR"
	@echo ""
	@echo "Kubernetes:"
	@echo "  k8s-deploy       Deploy to Kubernetes"
	@echo "  k8s-delete       Delete from Kubernetes"
	@echo "  k8s-logs         Show application logs"
	@echo "  k8s-status       Show deployment status"
	@echo ""
	@echo "Infrastructure:"
	@echo "  terraform-init   Initialize Terraform"
	@echo "  terraform-plan   Plan infrastructure changes"
	@echo "  terraform-apply  Apply infrastructure changes"
	@echo "  terraform-destroy Destroy infrastructure"
	@echo ""
	@echo "Setup:"
	@echo "  setup-cluster    Setup EKS cluster"
	@echo "  setup-secrets    Setup Kubernetes secrets"

# Development commands
install:
	npm ci

build:
	npm run build

dev:
	npm run dev

test:
	npm test

lint:
	npx eslint src/ --ext .ts || echo "ESLint not configured"

# Docker commands
docker-build:
	docker build -t whatsapp-analytics-api:latest .

docker-run:
	docker run -p 3000:3000 --env-file .env whatsapp-analytics-api:latest

docker-push:
	@echo "Pushing to ECR..."
	@aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $$(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com
	@docker tag whatsapp-analytics-api:latest $$(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/whatsapp-analytics-api:latest
	@docker push $$(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/whatsapp-analytics-api:latest

# Kubernetes commands
k8s-deploy:
	cd k8s/overlays/production && kustomize build . | kubectl apply -f -

k8s-delete:
	cd k8s/overlays/production && kustomize build . | kubectl delete -f -

k8s-logs:
	kubectl logs -f deployment/whatsapp-analytics-api -n whatsapp-analytics-prod

k8s-status:
	@echo "=== Pods ==="
	kubectl get pods -n whatsapp-analytics-prod
	@echo ""
	@echo "=== Services ==="
	kubectl get services -n whatsapp-analytics-prod
	@echo ""
	@echo "=== Ingress ==="
	kubectl get ingress -n whatsapp-analytics-prod
	@echo ""
	@echo "=== HPA ==="
	kubectl get hpa -n whatsapp-analytics-prod

# Infrastructure commands
terraform-init:
	cd infrastructure/terraform && terraform init

terraform-plan:
	cd infrastructure/terraform && terraform plan

terraform-apply:
	cd infrastructure/terraform && terraform apply

terraform-destroy:
	cd infrastructure/terraform && terraform destroy

# Setup commands
setup-cluster:
	./infrastructure/scripts/setup-cluster.sh

setup-secrets:
	./infrastructure/scripts/setup-secrets.sh create-prod

# Utility commands
clean:
	rm -rf node_modules dist

format:
	npx prettier --write src/

check-deps:
	npm audit

update-deps:
	npm update

# Environment setup
setup-dev:
	cp .env.example .env
	@echo "Please edit .env file with your configuration"

# Health checks
health-check:
	@curl -f http://localhost:3000/health || echo "Application not running"

# Complete setup for new environment
setup-all: install build docker-build setup-cluster setup-secrets k8s-deploy
	@echo "Complete setup finished!"

