from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary, Text
from sqlalchemy.sql import func
from .database import Base

class Visitor(Base):
    __tablename__ = "visitors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    relationship = Column(String, nullable=False)
    memory_anchor = Column(Text, nullable=True)  # The fact Gemini will use
    encoding = Column(LargeBinary, nullable=False)  # 128-d face vector
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    visitor_id = Column(Integer, ForeignKey("visitors.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    # You can add 'mood' or 'detected_dignity' metrics here later