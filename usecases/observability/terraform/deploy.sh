#!/bin/bash

# Service Screener Observability Infrastructure Deployment Script

set -e

echo "🚀 Deploying Service Screener Observability Infrastructure..."

# Check if Terraform is installed, install if needed
if ! command -v terraform &> /dev/null; then
    echo "📦 Installing Terraform for CloudShell..."
    cd /tmp
    wget -q https://releases.hashicorp.com/terraform/1.6.6/terraform_1.6.6_linux_amd64.zip
    unzip -q terraform_1.6.6_linux_amd64.zip
    sudo mv terraform /usr/local/bin/
    cd - > /dev/null
    echo "✅ Terraform installed successfully"
fi

# Initialize Terraform
echo "📦 Initializing Terraform..."
terraform init

# Plan the deployment
echo "📋 Planning Terraform deployment..."
terraform plan

# Ask for confirmation
read -p "🤔 Do you want to proceed with the deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled."
    exit 1
fi

# Apply the configuration
echo "🔧 Applying Terraform configuration..."
terraform apply -auto-approve

# Get outputs
echo "📊 Deployment completed! Here are the important details:"
echo
echo "S3 Bucket: $(terraform output -raw s3_bucket_name)"
echo "Lambda Function: $(terraform output -raw lambda_function_name)"
echo "Metrics Bucket: $(terraform output -raw metrics_bucket_name)"
echo
echo "✅ To enable observability, set the following environment variable:"
echo "export SERVICE_SCREENER_S3_BUCKET=$(terraform output -raw s3_bucket_name)"
echo
echo "🎯 Next steps:"
echo "1. Set the S3 bucket environment variable in your CloudShell session"
echo "2. Run Service Screener as usual - reports will automatically be uploaded"
echo "3. Set up QuickSight dashboard using metrics bucket: $(terraform output -raw metrics_bucket_name)"