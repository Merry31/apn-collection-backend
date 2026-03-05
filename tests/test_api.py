import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from main import app
from services.firestore_db import FirestoreDB
from models.camera import CameraInDB, CameraCreate

client = TestClient(app)

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

    return mock_db

# Override the dependency
from api.router import get_db
app.dependency_overrides[get_db] = mock_get_db

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to APN Collection API", "docs_url": "/docs"}

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
