#!/bin/bash

# Gary Bot - Optimized Google Cloud Run Deployment Script
echo "🐳 Deploying Gary Bot to Google Cloud Run (Optimized)..."

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
    exit 1
fi

# Get current project
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: No Google Cloud project is set."
    echo "Please run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

# Set variables for ML workload
SERVICE_NAME="gary-bot"
REGION="us-central1"
MEMORY="8Gi"
CPU="4"
MAX_INSTANCES="10"
TIMEOUT="3600"

echo "📋 Deployment Details:"
echo "   Project ID: $PROJECT_ID"
echo "   Service: $SERVICE_NAME"
echo "   Region: $REGION"
echo "   Memory: $MEMORY"
echo "   CPU: $CPU"
echo "   Timeout: $TIMEOUT seconds"

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com

# Increase Cloud Build timeout
echo "⏱️ Setting Cloud Build timeout..."
gcloud config set builds/timeout 3600

echo "🚀 Deploying to Cloud Run with ML optimizations..."
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory $MEMORY \
  --cpu $CPU \
  --max-instances $MAX_INSTANCES \
  --min-instances 0 \
  --set-secrets GROQ_API_KEY=GROQ_API_KEY:latest \
  --set-env-vars LLM_MODEL="llama3-70b-8192",EMBEDDING_MODEL="all-MiniLM-L6-v2",RAG_RETRIEVAL_COUNT="1",DEFAULT_TEMPERATURE="0.7",MIN_SIMILARITY_THRESHOLD="0.3",TOKENIZERS_PARALLELISM="false",OMP_NUM_THREADS="2" \
  --timeout $TIMEOUT \
  --concurrency 10 \
  --port 8080 \
  --cpu-boost \
  --execution-environment gen2 \
  --no-use-http2

if [ $? -eq 0 ]; then
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    echo "✅ Deployment successful!"
    echo "🌐 Your Gary Bot is now live at: $SERVICE_URL"
    echo ""
    echo "📊 Useful commands:"
    echo "   View logs: gcloud run services logs tail $SERVICE_NAME --region=$REGION"
    echo "   Update service: gcloud run services update $SERVICE_NAME --region=$REGION"
    echo "   Delete service: gcloud run services delete $SERVICE_NAME --region=$REGION"
    
    echo ""
    echo "🔍 Testing the deployment..."
    curl -f "$SERVICE_URL/_stcore/health" && echo "✅ Health check passed!" || echo "⚠️ Health check failed - check logs"
else
    echo "❌ Deployment failed. Check the logs above for details."
    echo "💡 Try these troubleshooting steps:"
    echo "   1. Check build logs: gcloud builds list --limit=5"
    echo "   2. Check service logs: gcloud run services logs tail $SERVICE_NAME --region=$REGION"
    echo "   3. Verify Docker locally: docker build -t gary-bot ."
    exit 1
fi 