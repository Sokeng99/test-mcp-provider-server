# Kubernetes Deployment Guide - Teams Bot

Complete guide for deploying the X-Pilot Teams Bot to Kubernetes (Rancher, AKS, EKS, GKE).

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [File Structure Explained](#file-structure-explained)
- [Build Docker Image](#build-docker-image)
- [Deploy to Staging](#deploy-to-staging)
- [Deploy to Production](#deploy-to-production)
- [Rancher-Specific Instructions](#rancher-specific-instructions)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring & Troubleshooting](#monitoring--troubleshooting)

## 🏗️ Architecture Overview

```
Internet
    ↓
[Azure Bot Service]
    ↓
[Ingress Controller + SSL]
    ↓
[Kubernetes Service]
    ↓
[Pods (3 replicas) with HPA]
    ↓
[Langflow API]
```

**Why This Architecture?**

- **Azure Bot Service**: Handles Teams integration, authentication, message routing
- **Ingress**: SSL termination, domain routing, load balancing
- **Service**: Stable internal networking for pods
- **Multiple Pods**: High availability, zero-downtime deployments
- **HPA**: Auto-scales based on CPU/memory load
- **Secrets**: Secure credential management

## 🔧 Prerequisites

### 1. Tools Needed

```powershell
# Check installations
docker --version
kubectl version --client
helm version  # Optional but recommended
```

Install if missing:

- **Docker Desktop**: https://www.docker.com/products/docker-desktop
- **kubectl**: `choco install kubernetes-cli` or download from https://kubernetes.io/docs/tasks/tools/
- **Helm**: `choco install kubernetes-helm` (optional)

### 2. Container Registry

You need a container registry to store your Docker images:

**Option A: Azure Container Registry (Recommended)**

```powershell
# Create ACR
az acr create --resource-group myResourceGroup --name myxpilotbotacr --sku Basic

# Login
az acr login --name myxpilotbotacr

# Get login server
az acr list --resource-group myResourceGroup --query "[].{acrLoginServer:loginServer}" --output table
```

**Option B: Docker Hub**

```powershell
docker login
```

**Option C: Private Harbor/Nexus** (if your org has one)

### 3. Kubernetes Cluster Access

Get your cluster config:

```powershell
# For AKS
az aks get-credentials --resource-group myResourceGroup --name myCluster

# For Rancher - download kubeconfig from Rancher UI

# Verify access
kubectl cluster-info
kubectl get nodes
```

### 4. Create Namespaces

```powershell
# Create namespaces
kubectl create namespace xpilot-staging
kubectl create namespace xpilot-production

# Verify
kubectl get namespaces
```

## 📁 File Structure Explained

```
your-project/
├── Dockerfile                    # How to build the container image
├── .dockerignore                # Files to exclude from image
├── deployment/
│   ├── staging/
│   │   ├── app-secret.yml       # Secrets (credentials, API keys)
│   │   ├── app-deployment.yml   # Pod configuration & replicas
│   │   ├── app-service.yml      # Internal networking
│   │   └── app-ingress.yml      # External access & SSL
│   └── production/
│       ├── app-secret.yml       # Production secrets
│       ├── app-deployment.yml   # Production pods (more replicas, HPA)
│       ├── app-service.yml      # Production service
│       └── app-ingress.yml      # Production ingress with strict security
```

**Why This Structure?**

1. **Separate Staging/Production**: Different configs, resources, secrets
2. **Secrets First**: Must be applied before deployment
3. **Service Before Ingress**: Service must exist for Ingress to route to
4. **Version Control**: Track changes, easy rollbacks

## 🐳 Build Docker Image

### Step 1: Update bot_server.py Health Endpoint

First, add a health check endpoint to your Flask app:

```python
# Add to bot_server.py
@app.route("/health", methods=["GET"])
def health_check():
    return {"status": "healthy", "service": "xpilot-bot"}, 200
```

### Step 2: Build the Image

```powershell
# Navigate to project root
cd C:\xpilot\test-mcp-provider-server

# Build for your registry
# Replace 'myxpilotbotacr' with your ACR name
docker build -t myxpilotbotacr.azurecr.io/xpilot-bot:v1.0.0 .

# Also tag as 'latest' for staging
docker tag myxpilotbotacr.azurecr.io/xpilot-bot:v1.0.0 myxpilotbotacr.azurecr.io/xpilot-bot:staging-latest
```

**Why Multi-Stage Build in Dockerfile?**

- **Smaller Images**: Only includes runtime dependencies
- **Faster Deployments**: Less data to transfer
- **More Secure**: Fewer attack vectors

**Why Non-Root User?**

- **Security Best Practice**: Limits damage if container is compromised
- **Compliance**: Many org policies require non-root containers

### Step 3: Test Locally

```powershell
# Run container locally
docker run -p 3978:3978 --env-file .env myxpilotbotacr.azurecr.io/xpilot-bot:v1.0.0

# Test health endpoint
curl http://localhost:3978/health

# Stop: Ctrl+C
```

### Step 4: Push to Registry

```powershell
# Push both tags
docker push myxpilotbotacr.azurecr.io/xpilot-bot:v1.0.0
docker push myxpilotbotacr.azurecr.io/xpilot-bot:staging-latest

# Verify
az acr repository list --name myxpilotbotacr --output table
```

### Step 5: Create Image Pull Secret

**Why?** Kubernetes needs credentials to pull images from private registry.

```powershell
# For Azure Container Registry
kubectl create secret docker-registry acr-secret \
  --namespace xpilot-staging \
  --docker-server=myxpilotbotacr.azurecr.io \
  --docker-username=myxpilotbotacr \
  --docker-password=$(az acr credential show --name myxpilotbotacr --query "passwords[0].value" -o tsv)

# Also create in production namespace
kubectl create secret docker-registry acr-secret \
  --namespace xpilot-production \
  --docker-server=myxpilotbotacr.azurecr.io \
  --docker-username=myxpilotbotacr \
  --docker-password=$(az acr credential show --name myxpilotbotacr --query "passwords[0].value" -o tsv)
```

## 🚀 Deploy to Staging

### Step 1: Update Staging Manifests

Edit `deployment/staging/app-secret.yml`:

```yaml
stringData:
  MICROSOFT_APP_ID: "your-actual-staging-app-id"
  MICROSOFT_APP_PASSWORD: "your-actual-staging-secret"
  # ... other values
```

Edit `deployment/staging/app-deployment.yml`:

```yaml
image: myxpilotbotacr.azurecr.io/xpilot-bot:staging-latest # Update registry
```

Edit `deployment/staging/app-ingress.yml`:

```yaml
host: xpilot-bot-staging.yourdomain.com # Update domain
```

### Step 2: Apply Manifests

```powershell
# Apply in order: secrets → deployment → service → ingress
kubectl apply -f deployment/staging/app-secret.yml
kubectl apply -f deployment/staging/app-deployment.yml
kubectl apply -f deployment/staging/app-service.yml
kubectl apply -f deployment/staging/app-ingress.yml
```

**Why This Order?**

1. **Secrets first**: Deployment references them
2. **Deployment**: Creates pods
3. **Service**: Provides stable endpoint for pods
4. **Ingress**: Routes external traffic to service

### Step 3: Verify Deployment

```powershell
# Check all resources
kubectl get all -n xpilot-staging

# Check pods are running
kubectl get pods -n xpilot-staging -w

# Check pod logs
kubectl logs -n xpilot-staging -l app=xpilot-bot --tail=100

# Check events for issues
kubectl get events -n xpilot-staging --sort-by='.lastTimestamp'
```

Expected output:

```
NAME                              READY   STATUS    RESTARTS   AGE
pod/xpilot-bot-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
pod/xpilot-bot-xxxxxxxxxx-xxxxx   1/1     Running   0          2m

NAME                         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)
service/xpilot-bot-service   ClusterIP   10.0.123.45     <none>        80/TCP
```

### Step 4: Get Ingress URL

```powershell
# Get ingress details
kubectl get ingress -n xpilot-staging

# Get external IP (may take a few minutes)
kubectl get ingress xpilot-bot-ingress -n xpilot-staging -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

### Step 5: Configure DNS

Point your domain to the Ingress IP:

```
A Record: xpilot-bot-staging.yourdomain.com → [Ingress IP]
```

### Step 6: Test the Deployment

```powershell
# Test health endpoint
curl https://xpilot-bot-staging.yourdomain.com/health

# Test bot endpoint
curl -X POST https://xpilot-bot-staging.yourdomain.com/api/messages \
  -H "Content-Type: application/json" \
  -d '{"test": "message"}'
```

### Step 7: Update Azure Bot Configuration

1. Go to Azure Portal → Your Bot Resource
2. Configuration → Messaging endpoint
3. Update to: `https://xpilot-bot-staging.yourdomain.com/api/messages`
4. Save

## 🏭 Deploy to Production

### Step 1: Update Production Manifests

Edit `deployment/production/app-secret.yml` with production values.

Edit `deployment/production/app-deployment.yml`:

```yaml
image: myxpilotbotacr.azurecr.io/xpilot-bot:v1.0.0 # Specific version, not :latest
```

Edit `deployment/production/app-ingress.yml`:

```yaml
host: xpilot-bot.yourdomain.com # Production domain
```

### Step 2: Apply Production Manifests

```powershell
# Apply all production resources
kubectl apply -f deployment/production/app-secret.yml
kubectl apply -f deployment/production/app-deployment.yml
kubectl apply -f deployment/production/app-service.yml
kubectl apply -f deployment/production/app-ingress.yml

# Verify
kubectl get all -n xpilot-production
kubectl logs -n xpilot-production -l app=xpilot-bot --tail=50
```

### Step 3: Monitor Rollout

```powershell
# Watch deployment progress
kubectl rollout status deployment/xpilot-bot -n xpilot-production

# Check HPA (after metrics-server is installed)
kubectl get hpa -n xpilot-production

# Check PDB
kubectl get pdb -n xpilot-production
```

## 🔄 Updates & Rollbacks

### Update Deployment

```powershell
# Build new version
docker build -t myxpilotbotacr.azurecr.io/xpilot-bot:v1.1.0 .
docker push myxpilotbotacr.azurecr.io/xpilot-bot:v1.1.0

# Update deployment image
kubectl set image deployment/xpilot-bot \
  xpilot-bot=myxpilotbotacr.azurecr.io/xpilot-bot:v1.1.0 \
  -n xpilot-production

# Or edit manifest and reapply
kubectl apply -f deployment/production/app-deployment.yml

# Watch rollout
kubectl rollout status deployment/xpilot-bot -n xpilot-production
```

### Rollback

```powershell
# View rollout history
kubectl rollout history deployment/xpilot-bot -n xpilot-production

# Rollback to previous version
kubectl rollout undo deployment/xpilot-bot -n xpilot-production

# Rollback to specific revision
kubectl rollout undo deployment/xpilot-bot -n xpilot-production --to-revision=2
```

## 📊 Monitoring

### Check Logs

```powershell
# All pods
kubectl logs -n xpilot-production -l app=xpilot-bot --tail=100 -f

# Specific pod
kubectl logs -n xpilot-production xpilot-bot-xxxxxxxxxx-xxxxx -f

# Previous container (if crashed)
kubectl logs -n xpilot-production xpilot-bot-xxxxxxxxxx-xxxxx --previous
```

### Check Resources

```powershell
# Pod resource usage
kubectl top pods -n xpilot-production

# Node resource usage
kubectl top nodes

# Describe pod for detailed info
kubectl describe pod -n xpilot-production xpilot-bot-xxxxxxxxxx-xxxxx
```

## 🔧 Troubleshooting

### Pod Won't Start

```powershell
# Check pod status
kubectl describe pod -n xpilot-staging [pod-name]

# Common issues:
# - ImagePullBackOff: Check image name and pull secret
# - CrashLoopBackOff: Check logs for application errors
# - Pending: Check resource requests, node capacity
```

### Can't Pull Image

```powershell
# Verify secret exists
kubectl get secret acr-secret -n xpilot-staging

# Recreate secret with correct credentials
kubectl delete secret acr-secret -n xpilot-staging
kubectl create secret docker-registry acr-secret ...
```

### Health Checks Failing

```powershell
# Test health endpoint from inside cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://xpilot-bot-service.xpilot-staging.svc.cluster.local/health

# Adjust probe timings in deployment.yml if needed
```

### Can't Access via Ingress

```powershell
# Check ingress status
kubectl describe ingress -n xpilot-staging

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller

# Verify DNS
nslookup xpilot-bot-staging.yourdomain.com

# Check certificate
kubectl get certificate -n xpilot-staging
```

## 🎯 Next Steps

1. **Set up monitoring**: Prometheus + Grafana
2. **Configure alerts**: Alert on pod restarts, high CPU, errors
3. **Implement CI/CD**: Automate builds and deployments
4. **Add backup**: For persistent data if needed
5. **Document runbooks**: For common operational tasks

See [RANCHER_DEPLOYMENT.md](RANCHER_DEPLOYMENT.md) for Rancher-specific instructions.
