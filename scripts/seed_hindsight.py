import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.memory.hindsight_tools import ensure_bank_exists, log_incident

ensure_bank_exists()

incidents = [
    dict(
        incident_id="INC-1042",
        service="checkout-service",
        symptom="Checkout requests returning HTTP 502 for ~8 minutes during peak traffic",
        error_signature="psycopg2.OperationalError: connection pool exhausted (max_connections=20 reached)",
        root_cause="Postgres connection pool sized for average load, not burst traffic from flash-sale campaign",
        resolution_steps="Increased pool size from 20 to 75, added a circuit breaker to fail fast instead of queueing infinitely",
        runbook_used="DB-Connection-Pool-Exhaustion-Runbook",
        outcome="Resolved in 22 minutes, no data loss",
        resolved_by="Priya N.",
        timestamp="2026-08-14T09:12:00Z",
    ),
    dict(
        incident_id="INC-1055",
        service="payment-gateway",
        symptom="15% of payment confirmations timing out, customers seeing 'payment pending' indefinitely",
        error_signature="httpx.ReadTimeout calling api.stripeclone.com/v1/charges after 30s",
        root_cause="Downstream payment processor began rate-limiting our IP after a burst of retries with no backoff",
        resolution_steps="Implemented exponential backoff with jitter and a dead-letter retry queue for failed charges",
        runbook_used="External-API-Rate-Limit-Runbook",
        outcome="Resolved in 40 minutes, all pending charges reconciled within the hour",
        resolved_by="Marcus T.",
        timestamp="2026-08-22T14:03:00Z",
    ),
    dict(
        incident_id="INC-1071",
        service="auth-service",
        symptom="Spike in 401 Unauthorized errors across mobile clients",
        error_signature="jwt.InvalidSignatureError: signature verification failed",
        root_cause="JWT signing key rotation deployed to 2 of 6 pods before rollout was paused, causing mismatched keys",
        resolution_steps="Rolled back the partial deployment, synced signing key across all pods, added a key-consistency healthcheck",
        runbook_used="Key-Rotation-Rollback-Runbook",
        outcome="Resolved in 18 minutes",
        resolved_by="Priya N.",
        timestamp="2026-09-02T03:47:00Z",
    ),
    dict(
        incident_id="INC-1088",
        service="inventory-service",
        symptom="Pods repeatedly OOMKilled during nightly batch sync",
        error_signature="Kubernetes event: OOMKilled, container exceeded 512Mi memory limit",
        root_cause="In-memory cache had no eviction policy, grew unbounded during large nightly SKU sync",
        resolution_steps="Added LRU eviction policy with a size cap, raised memory limit to 1Gi as a buffer, added a memory alert at 80%",
        runbook_used="Memory-Leak-Triage-Runbook",
        outcome="Resolved in 55 minutes, recurred once more before the eviction fix, then stable",
        resolved_by="Devika R.",
        timestamp="2026-09-10T02:15:00Z",
    ),
]

for incident in incidents:
    log_incident(**incident)
    print(f"Logged {incident['incident_id']} ({incident['service']})")

print("\nDone. Memory bank seeded with 4 historical incidents.")
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.memory.hindsight_tools import ensure_bank_exists, log_incident

ensure_bank_exists()

incidents = [
    dict(
        incident_id="INC-1042",
        service="checkout-service",
        symptom="Checkout requests returning HTTP 502 for ~8 minutes during peak traffic",
        error_signature="psycopg2.OperationalError: connection pool exhausted (max_connections=20 reached)",
        root_cause="Postgres connection pool sized for average load, not burst traffic from flash-sale campaign",
        resolution_steps="Increased pool size from 20 to 75, added a circuit breaker to fail fast instead of queueing infinitely",
        runbook_used="DB-Connection-Pool-Exhaustion-Runbook",
        outcome="Resolved in 22 minutes, no data loss",
        resolved_by="Priya N.",
        timestamp="2026-08-14T09:12:00Z",
    ),
    dict(
        incident_id="INC-1055",
        service="payment-gateway",
        symptom="15% of payment confirmations timing out, customers seeing 'payment pending' indefinitely",
        error_signature="httpx.ReadTimeout calling api.stripeclone.com/v1/charges after 30s",
        root_cause="Downstream payment processor began rate-limiting our IP after a burst of retries with no backoff",
        resolution_steps="Implemented exponential backoff with jitter and a dead-letter retry queue for failed charges",
        runbook_used="External-API-Rate-Limit-Runbook",
        outcome="Resolved in 40 minutes, all pending charges reconciled within the hour",
        resolved_by="Marcus T.",
        timestamp="2026-08-22T14:03:00Z",
    ),
    dict(
        incident_id="INC-1071",
        service="auth-service",
        symptom="Spike in 401 Unauthorized errors across mobile clients",
        error_signature="jwt.InvalidSignatureError: signature verification failed",
        root_cause="JWT signing key rotation deployed to 2 of 6 pods before rollout was paused, causing mismatched keys",
        resolution_steps="Rolled back the partial deployment, synced signing key across all pods, added a key-consistency healthcheck",
        runbook_used="Key-Rotation-Rollback-Runbook",
        outcome="Resolved in 18 minutes",
        resolved_by="Priya N.",
        timestamp="2026-09-02T03:47:00Z",
    ),
    dict(
        incident_id="INC-1088",
        service="inventory-service",
        symptom="Pods repeatedly OOMKilled during nightly batch sync",
        error_signature="Kubernetes event: OOMKilled, container exceeded 512Mi memory limit",
        root_cause="In-memory cache had no eviction policy, grew unbounded during large nightly SKU sync",
        resolution_steps="Added LRU eviction policy with a size cap, raised memory limit to 1Gi as a buffer, added a memory alert at 80%",
        runbook_used="Memory-Leak-Triage-Runbook",
        outcome="Resolved in 55 minutes, recurred once more before the eviction fix, then stable",
        resolved_by="Devika R.",
        timestamp="2026-09-10T02:15:00Z",
    ),
]

for incident in incidents:
    log_incident(**incident)
    print(f"Logged {incident['incident_id']} ({incident['service']})")

print("\nDone. Memory bank seeded with 4 historical incidents.")

client.close()