import os
from fastapi import Request
from main import app
import uvicorn
from api.auth import verify_firebase_token
from services.firestore_db import FirestoreDB

# Override the authentication dependency to always return a mock user
def mock_verify_firebase_token(request: Request):
    return {"uid": "karate-test-user-id", "email": "test@karate.com"}

app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token

# Automatically connect to the test project if needed
# The default FirestoreDB uses `apn-collection-backend-d-9fa01` which works for our test.

if __name__ == "__main__":
    print("Starting Karate Test API on port 8081...")
    uvicorn.run(app, host="127.0.0.1", port=8081, log_level="info")
