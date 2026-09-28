from pydantic import BaseModel, Field


class IncidentCreate(BaseModel):
    title: str
    description: str
    severity: str = Field(
    ...,
    pattern="^(low|medium|high|critical)$"
)
    service: str | None = None


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: str
    severity: str
    status: str
    service: str | None
    root_cause: str | None
    resolution: str | None

    class Config:
        from_attributes = True
class IncidentUpdate(BaseModel):
    status: str | None = None
    root_cause: str | None = None
    resolution: str | None = None