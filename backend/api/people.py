from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import numpy as np
import base64
from deepface import DeepFace

from backend.db.database import get_db
from backend.db.models import Visitor
from backend.db.schemas import VisitorResponse, VisitorSyncResponse

router = APIRouter(prefix="/people", tags=["People"])

# Constant for alignment with the Raspberry Pi
MODEL_NAME = "Facenet512"

@router.post("/enroll", response_model=VisitorResponse)
async def enroll_visitor(
    name: str = Body(...),
    relation: str = Body(...),
    memory_anchor: str = Body(None),
    image_base64: str = Body(...), # Captured frame from dashboard
    db: AsyncSession = Depends(get_db)
):
    """
    Processes the enrollment image, generates a Facenet512 embedding, 
    and saves the visitor to the database.
    """
    try:
        # 1. Generate Embedding using DeepFace
        # We use detector_backend='opencv' for speed during enrollment
        results = DeepFace.represent(
            img_path=image_base64,
            model_name=MODEL_NAME,
            enforce_detection=True,
            detector_backend="opencv",
            align=True
        )

        if not results:
            raise HTTPException(status_code=400, detail="No face detected in the image.")

        # 2. Extract the 512-d vector and convert to bytes
        embedding = np.array(results[0]["embedding"], dtype=np.float32)
        encoding_bytes = embedding.tobytes()

        # 3. Save to Database
        new_visitor = Visitor(
            name=name,
            relation=relation,
            memory_anchor=memory_anchor,
            encoding=encoding_bytes
        )
        
        db.add(new_visitor)
        await db.commit()
        await db.refresh(new_visitor)
        return new_visitor

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enrollment failed: {str(e)}")

@router.get("/sync", response_model=list[VisitorSyncResponse])
async def get_all_encodings(db: AsyncSession = Depends(get_db)):
    """
    Endpoint for the Raspberry Pi to download all known faces and their vectors.
    """
    result = await db.execute(select(Visitor))
    visitors = result.scalars().all()
    
    # The Pydantic schema 'VisitorSyncResponse' handles the Bytes -> Base64 conversion
    return visitors

@router.get("/{visitor_id}", response_model=VisitorResponse)
async def get_visitor(visitor_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Visitor).where(Visitor.id == visitor_id))
    visitor = result.scalars().first()
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    return visitor