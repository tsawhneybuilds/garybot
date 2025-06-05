#!/bin/bash

# Gary Bot - Google App Engine Deployment Script
echo "🚀 Deploying Gary Bot to Google App Engine..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo "❌ Error: Not authenticated with gcloud."
    echo "Please run: gcloud auth login"
    exit 1
fi

# Check for GROQ_API_KEY
if [ -z "$GROQ_API_KEY" ]; then
    echo "❌ Error: GROQ_API_KEY environment variable is not set."
    echo "Please set it with: export GROQ_API_KEY=your_api_key_here"
    echo "Or add it to your shell profile for persistence."
    exit 1
fi

# Get current project
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: No Google Cloud project is set."
    echo "Please run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📋 Deployment Details:"
echo "   Project ID: $PROJECT_ID"
echo "   Runtime: Python 3.11"
echo "   Service: Gary Bot"

# Create a temporary app.yaml with the API key
echo "🔧 Preparing deployment configuration..."
cp app.yaml app.yaml.backup

# Add the API key to app.yaml temporarily
sed "/env_variables:/a\\
  GROQ_API_KEY: \"$GROQ_API_KEY\"" app.yaml > app_deploy.yaml

# Deploy the application
echo "🚀 Starting deployment..."
gcloud app deploy app_deploy.yaml --quiet

# Clean up temporary file
rm app_deploy.yaml

# Restore original app.yaml
mv app.yaml.backup app.yaml

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo "🌐 Your Gary Bot is now live at: https://$PROJECT_ID.appspot.com"
    echo ""
    echo "📊 Useful commands:"
    echo "   View logs: gcloud app logs tail -s default"
    echo "   Open app: gcloud app browse"
    echo "   View instances: gcloud app instances list"
else
    echo "❌ Deployment failed. Check the logs above for details."
    exit 1
fi 