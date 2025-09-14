@echo off
REM Insurance Claims Data Automation System - Deployment Script for Windows

echo 🚀 Starting deployment of Insurance Claims Data Automation System

REM Configuration
set AWS_REGION=us-east-1
set ECR_REPOSITORY=insurance-claims-automation
set ECS_CLUSTER=insurance-claims-cluster
set ECS_SERVICE=insurance-claims-automation-service

REM Get AWS Account ID
for /f %%i in ('aws sts get-caller-identity --query Account --output text') do set AWS_ACCOUNT_ID=%%i
echo 📋 AWS Account ID: %AWS_ACCOUNT_ID%

REM Build and push Docker image
echo 🔨 Building Docker image...
docker build -t %ECR_REPOSITORY% .

echo 🏷️ Tagging image for ECR...
docker tag %ECR_REPOSITORY%:latest %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com/%ECR_REPOSITORY%:latest

echo 🔐 Logging into ECR...
aws ecr get-login-password --region %AWS_REGION% | docker login --username AWS --password-stdin %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com

echo 📤 Pushing image to ECR...
docker push %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com/%ECR_REPOSITORY%:latest

REM Update ECS service
echo 🔄 Updating ECS service...
aws ecs update-service --cluster %ECS_CLUSTER% --service %ECS_SERVICE% --force-new-deployment --region %AWS_REGION%

echo ⏳ Waiting for deployment to complete...
aws ecs wait services-stable --cluster %ECS_CLUSTER% --services %ECS_SERVICE% --region %AWS_REGION%

echo ✅ Deployment completed successfully!
echo 🌐 Application should be available at your load balancer endpoint

REM Get service endpoint
echo 🔍 Getting service endpoint...
for /f %%i in ('aws elbv2 describe-load-balancers --region %AWS_REGION% --query "LoadBalancers[?contains(LoadBalancerName, `insurance-claims`)].DNSName" --output text') do set SERVICE_ENDPOINT=%%i
echo 📍 Service endpoint: http://%SERVICE_ENDPOINT%

pause

