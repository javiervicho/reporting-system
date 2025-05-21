from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator

class GeoPoint(BaseModel):
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)

class IncidentBase(BaseModel):
    title: str
    description: str
    incident_type: str
    severity: int = Field(..., ge=1, le=5)
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    
class IncidentCreate(IncidentBase):
    reporter_info: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    incident_type: Optional[str] = None
    severity: Optional[int] = Field(None, ge=1, le=5)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    status: Optional[str] = None
    reporter_info: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class Incident(IncidentBase):
    id: int
    reported_at: datetime
    status: str
    reporter_info: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

class IncidentSearchParams(BaseModel):
    # For standard search
    incident_type: Optional[str] = None
    severity: Optional[int] = None
    status: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    
    # For proximity search
    center: Optional[GeoPoint] = None
    radius: Optional[float] = None  # in meters
    
    # For area search
    polygon: Optional[List[GeoPoint]] = None
    
    # For text similarity search
    description_query: Optional[str] = None
    
    # Pagination
    skip: int = 0
    limit: int = 100 