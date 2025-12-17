# Simple Kubernetes Deployment Guide

Quick and easy guide for deploying your Teams Bot to Kubernetes/Rancher.

## 📁 Project Structure

```
your-project/
├── Dockerfile
├── deployment/
│   ├── staging/
│   │   ├── app-secret.yml        # Your credentials
│   │   ├── app-deployment.yml    # Your app pods
│   │   └── app-service.yml       # Internal networking
│   └── production/
│       ├── app-secret.yml
│       ├── app-deployment.yml
│       └── app-service.yml
```

## 🚀 Quick Start

### Step 1: Build Docker Image

```powershell
cd C:\xpilot\test-mcp-provider-server

# Build image
docker build -t registry.smart.com.kh/spa/xpilot-bot:v1.0.0 .

# Login to registry
docker login registry.smart.com.kh

# Push image
docker push registry.smart.com.kh/spa/xpilot-bot:v1.0.1
```

### Step 2: Update Kubernetes Files

**Edit `deployment/staging/app-secret.yml`:**

Replace these values with your actual credentials:

```yaml
stringData:
  MICROSOFT_APP_ID: "your-actual-app-id"
  MICROSOFT_APP_PASSWORD: "your-actual-secret"
  MICROSOFT_APP_TENANT_ID: "your-tenant-id"
  LANGFLOW_URL: "https://your-langflow-url.com"
  LANGFLOW_API_KEY: "your-langflow-api-key"
  LANGFLOW_CHAT_FLOW_ID: "your-flow-id"
  LANGFLOW_REQUIREMENT_FLOW_ID: "your-requirement-flow-id"
```

**Edit `deployment/staging/app-deployment.yml`:**

Update the image line:

```yaml
image: registry.smart.com.kh/spa/xpilot-bot:v1.0.1 # Your actual registry
```

### Step 3: Deploy to Rancher

**Option A: Using Rancher UI**

1. Login to Rancher
2. Select your cluster
3. Click "Import YAML" button
4. Copy-paste contents of:
   - `app-secret.yml`
   - `app-deployment.yml`
   - `app-service.yml`
5. Click "Import"

**Option B: Using kubectl**

```powershell
# Apply files
kubectl apply -f deployment/staging/app-secret.yml
kubectl apply -f deployment/staging/app-deployment.yml
kubectl apply -f deployment/staging/app-service.yml

# Check status
kubectl get pods -n xpilot-staging

# View logs
kubectl logs -n xpilot-staging -l app=xpilot-bot-staging
```

### Step 4: Expose Your Service

Ask your DevOps team to:

1. Create an Ingress route pointing to `xpilot-bot-staging-svc`
2. Or provide you with the internal service URL
3. Update Azure Bot messaging endpoint with that URL

## 📝 What Each File Does

### **app-secret.yml**

Stores your passwords and API keys securely.

### **app-deployment.yml**

Creates 2 copies (pods) of your bot application.

Key settings:

- `replicas: 2` - Number of copies running
- `image:` - Your Docker image location
- `resources:` - CPU and memory limits
- `envFrom:` - Loads all secrets as environment variables

### **app-service.yml**

Creates a stable internal address for your app.

- Pods can restart/move, but service stays at same address
- Maps port 80 to your app's port 3978

## 🔧 Common Tasks

### Update Your Bot

```powershell
# 1. Build new version
docker build -t registry.smart.com.kh/spa/xpilot-bot:v1.1.0 .
docker push registry.smart.com.kh/spa/xpilot-bot:v1.1.0

# 2. Update deployment
kubectl set image deployment/xpilot-bot-staging \
  xpilot-bot-staging=registry.smart.com.kh/spa/xpilot-bot:v1.1.0 \
  -n xpilot-staging

# 3. Watch rollout
kubectl rollout status deployment/xpilot-bot-staging -n xpilot-staging
```

### View Logs

```powershell
# All pods
kubectl logs -n xpilot-staging -l app=xpilot-bot-staging --tail=50

# Specific pod
kubectl logs -n xpilot-staging xpilot-bot-staging-xxxxx-xxxxx

# Follow logs
kubectl logs -n xpilot-staging -l app=xpilot-bot-staging -f
```

### Check Status

```powershell
# View all resources
kubectl get all -n xpilot-staging

# View pods
kubectl get pods -n xpilot-staging

# Describe pod (detailed info)
kubectl describe pod -n xpilot-staging xpilot-bot-staging-xxxxx-xxxxx
```

### Restart Pods

```powershell
kubectl rollout restart deployment/xpilot-bot-staging -n xpilot-staging
```

## 🐛 Troubleshooting

### Pods Won't Start

```powershell
# Check pod status
kubectl get pods -n xpilot-staging

# Common statuses:
# - ImagePullBackOff: Wrong image name or missing imagePullSecret
# - CrashLoopBackOff: App is crashing, check logs
# - Pending: Not enough resources or other scheduling issues

# View detailed error
kubectl describe pod -n xpilot-staging xpilot-bot-staging-xxxxx-xxxxx
```

### Can't Pull Image

```powershell
# Create registry secret (ask DevOps for credentials)
kubectl create secret docker-registry registry-secret \
  --docker-server=registry.smart.com.kh \
  --docker-username=your-username \
  --docker-password=your-password \
  --namespace=xpilot-staging
```

### Check Environment Variables

```powershell
# See what environment variables the pod has
kubectl exec -n xpilot-staging xpilot-bot-staging-xxxxx-xxxxx -- env
```

## 📊 File Comparison: Staging vs Production

| Setting       | Staging          | Production                 |
| ------------- | ---------------- | -------------------------- |
| **Namespace** | xpilot-staging   | xpilot-production          |
| **Replicas**  | 2                | 3                          |
| **Image Tag** | :staging-latest  | :v1.0.0 (specific version) |
| **CPU**       | 100m-500m        | 250m-1000m                 |
| **Memory**    | 128Mi-512Mi      | 256Mi-1Gi                  |
| **Secrets**   | Test credentials | Production credentials     |

## ✅ Deployment Checklist

- [ ] Docker image built and pushed to registry
- [ ] `app-secret.yml` updated with real credentials
- [ ] `app-deployment.yml` image updated to your registry
- [ ] Registry pull secret created (`acr-secret`)
- [ ] Files applied to Kubernetes
- [ ] Pods are running (check with `kubectl get pods`)
- [ ] Logs show no errors
- [ ] Service created and accessible internally
- [ ] Ingress/external access configured (ask DevOps)
- [ ] Azure Bot messaging endpoint updated

## 🎯 Next Steps

1. **Test in staging first**
2. **Once working, deploy to production** (use production files)
3. **Set up CI/CD** (optional, see CI_CD_PIPELINE.md)
4. **Monitor your application** (logs, resource usage)

## 🆘 Getting Help

- **Rancher issues**: Ask your DevOps/Platform team
- **Application errors**: Check pod logs
- **Kubernetes questions**: See DEPLOYMENT_EXPLAINED.md
- **CI/CD setup**: See CI_CD_PIPELINE.md

Good luck! 🚀
