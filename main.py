from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from models.incident import Incident
from routes.incidents import router as incident_router
from routes.analyze import router as analyze_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Incident Response Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(incident_router)
app.include_router(analyze_router)


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
