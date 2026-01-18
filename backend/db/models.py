from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Visitor(Base):
    __tablename__ = "visitors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    # Renamed from relationship_type to avoid confusion with the relationship() function
    relation = Column(String, nullable=False) 
    memory_anchor = Column(Text, nullable=True)
    encoding = Column(LargeBinary, nullable=False) # Stores float32 vector as bytes
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ORM relationship for easier access to history
    visits = relationship("Visit", back_populates="visitor", cascade="all, delete-orphan")

class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    visitor_id = Column(Integer, ForeignKey("visitors.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    visitor = relationship("Visitor", back_populates="visits")

    # Index for fast lookup when querying for the most recent visit
    __table_args__ = (Index("ix_visits_visitor_id_timestamp", "visitor_id", "timestamp"),)