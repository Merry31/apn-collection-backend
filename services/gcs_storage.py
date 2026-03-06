import uuid
from google.cloud import storage
from fastapi import UploadFile
import os

class GCSStorage:
    def __init__(self, project_id: str = "apn-collection-backend-d-9fa01", bucket_name: str = "apn-collection-backend-d-9fa01.firebasestorage.app"):
        self.bucket_name = bucket_name
        self.project_id = project_id
        try:
            self.client = storage.Client(project=project_id)
            self.bucket = self.client.bucket(bucket_name)
        except Exception as e:
            print(f"Failed to initialize GCS Client: {e}")
            self.client = None
            self.bucket = None

    async def upload_image(self, camera_id: str, file: UploadFile) -> str:
        """
        Uploads an image to GCS and returns the public URL.
        """
        if not self.bucket:
            raise Exception("GCS Client not initialized")

        # Generate a unique filename using UUID to prevent collisions
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{camera_id}/{uuid.uuid4()}{file_extension}"
        
        blob = self.bucket.blob(unique_filename)

        # Upload the file
        blob.upload_from_file(file.file, content_type=file.content_type)
        
        # Return the object path instead of the public URL
        # The frontend will use the Firebase Storage SDK to generate a temporary download URL.
        return unique_filename
