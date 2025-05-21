from typing import List, Optional, Any, Dict, Union
import json
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from geoalchemy2.functions import ST_DWithin, ST_SetSRID, ST_MakePoint, ST_GeomFromGeoJSON
from sentence_transformers import SentenceTransformer
import numpy as np

from app.core.config import settings
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentUpdate

# Initialize embedding model
embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

def generate_embedding(text: str) -> List[float]:
    """
    Generate a vector embedding for the given text.
    """
    return embedding_model.encode(text).tolist()

def create_incident(db: Session, incident_in: IncidentCreate) -> Incident:
    """
    Create a new incident with embedding and geospatial data.
    """
    # Generate embedding for the description
    embedding = generate_embedding(incident_in.description)
    
    # Create a DB object
    db_obj = Incident(
        title=incident_in.title,
        description=incident_in.description,
        incident_type=incident_in.incident_type,
        severity=incident_in.severity,
        longitude=incident_in.longitude,
        latitude=incident_in.latitude,
        # Create a PostGIS Point from lat/lon
        location=ST_SetSRID(
            ST_MakePoint(incident_in.longitude, incident_in.latitude),
            4326
        ),
        description_embedding=embedding,
        reporter_info=incident_in.reporter_info,
        metadata=incident_in.metadata
    )
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_incident(db: Session, id: int) -> Optional[Incident]:
    """
    Get an incident by ID.
    """
    return db.query(Incident).filter(Incident.id == id).first()

def get_incidents(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    incident_type: Optional[str] = None
) -> List[Incident]:
    """
    Get multiple incidents with optional filtering.
    """
    query = db.query(Incident)
    
    # Apply filters if provided
    if incident_type:
        query = query.filter(Incident.incident_type == incident_type)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    return query.all()

def update_incident(
    db: Session, 
    db_obj: Incident,
    obj_in: Union[IncidentUpdate, Dict[str, Any]]
) -> Incident:
    """
    Update an incident.
    """
    # Convert to dict if it's not already
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    # Check if description is being updated, and regenerate the embedding if so
    if "description" in update_data:
        update_data["description_embedding"] = generate_embedding(update_data["description"])
    
    # Check if location is being updated
    if "longitude" in update_data and "latitude" in update_data:
        # Update the PostGIS Point geometry
        update_data["location"] = ST_SetSRID(
            ST_MakePoint(update_data["longitude"], update_data["latitude"]),
            4326
        )
    
    # Update fields
    for field in update_data:
        if field in ["location", "description_embedding"]:
            continue  # These are handled separately
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_incident(db: Session, id: int) -> Incident:
    """
    Delete an incident.
    """
    obj = db.query(Incident).get(id)
    db.delete(obj)
    db.commit()
    return obj

def search_incidents_by_proximity(
    db: Session,
    latitude: float,
    longitude: float,
    radius: float,  # in meters
    limit: int = 10
) -> List[Incident]:
    """
    Search for incidents within a specified radius from a point.
    """
    point = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
    
    query = db.query(Incident).filter(
        ST_DWithin(
            Incident.location,
            point,
            radius
        )
    ).limit(limit)
    
    return query.all()

def search_incidents_by_area(
    db: Session,
    polygon: str,  # GeoJSON polygon
    limit: int = 10
) -> List[Incident]:
    """
    Search for incidents within a specified geographical area.
    """
    # Parse the GeoJSON polygon
    geo_json = json.loads(polygon)
    
    # Convert to PostGIS geometry
    geom = ST_GeomFromGeoJSON(polygon)
    
    # Find incidents within the polygon
    query = db.query(Incident).filter(
        text("ST_Within(location, :geom)").params(geom=geom)
    ).limit(limit)
    
    return query.all()

def search_incidents_by_similarity(
    db: Session,
    description: str,
    limit: int = 10
) -> List[Incident]:
    """
    Search for incidents with similar descriptions using vector similarity.
    """
    # Generate embedding for the search query
    query_embedding = generate_embedding(description)
    
    # Perform similarity search using cosine distance
    query = db.query(Incident).order_by(
        text("description_embedding <-> :embedding").params(embedding=query_embedding)
    ).limit(limit)
    
    return query.all() 