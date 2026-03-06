import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from main import app
from services.firestore_db import FirestoreDB
from services.gcs_storage import GCSStorage
from models.camera import CameraInDB, CameraCreate
from api.auth import verify_firebase_token

client = TestClient(app)

class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)

# Helper function to mock the get_db dependency
def mock_get_db():
    mock_db = MagicMock(spec=FirestoreDB)
    
    # Mock get_cameras
    mock_db.get_cameras.return_value = [
        CameraInDB(id="mock-id-1", brand="Canon", model="AE-1", type="Film", year=1976, format="35mm")
    ]
    
    # Mock get_camera
    def mock_get_camera_func(camera_id):
        if camera_id == "mock-id-1":
            return CameraInDB(id="mock-id-1", brand="Canon", model="AE-1", type="Film", year=1976, format="35mm")
        return None
    mock_db.get_camera.side_effect = mock_get_camera_func
    
    # Mock add_camera
    mock_db.add_camera.return_value = CameraInDB(
        id="new-mock-id", brand="Nikon", model="F3", type="Film", year=1980, format="35mm"
    )

    # Mock delete_camera
    def mock_delete_camera_func(camera_id):
        return camera_id == "mock-id-1"
    mock_db.delete_camera.side_effect = mock_delete_camera_func
    
    # Mock update_camera
    def mock_update_camera_func(camera_id, update_data):
         if camera_id == "mock-id-1":
             return CameraInDB(id="mock-id-1", brand="Canon", model="AE-1", type="Film", year=1976, format="35mm", image_urls=update_data.image_urls)
         return None
    mock_db.update_camera.side_effect = mock_update_camera_func

    return mock_db

def mock_get_storage():
    mock_storage = MagicMock(spec=GCSStorage)
    mock_storage.upload_image = AsyncMock(return_value="https://storage.googleapis.com/mock-bucket/mock-id/mock-uuid.jpg")
    return mock_storage

# Override the dependencies
from api.router import get_db, get_storage
app.dependency_overrides[get_db] = mock_get_db
app.dependency_overrides[get_storage] = mock_get_storage
app.dependency_overrides[verify_firebase_token] = lambda: {"uid": "mock-user-id", "email": "mock@test.com"}

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "<html" in response.text
    assert "<title>APN Collection Manager</title>" in response.text

def test_get_cameras():
    response = client.get("/api/v1/cameras/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["brand"] == "Canon"
    assert data[0]["id"] == "mock-id-1"

def test_get_camera_exists():
    response = client.get("/api/v1/cameras/mock-id-1")
    assert response.status_code == 200
    assert response.json()["model"] == "AE-1"

def test_get_camera_not_found():
    response = client.get("/api/v1/cameras/non-existent-id")
    assert response.status_code == 404

def test_create_camera():
    new_cam = {
        "brand": "Nikon",
        "model": "F3",
        "type": "Film",
        "year": 1980,
        "format": "35mm"
    }
    response = client.post("/api/v1/cameras/", json=new_cam)
    assert response.status_code == 201
    assert response.json()["id"] == "new-mock-id"

def test_delete_camera():
    response = client.delete("/api/v1/cameras/mock-id-1")
    assert response.status_code == 204

def test_delete_camera_not_found():
    response = client.delete("/api/v1/cameras/non-existent-id")
    assert response.status_code == 404

def test_upload_image():
    # simulate file upload
    files = {'file': ('test_image.jpg', b'dummy content', 'image/jpeg')}
    response = client.post("/api/v1/cameras/mock-id-1/images", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "image_urls" in data
    assert "https://storage.googleapis.com/mock-bucket/mock-id/mock-uuid.jpg" in data["image_urls"]

