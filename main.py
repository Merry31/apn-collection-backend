from fastapi import FastAPI
from api.router import router as camera_router
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="APN Collection API",
    description="API for managing a collection of film and digital cameras.",
    version="1.0.0"
)

# CORS configuration
origins = [
    "*"  # Allows all origins for development. In production, specify allowed origins.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(camera_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Welcome to APN Collection API", "docs_url": "/docs"}

if __name__ == "__main__":
    import uvicorn
    # Cloud Run uses the PORT environment variable. Defaults to 8080.
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
