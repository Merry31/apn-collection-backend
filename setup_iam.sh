#!/bin/bash

# Configuration
PROJECT_ID="apn-collection-backend-d-9fa01"
REGION="europe-west1"
SERVICE_ACCOUNT="apn-collection-sa@${PROJECT_ID}.iam.gserviceaccount.com"
BUCKET_NAME="apn-collection-backend-d-9fa01.firebasestorage.app"

echo "Setting up IAM roles and Service Account for APN Collection Backend..."

# Create Service Account if it doesn't exist
if ! gcloud iam service-accounts describe "${SERVICE_ACCOUNT}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
    echo "Creating service account..."
    gcloud iam service-accounts create apn-collection-sa \
        --description="Service account for APN Collection Backend Cloud Run" \
        --display-name="APN Collection Backend SA" \
        --project="${PROJECT_ID}"
else
    echo "Service account already exists."
fi

# 1. Grant Datastore/Firestore Access
echo "Granting Datastore User role..."
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/datastore.user" \
    --condition=None

# 2. Grant Cloud Storage Access for the Images Bucket
echo "Granting Storage Object Admin role on bucket ${BUCKET_NAME}..."
gsutil iam ch "serviceAccount:${SERVICE_ACCOUNT}:objectAdmin" "gs://${BUCKET_NAME}"

echo "IAM Setup complete!"
echo "When deploying to Cloud Run, ensure you specify this service account:"
echo "--service-account=${SERVICE_ACCOUNT}"
