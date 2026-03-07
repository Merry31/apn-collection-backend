from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth, credentials
import os

# Initialize Firebase Admin if not already initialized
if not len(firebase_admin._apps):
    try:
        # It will use Application Default Credentials (ADC)
        # In Cloud Run, it gets credentials from the attached service account.
        # Locally, it gets them from `gcloud auth application-default login`.
        # Set Explicit Project ID to validate tokens for the correct Firebase Project
        firebase_admin.initialize_app(options={'projectId': 'apn-collection-backend-d-9fa01'})
    except Exception as e:
        print(f"Failed to initialize Firebase Admin: {e}")

security = HTTPBearer()

def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verifies the Firebase JWT token provided in the Authorization header.
    Returns the decoded token dictionary if valid.
    """
    token = credentials.credentials
    try:
        # Verify the ID token and get the decoded payload
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid Firebase ID token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Expired Firebase ID token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"Error validating token: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
