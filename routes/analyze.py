import os
from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(
    prefix="/analyze",
    tags=["Analyze"]
)


class AnalyzeRequest(BaseModel):
    logs: str


@router.get("/status")
def analyze_status():
    return {
        "ai_configured": bool(
            os.getenv("GROQ_API_KEY")
            and os.getenv("HINDSIGHT_BASE_URL")
            and os.getenv("HINDSIGHT_API_KEY")
        ),
        "message": (
            "AI memory integration is configured."
            if (
                os.getenv("GROQ_API_KEY")
                and os.getenv("HINDSIGHT_BASE_URL")
                and os.getenv("HINDSIGHT_API_KEY")
            )
            else
            "AI memory integration is waiting for environment configuration."
        )
    }


@router.post("/")
def analyze_incident(request: AnalyzeRequest):
    logs = request.logs.lower()

    if any(word in logs for word in ["kafka", "consumer", "rebalance", "queue", "lag"]):
        service = "dispatch-worker"
        root_cause = "Kafka consumer lag or rebalance is affecting message processing."
        suggested_fix = "Check consumer group health, partition assignment, and consumer lag."
        tags = ["kafka", "consumer-lag"]

    elif any(word in logs for word in ["postgres", "database", "deadlock", "transaction", "lock"]):
        service = "orders-db"
        root_cause = "Database contention or transaction locking is affecting requests."
        suggested_fix = "Check active transactions, locks, and database connection usage."
        tags = ["database", "locking"]

    elif any(word in logs for word in ["auth", "token", "jwt", "401", "403", "credential"]):
        service = "identity-edge"
        root_cause = "Authentication or authorization failure is affecting requests."
        suggested_fix = "Check token validation, credentials, and authentication service health."
        tags = ["auth", "authentication"]

    elif any(word in logs for word in ["search", "elastic", "index", "shard"]):
        service = "indexer-worker"
        root_cause = "Search indexing or shard processing is experiencing an issue."
        suggested_fix = "Check index health, shard status, and indexing queue."
        tags = ["search", "indexing"]

    else:
        service = "checkout-api"
        root_cause = "The incident requires further investigation from the available log signal."
        suggested_fix = "Review the surrounding logs, service health, and recent deployments."
        tags = ["investigation"]

    return {
        "service": service,
        "root_cause": root_cause,
        "suggested_fix": suggested_fix,
        "tags": tags,
        "confidence": 85
    }
@router.post("/ai")
def analyze_incident_with_ai(request: AnalyzeRequest):
    if not (
        os.getenv("GROQ_API_KEY")
        and os.getenv("HINDSIGHT_BASE_URL")
        and os.getenv("HINDSIGHT_API_KEY")
    ):
        return {
            "status": "not_configured",
            "message": "AI memory integration requires Hindsight and Groq environment configuration."
        }

    from src.memory.agent_orchestrator import analyze_alert

    result = analyze_alert(request.logs)

    return {
        "status": "success",
        "analysis": result
    }