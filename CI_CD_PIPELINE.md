# CI/CD Pipeline Example

Automate your Docker builds and Kubernetes deployments.

## GitHub Actions Pipeline

Create `.github/workflows/deploy.yml`:

```yaml
name: Build and Deploy

on:
  push:
    branches:
      - main # Deploy to staging on main branch
      - production # Deploy to production on production branch
    tags:
      - "v*" # Deploy to production on version tags

env:
  REGISTRY: myxpilotbotacr.azurecr.io
  IMAGE_NAME: xpilot-bot

jobs:
  build:
    name: Build Docker Image
    runs-on: ubuntu-latest

    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix={{branch}}-

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:buildcache,mode=max

  deploy-staging:
    name: Deploy to Staging
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3

      - name: Configure Kubernetes
        run: |
          echo "${{ secrets.KUBE_CONFIG_STAGING }}" | base64 -d > kubeconfig
          echo "KUBECONFIG=$PWD/kubeconfig" >> $GITHUB_ENV

      - name: Update deployment image
        run: |
          kubectl set image deployment/xpilot-bot \
            xpilot-bot=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:main \
            -n xpilot-staging

      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/xpilot-bot -n xpilot-staging --timeout=5m

      - name: Verify deployment
        run: |
          kubectl get pods -n xpilot-staging -l app=xpilot-bot

  deploy-production:
    name: Deploy to Production
    needs: build
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    environment: production # Requires manual approval

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3

      - name: Configure Kubernetes
        run: |
          echo "${{ secrets.KUBE_CONFIG_PRODUCTION }}" | base64 -d > kubeconfig
          echo "KUBECONFIG=$PWD/kubeconfig" >> $GITHUB_ENV

      - name: Update deployment image
        run: |
          kubectl set image deployment/xpilot-bot \
            xpilot-bot=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.ref_name }} \
            -n xpilot-production

      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/xpilot-bot -n xpilot-production --timeout=10m

      - name: Verify deployment
        run: |
          kubectl get pods -n xpilot-production -l app=xpilot-bot

      - name: Notify success
        if: success()
        run: echo "✅ Production deployment successful!"
```

## Required GitHub Secrets

Add these in GitHub Settings → Secrets and variables → Actions:

1. `REGISTRY_USERNAME`: Container registry username
2. `REGISTRY_PASSWORD`: Container registry password
3. `KUBE_CONFIG_STAGING`: Base64-encoded kubeconfig for staging
4. `KUBE_CONFIG_PRODUCTION`: Base64-encoded kubeconfig for production

To encode kubeconfig:

```powershell
# PowerShell
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((Get-Content kubeconfig.yaml -Raw)))

# Or bash
cat kubeconfig.yaml | base64 -w 0
```

## GitLab CI Pipeline

Create `.gitlab-ci.yml`:

```yaml
stages:
  - build
  - deploy-staging
  - deploy-production

variables:
  REGISTRY: myxpilotbotacr.azurecr.io
  IMAGE_NAME: xpilot-bot

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $REGISTRY_USER -p $REGISTRY_PASSWORD $REGISTRY
  script:
    - docker build -t $REGISTRY/$IMAGE_NAME:$CI_COMMIT_SHA .
    - docker tag $REGISTRY/$IMAGE_NAME:$CI_COMMIT_SHA $REGISTRY/$IMAGE_NAME:$CI_COMMIT_REF_SLUG
    - docker push $REGISTRY/$IMAGE_NAME:$CI_COMMIT_SHA
    - docker push $REGISTRY/$IMAGE_NAME:$CI_COMMIT_REF_SLUG

deploy-staging:
  stage: deploy-staging
  image: bitnami/kubectl:latest
  only:
    - main
  before_script:
    - echo "$KUBE_CONFIG_STAGING" | base64 -d > kubeconfig
    - export KUBECONFIG=$PWD/kubeconfig
  script:
    - kubectl set image deployment/xpilot-bot xpilot-bot=$REGISTRY/$IMAGE_NAME:$CI_COMMIT_SHA -n xpilot-staging
    - kubectl rollout status deployment/xpilot-bot -n xpilot-staging

deploy-production:
  stage: deploy-production
  image: bitnami/kubectl:latest
  only:
    - tags
  when: manual # Requires manual trigger
  before_script:
    - echo "$KUBE_CONFIG_PRODUCTION" | base64 -d > kubeconfig
    - export KUBECONFIG=$PWD/kubeconfig
  script:
    - kubectl set image deployment/xpilot-bot xpilot-bot=$REGISTRY/$IMAGE_NAME:$CI_COMMIT_TAG -n xpilot-production
    - kubectl rollout status deployment/xpilot-bot -n xpilot-production
```

## Azure DevOps Pipeline

Create `azure-pipelines.yml`:

```yaml
trigger:
  branches:
    include:
      - main
  tags:
    include:
      - v*

pool:
  vmImage: "ubuntu-latest"

variables:
  registry: "myxpilotbotacr.azurecr.io"
  imageName: "xpilot-bot"

stages:
  - stage: Build
    displayName: Build Docker Image
    jobs:
      - job: Build
        steps:
          - task: Docker@2
            inputs:
              command: "buildAndPush"
              containerRegistry: "ACR-Connection"
              repository: $(imageName)
              tags: |
                $(Build.SourceBranchName)
                $(Build.SourceVersion)

  - stage: DeployStaging
    displayName: Deploy to Staging
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: DeployStaging
        environment: "staging"
        strategy:
          runOnce:
            deploy:
              steps:
                - task: Kubernetes@1
                  inputs:
                    connectionType: "Kubernetes Service Connection"
                    kubernetesServiceEndpoint: "K8s-Staging"
                    namespace: "xpilot-staging"
                    command: "set"
                    arguments: "image deployment/xpilot-bot xpilot-bot=$(registry)/$(imageName):$(Build.SourceVersion)"

  - stage: DeployProduction
    displayName: Deploy to Production
    condition: and(succeeded(), startsWith(variables['Build.SourceBranch'], 'refs/tags/v'))
    jobs:
      - deployment: DeployProduction
        environment: "production"
        strategy:
          runOnce:
            deploy:
              steps:
                - task: Kubernetes@1
                  inputs:
                    connectionType: "Kubernetes Service Connection"
                    kubernetesServiceEndpoint: "K8s-Production"
                    namespace: "xpilot-production"
                    command: "set"
                    arguments: "image deployment/xpilot-bot xpilot-bot=$(registry)/$(imageName):$(Build.SourceBranchName)"
```

## Local Deployment Script

Create `deploy.ps1` for manual deployment:

```powershell
#!/usr/bin/env pwsh
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("staging", "production")]
    [string]$Environment,

    [Parameter(Mandatory=$true)]
    [string]$Version
)

$ErrorActionPreference = "Stop"

$registry = "myxpilotbotacr.azurecr.io"
$imageName = "xpilot-bot"
$namespace = "xpilot-$Environment"

Write-Host "🚀 Deploying $imageName:$Version to $Environment..." -ForegroundColor Cyan

# Build image
Write-Host "📦 Building Docker image..." -ForegroundColor Yellow
docker build -t "${registry}/${imageName}:${Version}" .

# Tag as environment-specific
docker tag "${registry}/${imageName}:${Version}" "${registry}/${imageName}:${Environment}-latest"

# Push images
Write-Host "⬆️  Pushing to registry..." -ForegroundColor Yellow
docker push "${registry}/${imageName}:${Version}"
docker push "${registry}/${imageName}:${Environment}-latest"

# Apply Kubernetes manifests
Write-Host "☸️  Applying Kubernetes manifests..." -ForegroundColor Yellow
kubectl apply -f "deployment/$Environment/"

# Update deployment image
Write-Host "🔄 Updating deployment..." -ForegroundColor Yellow
kubectl set image "deployment/xpilot-bot" "xpilot-bot=${registry}/${imageName}:${Version}" -n $namespace

# Wait for rollout
Write-Host "⏳ Waiting for rollout to complete..." -ForegroundColor Yellow
kubectl rollout status "deployment/xpilot-bot" -n $namespace --timeout=5m

# Verify
Write-Host "✅ Verifying deployment..." -ForegroundColor Yellow
kubectl get pods -n $namespace -l app=xpilot-bot

Write-Host "🎉 Deployment complete!" -ForegroundColor Green
Write-Host "View logs: kubectl logs -n $namespace -l app=xpilot-bot -f" -ForegroundColor Cyan
```

Usage:

```powershell
# Deploy to staging
.\deploy.ps1 -Environment staging -Version v1.0.0

# Deploy to production
.\deploy.ps1 -Environment production -Version v1.0.0
```

## Helm Chart (Advanced)

For more complex deployments, consider creating a Helm chart:

```
helm-chart/
├── Chart.yaml
├── values.yaml
├── values-staging.yaml
├── values-production.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    └── secret.yaml
```

Deploy with:

```powershell
# Staging
helm upgrade --install xpilot-bot ./helm-chart -f ./helm-chart/values-staging.yaml -n xpilot-staging

# Production
helm upgrade --install xpilot-bot ./helm-chart -f ./helm-chart/values-production.yaml -n xpilot-production
```

## Best Practices

1. **Use semantic versioning**: `v1.0.0`, `v1.1.0`, etc.
2. **Tag staging with branch name**: `main-abc123`
3. **Tag production with version**: `v1.0.0`
4. **Always test in staging first**
5. **Require manual approval for production**
6. **Keep secrets in CI/CD platform**, not in code
7. **Use environment-specific configs**
8. **Monitor deployments** with logs and health checks
9. **Have rollback plan** ready
10. **Document your pipeline** for team members
