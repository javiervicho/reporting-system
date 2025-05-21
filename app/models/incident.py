from sqlalchemy import Column, Integer, String, Text, DateTime, Float, func
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from pgvector.sqlalchemy import Vector

from app.db.session import Base

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    incident_type = Column(String(100), nullable=False, index=True)
    severity = Column(Integer, nullable=False)
    
    # Geospatial data
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    
    # Metadata
    reported_at = Column(DateTime, nullable=False, default=func.now())
    reporter_info = Column(JSONB, nullable=True)  # Optional reporter information
    status = Column(String(50), nullable=False, default="reported")
    
    # Vector embedding for similarity search
    description_embedding = Column(Vector(384), nullable=True)  # 384 dimensions for all-MiniLM-L6-v2
    
    # Additional metadata
    metadata = Column(JSONB, nullable=True)  # For any additional data
    
    def __repr__(self):
        return f"<Incident {self.id}: {self.title}>" 