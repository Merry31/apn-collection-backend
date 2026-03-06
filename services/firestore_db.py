from google.cloud import firestore
from models.camera import CameraCreate, CameraUpdate, CameraInDB
from typing import List, Optional

class FirestoreDB:
    def __init__(self, project_id: str = "apn-collection-backend-d-9fa01"):
        # The client will automatically pick up application default credentials
        # from the environment when running in GCP, or from 'gcloud auth application-default login'
        # when running locally.
        try:
            self.db = firestore.Client(project=project_id)
            self.collection = self.db.collection('cameras')
        except Exception as e:
            print(f"Failed to initialize Firestore Client: {e}")
            self.db = None
            self.collection = None

    def get_cameras(self) -> List[CameraInDB]:
        if not self.collection:
            return []
        
        docs = self.collection.stream()
        cameras = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            cameras.append(CameraInDB(**data))
        return cameras

    def get_camera(self, camera_id: str) -> Optional[CameraInDB]:
        if not self.collection:
            return None
        
        doc_ref = self.collection.document(camera_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return CameraInDB(**data)
        return None

    def add_camera(self, camera: CameraCreate) -> CameraInDB:
        if not self.collection:
            raise Exception("Firestore is not initialized")
        
        doc_ref = self.collection.document()
        doc_ref.set(camera.model_dump())
        
        return self.get_camera(doc_ref.id)

    def update_camera(self, camera_id: str, camera_update: CameraUpdate) -> Optional[CameraInDB]:
        if not self.collection:
            raise Exception("Firestore is not initialized")
        
        doc_ref = self.collection.document(camera_id)
        if not doc_ref.get().exists:
            return None
            
        update_data = {k: v for k, v in camera_update.model_dump().items() if v is not None}
        if update_data:
            doc_ref.update(update_data)
        
        return self.get_camera(camera_id)

    def delete_camera(self, camera_id: str) -> bool:
        if not self.collection:
            raise Exception("Firestore is not initialized")
            
        doc_ref = self.collection.document(camera_id)
        if doc_ref.get().exists:
            doc_ref.delete()
            return True
        return False
