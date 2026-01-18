from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary, Text
from sqlalchemy.orm import relationship  # Ensure this is exactly like this
from sqlalchemy.sql import func
from .database import Base

class Visitor(Base):
    __tablename__ = "visitors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    relationship_type = Column(String, nullable=False) # RENAME THIS
    memory_anchor = Column(Text, nullable=True)
    encoding = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # This 'relationship' function call was likely clashing with the column name above
    visits = relationship("Visit", back_populates="visitor")

class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    visitor_id = Column(Integer, ForeignKey("visitors.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    visitor = relationship("Visitor", back_populates="visits")