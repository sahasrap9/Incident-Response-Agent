from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(
    prefix="/analyze",
    tags=["Analyze"]
)


class AnalyzeRequest(BaseModel):
    logs: str


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