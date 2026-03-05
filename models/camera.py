from typing import Optional, List
from pydantic import BaseModel, Field

class CameraBase(BaseModel):
    brand: str = Field(..., description="Brand of the camera, e.g., Canon, Nikon")
    model: str = Field(..., description="Model name of the camera")
    type: str = Field(..., description="Type of camera, e.g., DSLR, Mirrorless, Point & Shoot, Film")
    year: Optional[int] = Field(None, description="Year of release")
    format: Optional[str] = Field(None, description="Film format or sensor size, e.g., 35mm, Medium Format, Full Frame")
    condition: Optional[str] = Field(None, description="Physical and working condition")
    notes: Optional[str] = Field(None, description="Any additional notes about this specific camera")

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    type: Optional[str] = None
    year: Optional[int] = None
    format: Optional[str] = None
    condition: Optional[str] = None
    notes: Optional[str] = None

class CameraInDB(CameraBase):
    id: str = Field(..., description="Firestore document ID")

