import unittest
from fastapi.testclient import TestClient
from main import app
from api.auth import verify_firebase_token

# Mock the authentication dependency
def mock_verify_julien():
    return {
        "uid": "julien-uid-123",
        "email": "julien.rallo@gmail.com",
        "email_verified": True
    }

class TestJulienAccess(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Apply the override
        app.dependency_overrides[verify_firebase_token] = mock_verify_julien

    def tearDown(self):
        # Clear overrides after test
        app.dependency_overrides.clear()

    def test_get_cameras_as_julien(self):
        response = self.client.get("/api/v1/cameras/", headers={"Authorization": "Bearer mocked_token"})
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.json()}")
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
