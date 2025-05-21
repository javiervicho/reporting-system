from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.incident import (
    Incident,
    IncidentCreate,
    IncidentUpdate,
    IncidentSearchParams
)
from app.services.incident_service import (
    create_incident,
    get_incident,
    get_incidents,
    update_incident,
    delete_incident,
    search_incidents_by_proximity,
    search_incidents_by_area,
    search_incidents_by_similarity
)

router = APIRouter()

@router.post("/", response_model=Incident, status_code=201)
def create_new_incident(
    *,
    db: Session = Depends(get_db),
    incident_in: IncidentCreate,
) -> Any:
    """
    Create a new incident report.
    """
    return create_incident(db=db, incident_in=incident_in)

@router.get("/{incident_id}", response_model=Incident)
def read_incident(
    *,
    db: Session = Depends(get_db),
    incident_id: int,
) -> Any:
    """
    Get incident by ID.
    """
    incident = get_incident(db=db, id=incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.get("/", response_model=List[Incident])
def read_incidents(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    incident_type: Optional[str] = None,
) -> Any:
    """
    Retrieve incidents with optional filtering by type.
    """
    return get_incidents(db=db, skip=skip, limit=limit, incident_type=incident_type)

@router.put("/{incident_id}", response_model=Incident)
def update_incident_api(
    *,
    db: Session = Depends(get_db),
    incident_id: int,
    incident_in: IncidentUpdate,
) -> Any:
    """
    Update an incident.
    """
    incident = get_incident(db=db, id=incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return update_incident(db=db, db_obj=incident, obj_in=incident_in)

@router.delete("/{incident_id}", response_model=Incident)
def delete_incident_api(
    *,
    db: Session = Depends(get_db),
    incident_id: int,
) -> Any:
    """
    Delete an incident.
    """
    incident = get_incident(db=db, id=incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return delete_incident(db=db, id=incident_id)

@router.get("/search/proximity/", response_model=List[Incident])
def search_by_proximity(
    *,
    db: Session = Depends(get_db),
    latitude: float = Query(..., description="Latitude of the search center"),
    longitude: float = Query(..., description="Longitude of the search center"),
    radius: float = Query(..., description="Search radius in meters"),
    limit: int = 10,
) -> Any:
    """
    Search for incidents within a specified radius from a point.
    """
    return search_incidents_by_proximity(
        db=db, latitude=latitude, longitude=longitude, radius=radius, limit=limit
    )

@router.get("/search/area/", response_model=List[Incident])
def search_by_area(
    *,
    db: Session = Depends(get_db),
    polygon: str = Query(..., description="GeoJSON polygon defining the search area"),
    limit: int = 10,
) -> Any:
    """
    Search for incidents within a specified geographical area (GeoJSON polygon).
    """
    return search_incidents_by_area(db=db, polygon=polygon, limit=limit)

@router.get("/search/similar/", response_model=List[Incident])
def search_by_similarity(
    *,
    db: Session = Depends(get_db),
    description: str = Query(..., description="Description to find similar incidents"),
    limit: int = 10,
) -> Any:
    """
    Search for incidents with similar descriptions using vector similarity.
    """
    return search_incidents_by_similarity(db=db, description=description, limit=limit) 