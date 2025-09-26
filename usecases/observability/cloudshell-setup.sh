#!/bin/bash

# CloudShell-optimized setup script for Service Screener Observability

set -e

echo "🚀 Setting up Service Screener Observability in CloudShell..."

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Deploy infrastructure
cd terraform
./deploy.sh

# Get the S3 bucket name
BUCKET_NAME=$(terraform output -raw s3_bucket_name)

# Set up environment variable for current session
echo "export SERVICE_SCREENER_S3_BUCKET=$BUCKET_NAME" >> ~/.bashrc
export SERVICE_SCREENER_S3_BUCKET=$BUCKET_NAME

echo "✅ Setup complete!"
echo "📝 S3 bucket configured: $BUCKET_NAME"
echo "🔄 Environment variable set for future sessions"
echo ""
echo "🎯 Next steps:"
echo "1. Run Service Screener: screener --regions us-east-1 --beta 1"
echo "2. Reports will automatically upload to S3 and trigger metrics processing"
echo "3. Set up QuickSight dashboard using metrics bucket: $(terraform output -raw metrics_bucket_name)"