from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db.database import get_db
from ..db.models import Visitor
from ..db.schemas import VisitorCreate, VisitorResponse

router = APIRouter(prefix="/people", tags=["People"])

@router.post("/enroll", response_model=VisitorResponse)
async def enroll_visitor(visitor_data: VisitorCreate, db: AsyncSession = Depends(get_db)):
    """Saves a new visitor and their 128-d face encoding."""
    new_visitor = Visitor(
        name=visitor_data.name,
        relationship=visitor_data.relationship,
        memory_anchor=visitor_data.memory_anchor,
        encoding=visitor_data.encoding  # Received as bytes
    )
    db.add(new_visitor)
    await db.commit()
    await db.refresh(new_visitor)
    return new_visitor

@router.get("/{visitor_id}", response_model=VisitorResponse)
async def get_visitor(visitor_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Visitor).where(Visitor.id == visitor_id))
    visitor = result.scalars().first()
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    return 

# Add this to your existing people.py
@router.get("/sync", response_model=list[VisitorResponse])
async def get_all_encodings(db: AsyncSession = Depends(get_db)):
    """Pi calls this on startup to load all known faces into memory."""
    result = await db.execute(select(Visitor))
    return result.scalars().all()