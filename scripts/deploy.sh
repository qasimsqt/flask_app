#!/bin/bash

# Deployment script for Mini Shop on Kubernetes
set -e

echo "🚀 Deploying Mini Shop to Kubernetes..."

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

# Check if we're connected to a cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Not connected to a Kubernetes cluster"
    exit 1
fi

echo "📋 Current cluster info:"
kubectl cluster-info

# Apply Kubernetes manifests in order
echo "📦 Creating namespace..."
kubectl apply -f k8s/namespace.yaml

echo "⚙️  Applying ConfigMap..."
kubectl apply -f k8s/configmap.yaml

echo "🔐 Applying Secrets..."
kubectl apply -f k8s/secret.yaml

echo "🚀 Deploying application..."
kubectl apply -f k8s/deployment.yaml

echo "🌐 Creating services..."
kubectl apply -f k8s/service.yaml

echo "🔄 Setting up auto-scaling..."
kubectl apply -f k8s/hpa.yaml

# Optional: Apply ingress if requested
if [ "$1" = "--with-ingress" ]; then
    echo "🌍 Setting up ingress..."
    kubectl apply -f k8s/ingress.yaml
fi

echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/mini-shop-deployment -n mini-shop

echo "✅ Deployment completed successfully!"

# Show status
echo "📊 Deployment status:"
kubectl get pods -n mini-shop
kubectl get services -n mini-shop

# Get service URL
SERVICE_IP=$(kubectl get service mini-shop-service -n mini-shop -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
if [ "$SERVICE_IP" != "pending" ] && [ ! -z "$SERVICE_IP" ]; then
    echo "🌐 Application URL: http://$SERVICE_IP"
    echo "📊 AI Monitor URL: http://$SERVICE_IP:9000"
else
    echo "🔄 LoadBalancer IP is pending. Use 'kubectl get services -n mini-shop' to check status."
    echo "💡 For local testing, use: kubectl port-forward service/mini-shop-service 8080:80 -n mini-shop"
fi

echo "🎉 Mini Shop is now running on Kubernetes!"
