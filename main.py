from fastapi import FastAPI
from database import Base, engine
from models.incident import Incident
from routes.incidents import router as incident_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Incident Response Agent API")

app.include_router(incident_router)


@app.get("/")
def home():
    return {
        "message": "Incident Response Agent Backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }