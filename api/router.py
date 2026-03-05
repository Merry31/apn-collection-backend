from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.camera import CameraCreate, CameraUpdate, CameraInDB
from services.firestore_db import FirestoreDB

router = APIRouter(prefix="/cameras", tags=["cameras"])

def get_db():
    return FirestoreDB()

@router.get("/", response_model=List[CameraInDB])
def read_cameras(db: FirestoreDB = Depends(get_db)):
    return db.get_cameras()

@router.get("/{camera_id}", response_model=CameraInDB)
def read_camera(camera_id: str, db: FirestoreDB = Depends(get_db)):
    camera = db.get_camera(camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

@router.post("/", response_model=CameraInDB, status_code=201)
def create_camera(camera: CameraCreate, db: FirestoreDB = Depends(get_db)):
    try:
        return db.add_camera(camera)
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@router.put("/{camera_id}", response_model=CameraInDB)
def update_camera(camera_id: str, camera_update: CameraUpdate, db: FirestoreDB = Depends(get_db)):
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
def delete_camera(camera_id: str, db: FirestoreDB = Depends(get_db)):
    try:
        success = db.delete_camera(camera_id)
        if not success:
            raise HTTPException(status_code=404, detail="Camera not found")
    except HTTPException:
        raise
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
