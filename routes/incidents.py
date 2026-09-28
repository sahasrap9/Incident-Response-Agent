from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models.incident import Incident
from schemas.incident import IncidentCreate, IncidentResponse, IncidentUpdate


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# GET all incidents + filtering
@router.get("/", response_model=list[IncidentResponse])
def get_incidents(
    status: str | None = None,
    severity: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Incident)

    if status:
        query = query.filter(Incident.status == status)
    if search:
        query = query.filter(
            Incident.title.ilike(f"%{search}%")
    )
    if severity:
        query = query.filter(Incident.severity == severity)

    return query.all()


# GET incident statistics
@router.get("/stats")
def get_incident_stats(db: Session = Depends(get_db)):
    total = db.query(Incident).count()

    open_count = db.query(Incident).filter(
        Incident.status == "open"
    ).count()

    resolved_count = db.query(Incident).filter(
        Incident.status == "resolved"
    ).count()

    return {
        "total": total,
        "open": open_count,
        "resolved": resolved_count
    }


# GET one incident
@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    return incident


# CREATE incident
@router.post("/", response_model=IncidentResponse)
def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db)
):
    new_incident = Incident(
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        service=incident.service
    )

    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)

    return new_incident


# UPDATE incident
@router.put("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: int,
    incident_update: IncidentUpdate,
    db: Session = Depends(get_db)
):
    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    if incident_update.status is not None:
        incident.status = incident_update.status

    if incident_update.root_cause is not None:
        incident.root_cause = incident_update.root_cause

    if incident_update.resolution is not None:
        incident.resolution = incident_update.resolution

    db.commit()
    db.refresh(incident)

    return incident


# DELETE incident
@router.delete("/{incident_id}")
def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    db.delete(incident)
    db.commit()

    return {
        "message": "Incident deleted successfully"
    }