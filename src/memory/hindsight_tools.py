"""
Thin wrapper around the Hindsight client, plus the Groq function-calling
tool definitions that let the LLM call these functions itself.
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv
from hindsight_client import Hindsight
from src.memory.schema import BANK_ID, format_incident_memory

load_dotenv()

_client = Hindsight(
    base_url=os.getenv("HINDSIGHT_BASE_URL"),
    api_key=os.getenv("HINDSIGHT_API_KEY"),
)


def ensure_bank_exists():
    """Creates the memory bank if it doesn't exist yet. Safe to call every run."""
    try:
        _client.create_bank(bank_id=BANK_ID, name="Meridian Commerce — Incident History")
    except Exception:
        pass  # Bank already exists — that's fine.


def log_incident(**kwargs) -> None:
    """
    Writes one resolved incident into memory, tagged by service. The tag
    is what lets recall_similar_incidents() later filter to just one
    service's history, while an untagged recall still searches everything.
    """
    content = format_incident_memory(**kwargs)
    _client.retain(
        bank_id=BANK_ID,
        content=content,
        tags=[kwargs["service"]],
    )


def recall_similar_incidents(alert_description: str, service: str = None, limit: int = 3):
    """
    Given a new alert, finds the most similar past incidents from memory.

    service=None -> searches the whole team-wide memory (cross-service
                    reasoning — this is the "connects the dots" story).
    service="checkout-service" -> scoped to just that service's history.
    """
    kwargs = {"bank_id": BANK_ID, "query": alert_description}
    if service:
        kwargs["tags"] = [service]
    result = _client.recall(**kwargs)
    return [r.text for r in result.results[:limit]]


def get_incident_briefing(alert_description: str, service: str = None) -> str:
    """
    Uses Hindsight's `reflect` to synthesize one readable briefing from
    everything memory knows relevant to this alert — this is the
    "senior engineer walks you through it" moment for the demo.
    """
    kwargs = {"bank_id": BANK_ID, "query": alert_description}
    if service:
        kwargs["tags"] = [service]
    response = _client.reflect(**kwargs)
    return response.text


# Tool schemas Groq uses to know these functions exist and how to call
# them. When Groq decides it needs memory, it returns a tool call with
# one of these names — your orchestrator (Person 2's job) catches that
# and calls the matching Python function above.
GROQ_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "recall_similar_incidents",
            "description": "Search memory for past incidents similar to the current alert.",
            "parameters": {
                "type": "object",
                "properties": {
                    "alert_description": {
                        "type": "string",
                        "description": "The current incident's symptoms/error message.",
                    },
                    "service": {
                        "type": "string",
                        "description": "Optional: limit search to one service's history.",
                    },
                },
                "required": ["alert_description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "log_incident",
            "description": "Store a newly resolved incident into long-term memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "incident_id": {"type": "string"},
                    "service": {"type": "string"},
                    "symptom": {"type": "string"},
                    "error_signature": {"type": "string"},
                    "root_cause": {"type": "string"},
                    "resolution_steps": {"type": "string"},
                    "runbook_used": {"type": "string"},
                    "outcome": {"type": "string"},
                    "resolved_by": {"type": "string"},
                    "timestamp": {"type": "string"},
                },
                "required": [
                    "incident_id", "service", "symptom", "error_signature",
                    "root_cause", "resolution_steps", "runbook_used",
                    "outcome", "resolved_by", "timestamp",
                ],
            },
        },
    },
]