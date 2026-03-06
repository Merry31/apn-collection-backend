import pytest
import os
from fastapi.testclient import TestClient
from main import app
from services.firestore_db import FirestoreDB
from api.auth import verify_firebase_token

# These tests will only run if a specific environment variable is set
# because they require an actual Firestore connection (e.g. to a test project or emulator)
pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_INTEGRATION_TESTS") != "1",
    reason="Need RUN_INTEGRATION_TESTS=1 to run against real/emulator Firestore"
)

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_teardown_db():
    # Uses the normal dependancy which will instantiate FirestoreDB
    # It will use `apn-collection-backend-d-9fa01` by default
    db = FirestoreDB()
    
    # Override auth dependency for tests
    app.dependency_overrides[verify_firebase_token] = lambda: {"uid": "test-user-id", "email": "test@example.com"}
    
    yield db
    # Teardown: we could optionally delete all documents created during testing
    app.dependency_overrides = {}

def test_create_and_get_camera(setup_teardown_db):
    new_cam = {
        "brand": "TestBrand",
        "model": "TestModel",
        "type": "Digital",
        "year": 2024
    }
    
    # Create
    create_response = client.post("/api/v1/cameras/", json=new_cam)
    assert create_response.status_code == 201
    created_cam = create_response.json()
    assert "id" in created_cam
    assert created_cam["brand"] == "TestBrand"
    
    cam_id = created_cam["id"]

    # Read
    get_response = client.get(f"/api/v1/cameras/{cam_id}")
    assert get_response.status_code == 200
    assert get_response.json()["model"] == "TestModel"

    # Clean up (Delete)
    delete_response = client.delete(f"/api/v1/cameras/{cam_id}")
    assert delete_response.status_code == 204

def test_upload_image_integration(setup_teardown_db):
    new_cam = {
        "brand": "UploadTestBrand",
        "model": "UploadTestModel",
        "type": "Digital",
        "year": 2024
    }
    
    # Create
    create_response = client.post("/api/v1/cameras/", json=new_cam)
    assert create_response.status_code == 201
    cam_id = create_response.json()["id"]

    try:
        # Upload Image
        files = {'file': ('test_integration.jpg', b'dummy content', 'image/jpeg')}
        upload_response = client.post(f"/api/v1/cameras/{cam_id}/images", files=files)
        
        assert upload_response.status_code == 200
        
        updated_cam = upload_response.json()
        assert "image_urls" in updated_cam
        assert len(updated_cam["image_urls"]) == 1
        assert "storage.googleapis.com" in updated_cam["image_urls"][0]
        
    finally:
        # Clean up (Delete)
        client.delete(f"/api/v1/cameras/{cam_id}")
