from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db.database import get_db
from backend.db.models import Visitor
from backend.db.schemas import VisitorCreate, VisitorResponse, VisitorSyncResponse

# This is the 'router' that main.py is looking for
router = APIRouter(prefix="/people", tags=["People"])

@router.post("/enroll", response_model=VisitorResponse)
async def enroll_visitor(visitor_data: VisitorCreate, db: AsyncSession = Depends(get_db)):
    """Saves a new visitor and their face encoding."""
    new_visitor = Visitor(
        name=visitor_data.name,
        relationship_type=visitor_data.relationship_type, # Fixed naming
        memory_anchor=visitor_data.memory_anchor,
        encoding=visitor_data.encoding  
    )
    db.add(new_visitor)
    await db.commit()
    await db.refresh(new_visitor)
    return new_visitor

@router.get("/sync", response_model=list[VisitorSyncResponse])
async def get_all_encodings(limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Pi calls this on startup to load known faces."""
    result = await db.execute(select(Visitor).limit(limit))
    return result.scalars().all()

@router.get("/{visitor_id}", response_model=VisitorResponse)
async def get_visitor(visitor_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Visitor).where(Visitor.id == visitor_id))
    visitor = result.scalars().first()
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    return visitor