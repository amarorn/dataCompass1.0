# DataCompass Python - Kubernetes Deployment Guide

This directory contains all the necessary Kubernetes manifests and scripts to deploy the DataCompass Python application on a Kubernetes cluster.

## 📋 Prerequisites

Before deploying the application, ensure you have:

1. **Kubernetes Cluster**: A running Kubernetes cluster (v1.20+)
2. **kubectl**: Kubernetes command-line tool configured to access your cluster
3. **Docker**: For building and pushing the application image
4. **Docker Registry**: Access to a container registry (Docker Hub, AWS ECR, GCR, etc.)
5. **Ingress Controller**: NGINX Ingress Controller or similar
6. **Cert-Manager**: For SSL certificate management (optional but recommended)
7. **Persistent Storage**: Storage class configured for persistent volumes

## 🏗️ Architecture Overview

The deployment includes:

- **Namespace**: `datacompass-python` - Isolated environment
- **MongoDB**: Database service with persistent storage
- **DataCompass App**: Main application with horizontal pod autoscaling
- **Ingress**: External access with SSL termination
- **Monitoring**: Prometheus and Grafana for observability
- **Security**: Network policies and RBAC

## 📁 File Structure

```
k8s/
├── namespace.yaml              # Namespace definition
├── configmap.yaml              # Application configuration
├── secret.yaml                 # Sensitive configuration (secrets)
├── mongodb-deployment.yaml     # MongoDB database deployment
├── app-deployment.yaml         # Main application deployment
├── ingress.yaml               # External access configuration
├── hpa.yaml                   # Horizontal Pod Autoscaler
├── networkpolicy.yaml         # Network security policies
├── rbac.yaml                  # Role-based access control
├── monitoring.yaml            # Monitoring configuration
├── kustomization.yaml         # Kustomize configuration
├── deploy.sh                  # Deployment script
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Configure Secrets

Before deploying, update the secrets in `secret.yaml` with your actual values:

```bash
# Encode your secrets to base64
echo -n "your_mongodb_uri" | base64
echo -n "your_whatsapp_token" | base64
echo -n "your_jwt_secret" | base64

# Update secret.yaml with the encoded values
```

### 2. Update Configuration

Edit `configmap.yaml` and `secret.yaml` with your specific configuration:

- **WhatsApp API**: Update phone number ID, access token, and webhook verify token
- **Database**: Configure MongoDB connection details
- **Domain**: Update ingress hostname to your domain
- **Registry**: Update Docker registry information in `deploy.sh`

### 3. Deploy the Application

```bash
# Make the deployment script executable
chmod +x deploy.sh

# Deploy the application
./deploy.sh deploy

# Or deploy manually
kubectl apply -k .
```

### 4. Verify Deployment

```bash
# Check if all resources are created
kubectl get all -n datacompass-python

# Check pod status
kubectl get pods -n datacompass-python

# Check logs
kubectl logs -f deployment/datacompass-python-app -n datacompass-python
```

## 🔧 Configuration Details

### Environment Variables

The application uses the following environment variables:

| Variable | Description | Source |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | Secret |
| `WHATSAPP_ACCESS_TOKEN` | WhatsApp API access token | Secret |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp phone number ID | Secret |
| `JWT_SECRET_KEY` | JWT signing key | Secret |
| `APP_NAME` | Application name | ConfigMap |
| `ENVIRONMENT` | Environment (production/development) | ConfigMap |
| `LOG_LEVEL` | Logging level | ConfigMap |

### Resource Requirements

**Application Pods:**
- CPU: 250m (request) / 500m (limit)
- Memory: 512Mi (request) / 1Gi (limit)

**MongoDB:**
- CPU: 250m (request) / 500m (limit)
- Memory: 512Mi (request) / 1Gi (limit)
- Storage: 10Gi persistent volume

### Scaling Configuration

The application is configured with:
- **Min Replicas**: 2
- **Max Replicas**: 10
- **CPU Threshold**: 70%
- **Memory Threshold**: 80%

## 🔒 Security

### Network Policies

Network policies are configured to:
- Restrict ingress traffic to necessary ports
- Allow communication between app and database
- Block unnecessary egress traffic

### RBAC

Service accounts and roles are configured for:
- Reading configuration and secrets
- Managing pod lifecycle
- Creating events

### Secrets Management

All sensitive data is stored in Kubernetes secrets:
- Base64 encoded values
- Referenced in deployments via `secretKeyRef`
- Never exposed in environment variables or logs

## 📊 Monitoring

### Prometheus Metrics

The application exposes metrics at `/metrics` endpoint:
- HTTP request metrics
- Application-specific metrics
- Custom business metrics

### Grafana Dashboard

A pre-configured dashboard includes:
- Request rate and error rate
- Response time percentiles
- Resource utilization
- Custom application metrics

### Alerting Rules

Alert rules are configured for:
- High error rate (>10%)
- High memory usage (>80%)
- High CPU usage (>80%)
- Pod crash looping

## 🌐 Accessing the Application

### External Access

The application is accessible via:
- **HTTPS**: `https://datacompass-python.yourdomain.com`
- **API Docs**: `https://datacompass-python.yourdomain.com/docs`
- **Health Check**: `https://datacompass-python.yourdomain.com/health`

### WhatsApp Webhook

Configure your WhatsApp webhook to:
```
https://datacompass-python.yourdomain.com/api/whatsapp/webhook
```

### Internal Access

For debugging or internal access:
```bash
# Port forward to access the application locally
kubectl port-forward svc/datacompass-python-service 8000:80 -n datacompass-python

# Access at http://localhost:8000
```

## 🔄 Updates and Maintenance

### Updating the Application

1. **Build new image**:
   ```bash
   docker build -t datacompass-python:v1.1.0 .
   docker push your-registry.com/datacompass-python:v1.1.0
   ```

2. **Update deployment**:
   ```bash
   kubectl set image deployment/datacompass-python-app \
     datacompass-python=your-registry.com/datacompass-python:v1.1.0 \
     -n datacompass-python
   ```

3. **Verify rollout**:
   ```bash
   kubectl rollout status deployment/datacompass-python-app -n datacompass-python
   ```

### Rolling Back

```bash
# View rollout history
kubectl rollout history deployment/datacompass-python-app -n datacompass-python

# Rollback to previous version
kubectl rollout undo deployment/datacompass-python-app -n datacompass-python
```

### Scaling

```bash
# Scale manually
kubectl scale deployment datacompass-python-app --replicas=5 -n datacompass-python

# Update HPA
kubectl patch hpa datacompass-python-hpa -n datacompass-python -p '{"spec":{"maxReplicas":15}}'
```

## 🗑️ Cleanup

To remove all resources:

```bash
# Using the deployment script
./deploy.sh cleanup

# Or manually
kubectl delete -k .
```

## 🐛 Troubleshooting

### Common Issues

1. **Pods not starting**:
   ```bash
   kubectl describe pod <pod-name> -n datacompass-python
   kubectl logs <pod-name> -n datacompass-python
   ```

2. **Database connection issues**:
   ```bash
   kubectl logs deployment/mongodb -n datacompass-python
   kubectl exec -it deployment/mongodb -n datacompass-python -- mongosh
   ```

3. **Ingress not working**:
   ```bash
   kubectl describe ingress datacompass-python-ingress -n datacompass-python
   kubectl get ingress -n datacompass-python
   ```

4. **High resource usage**:
   ```bash
   kubectl top pods -n datacompass-python
   kubectl top nodes
   ```

### Logs

```bash
# Application logs
kubectl logs -f deployment/datacompass-python-app -n datacompass-python

# MongoDB logs
kubectl logs -f deployment/mongodb -n datacompass-python

# All pods in namespace
kubectl logs -f -l app=datacompass-python -n datacompass-python
```

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Kubernetes Operator](https://www.mongodb.com/kubernetes-operator)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator)

## 🤝 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review application logs
3. Check Kubernetes events: `kubectl get events -n datacompass-python`
4. Open an issue in the project repository