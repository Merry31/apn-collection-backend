from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List
from models.camera import CameraCreate, CameraUpdate, CameraInDB
from services.firestore_db import FirestoreDB
from services.gcs_storage import GCSStorage
from api.auth import verify_firebase_token

router = APIRouter(prefix="/cameras", tags=["cameras"])

def get_db():
    return FirestoreDB()

def get_storage():
    return GCSStorage()

@router.get("/", response_model=List[CameraInDB])
def read_cameras(db: FirestoreDB = Depends(get_db), user: dict = Depends(verify_firebase_token)):
    return db.get_cameras()

@router.get("/{camera_id}", response_model=CameraInDB)
def read_camera(camera_id: str, db: FirestoreDB = Depends(get_db), user: dict = Depends(verify_firebase_token)):
    camera = db.get_camera(camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

@router.post("/", response_model=CameraInDB, status_code=201)
def create_camera(
    camera: CameraCreate, 
    db: FirestoreDB = Depends(get_db),
    user: dict = Depends(verify_firebase_token)
):
    try:
        return db.add_camera(camera)
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@router.put("/{camera_id}", response_model=CameraInDB)
def update_camera(
    camera_id: str, 
    camera_update: CameraUpdate, 
    db: FirestoreDB = Depends(get_db),
    user: dict = Depends(verify_firebase_token)
):
    try:
        camera = db.update_camera(camera_id, camera_update)
        if camera is None:
            raise HTTPException(status_code=404, detail="Camera not found")
        return camera
    except HTTPException:
        raise
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{camera_id}", status_code=204)
def delete_camera(
    camera_id: str, 
    db: FirestoreDB = Depends(get_db),
    user: dict = Depends(verify_firebase_token)
):
    try:
        success = db.delete_camera(camera_id)
        if not success:
            raise HTTPException(status_code=404, detail="Camera not found")
    except HTTPException:
        raise
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@router.post("/{camera_id}/images", response_model=CameraInDB)
async def upload_camera_image(
    camera_id: str, 
    file: UploadFile = File(...), 
    db: FirestoreDB = Depends(get_db),
    storage: GCSStorage = Depends(get_storage),
    user: dict = Depends(verify_firebase_token)
):
    camera = db.get_camera(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    try:
        # Upload to Google Cloud Storage
        image_url = await storage.upload_image(camera_id, file)
        
        # Update camera object with new image URL
        current_urls = camera.image_urls or []
        current_urls.append(image_url)
        update_data = CameraUpdate(image_urls=current_urls)
        
        updated_camera = db.update_camera(camera_id, update_data)
        return updated_camera

    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
