"""
Memory schema for the Incident Response Agent.

Hindsight stores freeform text and finds it later via semantic search —
it does not enforce a schema on you. Recall quality depends on how
consistently formatted that text is, so this file defines ONE template
every incident record follows.

Architecture decision (locked): ONE shared bank for the whole company,
with each memory tagged by service (see hindsight_tools.py). This is
Hindsight's own recommended "single bank with tags" pattern for
applications that need cross-entity reasoning (e.g. "does this checkout
failure relate to something that happened on payment-gateway?") while
still supporting per-service filtered views when needed.
"""

# One bank for the whole demo company's incident history. Combined with
# per-service tags (applied in hindsight_tools.py), this lets the agent
# reason across services AND drill into one service's history on demand.
BANK_ID = "meridian-commerce-incidents"


def format_incident_memory(
    incident_id: str,
    service: str,
    symptom: str,
    error_signature: str,
    root_cause: str,
    resolution_steps: str,
    runbook_used: str,
    outcome: str,
    resolved_by: str,
    timestamp: str,
) -> str:
    """
    Turns one resolved incident into a single structured text block for
    Hindsight to retain. Every field is explicitly labeled so a semantic
    search matches on the right part of the incident, regardless of
    whether the new alert resembles the symptom, the root cause, or the
    fix.
    """
    return f"""INCIDENT {incident_id} — {service}
Timestamp: {timestamp}
Symptom: {symptom}
Error signature: {error_signature}
Root cause: {root_cause}
Resolution steps taken: {resolution_steps}
Runbook used: {runbook_used}
Outcome: {outcome}
Resolved by: {resolved_by}
""".strip()