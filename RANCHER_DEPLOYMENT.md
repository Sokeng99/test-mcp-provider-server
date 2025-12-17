# Rancher Deployment Guide - Teams Bot

Step-by-step guide for deploying X-Pilot Teams Bot to Rancher (your organization's Kubernetes platform).

## 📋 What is Rancher?

Rancher is a complete container management platform that makes it easy to deploy and manage Kubernetes clusters. Your organization likely uses Rancher to:

- Manage multiple Kubernetes clusters
- Provide UI-based deployment (no kubectl needed)
- Control access and permissions
- Monitor resources and applications

## 🎯 Prerequisites

### 1. Get Rancher Access

Contact your DevOps/Platform team to:

- [ ] Get Rancher account/login
- [ ] Request access to appropriate cluster (staging/production)
- [ ] Get permissions for creating namespaces and deployments
- [ ] Obtain container registry credentials (if using private registry)

**Rancher URL**: Usually something like `https://rancher.yourcompany.com`

### 2. Prepare Your Container Image

You need to build and push your Docker image first (see [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md)).

```powershell
# Build image
docker build -t your-registry.com/xpilot-bot:v1.0.0 .

# Push to your org's registry
docker push your-registry.com/xpilot-bot:v1.0.0
```

**Registry Options:**

- Your org's private Harbor/Nexus registry
- Azure Container Registry (if org uses Azure)
- AWS ECR (if org uses AWS)

## 🚀 Deployment Methods in Rancher

Rancher offers **3 ways** to deploy applications. Choose based on your preference:

### Method 1: Rancher UI (Easiest - Recommended for Beginners)

- Click-through interface
- No YAML knowledge needed
- Good for learning

### Method 2: Import YAML (Balanced)

- Use the YAML files we created
- Quick and reproducible
- Best for this project

### Method 3: kubectl (Advanced)

- Command-line access
- Full control
- Best for automation

We'll cover all three methods below.

---

## 🖱️ Method 1: Deploy Using Rancher UI

### Step 1: Login to Rancher

1. Navigate to your org's Rancher URL
2. Login with your credentials (usually SSO/LDAP)
3. You'll see a list of clusters

### Step 2: Select Cluster

1. Click on your **staging cluster** (e.g., "staging-k8s", "dev-cluster")
2. This opens the cluster dashboard

### Step 3: Create Namespace

**Why?** Namespaces isolate your app from others.

1. Click **"Cluster"** in left menu
2. Click **"Projects/Namespaces"**
3. Click **"Create Namespace"**
4. Enter:
   - **Name**: `xpilot-staging`
   - **Project**: Select appropriate project or "Default"
5. Click **"Create"**

### Step 4: Create Registry Secret

**Why?** Allows Kubernetes to pull your private container images.

1. Navigate to **Storage → Secrets**
2. Click **"Add Secret"**
3. Select namespace: `xpilot-staging`
4. Choose type: **"Registry Credentials"**
5. Fill in:
   - **Name**: `acr-secret`
   - **Registry Domain**: `your-registry.azurecr.io`
   - **Username**: Your registry username
   - **Password**: Your registry password
6. Click **"Save"**

### Step 5: Create Application Secrets

**Why?** Store sensitive credentials (API keys, passwords).

1. Navigate to **Storage → Secrets**
2. Click **"Add Secret"**
3. Select namespace: `xpilot-staging`
4. Choose type: **"Opaque"**
5. Fill in:
   - **Name**: `xpilot-bot-secret`
   - Click **"Add Key-Value"** for each:
     ```
     MICROSOFT_APP_ID: your-app-id
     MICROSOFT_APP_PASSWORD: your-secret
     MICROSOFT_APP_TENANT_ID: your-tenant-id
     LANGFLOW_URL: https://your-langflow.com
     LANGFLOW_API_KEY: your-api-key
     LANGFLOW_CHAT_FLOW_ID: your-flow-id
     LANGFLOW_REQUIREMENT_FLOW_ID: your-requirement-flow-id
     ```
6. Click **"Save"**

### Step 6: Create ConfigMap

**Why?** Store non-sensitive configuration.

1. Navigate to **Storage → ConfigMaps**
2. Click **"Add ConfigMap"**
3. Select namespace: `xpilot-staging`
4. Fill in:
   - **Name**: `xpilot-bot-config`
   - Add keys:
     ```
     FLASK_ENV: staging
     LOG_LEVEL: DEBUG
     PORT: 3978
     ```
5. Click **"Save"**

### Step 7: Deploy Workload

**Why?** Creates your application pods.

1. Navigate to **Workloads → Deployments**
2. Click **"Create"**
3. Select namespace: `xpilot-staging`

**Basic Settings:**

- **Name**: `xpilot-bot`
- **Replicas**: `2`

**Container Image:**

- **Container Image**: `your-registry.com/xpilot-bot:v1.0.0`
- **Pull Policy**: `Always` (for staging)
- **Image Pull Secret**: Select `acr-secret`

**Environment Variables:**

- Click **"Add from Source"** → Select `xpilot-bot-secret` (select all keys)
- Click **"Add from Source"** → Select `xpilot-bot-config` (select all keys)

**Ports:**

- Click **"Add Port"**
  - **Port Name**: `http`
  - **Container Port**: `3978`
  - **Protocol**: `TCP`

**Health Check:**

- **Liveness Check**:
  - Type: `HTTP`
  - Path: `/health`
  - Port: `3978`
  - Initial Delay: `30` seconds
  - Period: `10` seconds
- **Readiness Check**:
  - Type: `HTTP`
  - Path: `/health`
  - Port: `3978`
  - Initial Delay: `10` seconds
  - Period: `5` seconds

**Resources (Optional but Recommended):**

- **CPU Reservation**: `100m`
- **CPU Limit**: `500m`
- **Memory Reservation**: `128Mi`
- **Memory Limit**: `512Mi`

4. Click **"Launch"**

### Step 8: Create Service

**Why?** Provides stable networking to reach pods.

1. Navigate to **Service Discovery → Services**
2. Click **"Create"**
3. Select namespace: `xpilot-staging`
4. Fill in:
   - **Name**: `xpilot-bot-service`
   - **Targets workload**: Select `xpilot-bot`
   - **Port Mapping**:
     - Service Port: `80`
     - Target Port: `3978`
     - Protocol: `TCP`
   - **Type**: `ClusterIP`
5. Click **"Create"**

### Step 9: Create Ingress

**Why?** Exposes your service to the internet with HTTPS.

1. Navigate to **Service Discovery → Ingresses**
2. Click **"Create"**
3. Select namespace: `xpilot-staging`
4. Fill in:
   - **Name**: `xpilot-bot-ingress`
   - **Request Host**: `xpilot-bot-staging.yourdomain.com`
   - **Path**: `/`
   - **Target Service**: `xpilot-bot-service`
   - **Port**: `80`
   - **TLS Certificate**:
     - Select existing or create new Let's Encrypt certificate
5. Click **"Create"**

### Step 10: Verify Deployment

1. Go to **Workloads → Deployments**
2. Find `xpilot-bot` - should show `2/2` (2 pods ready)
3. Click on deployment name
4. Click **"View Logs"** to check application logs
5. Test: `curl https://xpilot-bot-staging.yourdomain.com/health`

---

## 📄 Method 2: Deploy Using YAML Files (Recommended)

This is **faster and reproducible** - you can reuse for other projects!

### Step 1: Access Rancher Kubectl Shell

1. Login to Rancher
2. Select your cluster
3. Click **"Kubectl Shell"** button (top right, terminal icon)
4. A web-based terminal opens with kubectl configured

### Step 2: Upload YAML Files

**Option A: Copy-Paste in Rancher**

1. Click **"Import YAML"** button (top right)
2. Copy content from `deployment/staging/app-secret.yml`
3. Paste into Rancher's YAML editor
4. Update values (app ID, passwords, etc.)
5. Click **"Import"**
6. Repeat for other files:
   - `app-deployment.yml`
   - `app-service.yml`
   - `app-ingress.yml`

**Option B: Use kubectl Shell**

```bash
# In Rancher kubectl shell, create files
cat > app-secret.yml << 'EOF'
# Paste content here
EOF

cat > app-deployment.yml << 'EOF'
# Paste content here
EOF

cat > app-service.yml << 'EOF'
# Paste content here
EOF

cat > app-ingress.yml << 'EOF'
# Paste content here
EOF

# Apply all files
kubectl apply -f app-secret.yml
kubectl apply -f app-deployment.yml
kubectl apply -f app-service.yml
kubectl apply -f app-ingress.yml
```

### Step 3: Verify

```bash
# Check all resources
kubectl get all -n xpilot-staging

# Check pods
kubectl get pods -n xpilot-staging

# View logs
kubectl logs -n xpilot-staging -l app=xpilot-bot
```

---

## 💻 Method 3: Deploy Using Local kubectl

### Step 1: Download Kubeconfig from Rancher

1. Login to Rancher
2. Select your cluster
3. Click **cluster name** dropdown (top right)
4. Click **"Download KubeConfig"**
5. Save file (e.g., `rancher-kubeconfig.yaml`)

### Step 2: Set KUBECONFIG Environment Variable

**PowerShell:**

```powershell
# Set for current session
$env:KUBECONFIG = "C:\path\to\rancher-kubeconfig.yaml"

# Or set permanently
[Environment]::SetEnvironmentVariable("KUBECONFIG", "C:\path\to\rancher-kubeconfig.yaml", "User")
```

**Alternative: Merge with existing config**

```powershell
# Backup existing config
cp ~/.kube/config ~/.kube/config.backup

# Set KUBECONFIG to use downloaded file
$env:KUBECONFIG = "$HOME\.kube\config;C:\path\to\rancher-kubeconfig.yaml"

# View merged contexts
kubectl config get-contexts

# Switch to Rancher cluster
kubectl config use-context rancher-cluster-name
```

### Step 3: Verify Connection

```powershell
# Test connection
kubectl cluster-info

# View nodes
kubectl get nodes

# Should see your org's cluster nodes
```

### Step 4: Apply YAML Files

```powershell
# Navigate to project
cd C:\xpilot\test-mcp-provider-server

# Update YAML files with actual values (app IDs, domains, registry)

# Apply in order
kubectl apply -f deployment/staging/app-secret.yml
kubectl apply -f deployment/staging/app-deployment.yml
kubectl apply -f deployment/staging/app-service.yml
kubectl apply -f deployment/staging/app-ingress.yml

# Verify
kubectl get all -n xpilot-staging
```

---

## 🔐 Common Rancher-Specific Configurations

### 1. Using Org's Certificate Manager

If your org has cert-manager:

```yaml
# In app-ingress.yml
annotations:
  cert-manager.io/cluster-issuer: "your-org-issuer" # Ask DevOps team
```

### 2. Using Org's Image Registry

Update all deployment files:

```yaml
# In app-deployment.yml
image: harbor.yourcompany.com/xpilot/xpilot-bot:v1.0.0
imagePullSecrets:
  - name: harbor-secret # Your org's registry secret
```

### 3. Network Policies

Some orgs require network policies:

```powershell
# Ask if required, apply if needed
kubectl apply -f deployment/staging/app-network-policy.yml
```

### 4. Resource Quotas

Check namespace quotas:

```powershell
kubectl describe quota -n xpilot-staging
```

If you hit limits, adjust your deployment resources or request quota increase.

### 5. Pod Security Policies

Some orgs enforce PSP/PSA. Update deployment:

```yaml
# In app-deployment.yml
spec:
  template:
    metadata:
      annotations:
        # If required by org
        container.apparmor.security.beta.kubernetes.io/xpilot-bot: runtime/default
```

---

## 🎓 Learning Resources in Rancher

### Explore Your Deployment

1. **Workload Dashboard**: See CPU/memory usage graphs
2. **Logs**: Real-time streaming logs for debugging
3. **Shell**: Execute commands inside running containers
4. **Events**: See what happened (pod starts, image pulls, errors)
5. **Monitoring**: Prometheus metrics if enabled

### Rancher Features to Learn

- **Projects**: Group namespaces together
- **Catalogs**: Pre-built application templates
- **Pipelines**: CI/CD integration
- **Alerts**: Set up notifications for issues
- **Monitoring**: Grafana dashboards

---

## 🚨 Troubleshooting in Rancher

### Can't See Cluster

**Cause**: Insufficient permissions

**Solution**: Contact DevOps team for access

### Image Pull Errors

**Cause**: Registry secret missing or incorrect

**Solution**:

1. Go to **Secrets** → Find `acr-secret`
2. Verify credentials are correct
3. Test: `kubectl get pods -n xpilot-staging` and check events

### Pods in CrashLoopBackOff

**Cause**: Application error

**Solution**:

1. Go to **Workloads** → Click pod
2. Click **"View Logs"**
3. Look for Python errors
4. Common issues:
   - Missing environment variables
   - Wrong Langflow URL
   - Port mismatch

### Can't Access via Ingress

**Cause**: DNS not configured or cert issue

**Solution**:

1. Check **Ingresses** → View status
2. Verify DNS: `nslookup xpilot-bot-staging.yourdomain.com`
3. Check certificate: Look for TLS secret in namespace
4. Ask DevOps team about ingress controller setup

### ResourceQuota Exceeded

**Cause**: Namespace limits reached

**Solution**:

1. Check quota: **Cluster → Projects/Namespaces** → View quota
2. Reduce resource requests in deployment
3. Or request quota increase from DevOps

---

## ✅ Post-Deployment Checklist

After successful deployment:

- [ ] Pods are running (green in Rancher)
- [ ] Logs show no errors
- [ ] Health endpoint accessible: `curl https://your-domain/health`
- [ ] Azure Bot messaging endpoint updated
- [ ] Bot responds in Teams
- [ ] SSL certificate valid (HTTPS padlock in browser)
- [ ] Set up monitoring alerts (if available)
- [ ] Document your specific org's requirements

---

## 🔄 Common Operations in Rancher

### Update Application (New Version)

1. Build new image: `docker build -t registry/xpilot-bot:v1.1.0 .`
2. Push: `docker push registry/xpilot-bot:v1.1.0`
3. In Rancher:
   - Go to **Workloads** → Click `xpilot-bot`
   - Click **⋮ → Edit Config**
   - Update **Container Image** to `v1.1.0`
   - Click **Save**
4. Rancher will rolling update automatically

### Scale Application

1. Go to **Workloads** → Click `xpilot-bot`
2. Click **⋮ → Edit Config**
3. Change **Scale** from `2` to `3` (or desired number)
4. Click **Save**

### View Logs

1. Go to **Workloads** → Click `xpilot-bot`
2. Click on any pod
3. Click **"View Logs"** tab
4. Real-time log streaming appears

### Restart Pods

1. Go to **Workloads** → Click `xpilot-bot`
2. Click **⋮ → Redeploy**
3. Pods will restart with rolling update

### Rollback

1. Go to **Workloads** → Click `xpilot-bot`
2. Click **⋮ → Rollback**
3. Select previous revision
4. Click **Rollback**

---

## 🎯 Production Deployment in Rancher

Use the same process, but:

1. **Use production namespace**: `xpilot-production`
2. **Use production manifests**: `deployment/production/*.yml`
3. **Use specific version tags**: Not `:latest`
4. **Set higher replicas**: At least 3 pods
5. **Apply stricter resources**: Set proper limits/requests
6. **Enable autoscaling**: HPA in production manifests
7. **Set up monitoring**: Alerts for errors, high CPU, restarts

---

## 📚 Additional Resources

- **Your Org's Wiki**: Check for internal Rancher docs
- **DevOps Team**: Slack/Teams channel for help
- **Rancher Docs**: https://rancher.com/docs/
- **Kubernetes Basics**: https://kubernetes.io/docs/tutorials/

---

## 🤝 Working With Your Organization

### Before You Start

- [ ] Attend your org's Kubernetes onboarding (if available)
- [ ] Join DevOps/Platform Slack/Teams channel
- [ ] Read internal documentation
- [ ] Understand approval process for production deployments

### During Development

- [ ] Use staging environment first
- [ ] Follow org's naming conventions
- [ ] Tag resources with required labels (team, cost-center, etc.)
- [ ] Stay within resource quotas

### Before Production

- [ ] Get code review/approval
- [ ] Complete security scan (if required)
- [ ] Document runbook for on-call
- [ ] Test failover scenarios
- [ ] Schedule deployment window (if needed)

---

## 💡 Pro Tips

1. **Save your commands**: Keep a notebook of kubectl/docker commands you use
2. **Learn kubectl**: Even if using Rancher UI, kubectl is valuable
3. **Understand YAML**: Makes debugging much easier
4. **Monitor costs**: Kubernetes resources cost money
5. **Use labels**: Makes finding your resources easier
6. **Document everything**: Future you will thank you

---

## 🎉 Success!

You now know how to deploy to Kubernetes via Rancher! This knowledge applies to **any containerized application**, not just this bot.

**Next project?** Just:

1. Create Dockerfile
2. Copy deployment YAML structure
3. Update configs
4. Deploy!

Good luck! 🚀
