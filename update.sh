#!/bin/bash

# Gary Bot - Quick Update Script for Google Cloud Run
echo "🔄 Updating Gary Bot on Google Cloud Run..."

# Check if GROQ_API_KEY is set
if [ -z "$GROQ_API_KEY" ]; then
    echo "❌ Error: GROQ_API_KEY environment variable is not set."
    echo "Please set it with: export GROQ_API_KEY=your_api_key_here"
    exit 1
fi

echo "🚀 Deploying updates..."
gcloud run deploy gary-bot \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GROQ_API_KEY="$GROQ_API_KEY",LLM_MODEL="llama3-70b-8192",EMBEDDING_MODEL="all-MiniLM-L6-v2"

if [ $? -eq 0 ]; then
    echo "✅ Update successful!"
    echo "🌐 Your updated Gary Bot is live at: https://gary-bot-471522940884.us-central1.run.app"
else
    echo "❌ Update failed. Check the logs above for details."
    exit 1
fi 