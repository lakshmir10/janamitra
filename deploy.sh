#!/bin/bash
set -e
PROJECT_ID=${1:?"Usage: ./deploy.sh PROJECT_ID GEMINI_API_KEY GOOGLE_API_KEY SEARCH_CX"}
GEMINI_API_KEY=${2:?"Provide GEMINI_API_KEY"}
GOOGLE_API_KEY=${3:?"Provide GOOGLE_API_KEY"}
SEARCH_CX=${4:-""}
REGION="us-central1"
SERVICE="janamitra"

echo "🗳️ Deploying JanaMitra..."
gcloud config set project "$PROJECT_ID"
echo "📦 Enabling APIs..."
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
    cloudbuild.googleapis.com translate.googleapis.com texttospeech.googleapis.com \
    youtube.googleapis.com civicinfo.googleapis.com customsearch.googleapis.com
echo "🚀 Building & deploying..."
gcloud run deploy "$SERVICE" --source . --region "$REGION" --allow-unauthenticated \
    --set-env-vars "GEMINI_API_KEY=$GEMINI_API_KEY,GOOGLE_API_KEY=$GOOGLE_API_KEY,GOOGLE_SEARCH_CX=$SEARCH_CX" \
    --memory 512Mi --cpu 1 --min-instances 0 --max-instances 3 --timeout 60
URL=$(gcloud run services describe "$SERVICE" --region "$REGION" --format 'value(status.url)')
echo "✅ Live: $URL"
echo "   Health: $URL/health"
