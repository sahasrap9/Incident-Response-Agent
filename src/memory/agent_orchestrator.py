"""
Agent orchestrator for the Incident Response Agent.

This is the piece that ties Groq's function-calling to the Hindsight
memory tools already built in hindsight_tools.py. Given an alert
description, it asks Groq what to do, executes any tool calls Groq
requests, and returns a final synthesized answer.

Standalone on purpose -- doesn't depend on FastAPI or any specific
route. Whoever does backend/frontend integration can import
`analyze_alert()` and call it from wherever makes sense (a new
endpoint, a background job, etc.).

Place this file at: src/memory/agent_orchestrator.py
(same folder as hindsight_tools.py, mental_model.py, schema.py)
"""

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv
from groq import Groq

from src.memory.hindsight_tools import (
    GROQ_TOOLS,
    ensure_bank_exists,
    get_incident_briefing,
    log_incident,
    recall_similar_incidents,
)

load_dotenv()

_groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Confirmed available on this API key via verify_connections.py, and
# supports tool-calling. Swap to "openai/gpt-oss-20b" if you need faster
# responses during the live demo (smaller model, less capable).
GROQ_MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """You are an incident response assistant for Meridian Commerce.
When given a new alert, decide whether you need to recall similar past
incidents from memory before answering. Use the recall_similar_incidents
tool when historical context would help diagnose the issue. Use
log_incident only when explicitly told an incident has just been
resolved and needs to be recorded. Always give a clear, actionable
answer citing what you found in memory, if anything."""

# Maps tool names Groq can call to the actual Python functions that run them.
_TOOL_DISPATCH = {
    "recall_similar_incidents": recall_similar_incidents,
    "log_incident": log_incident,
}


def _execute_tool_call(tool_call) -> str:
    """Runs the Python function matching a tool call Groq requested; returns a string result."""
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    if name not in _TOOL_DISPATCH:
        return f"Error: unknown tool '{name}'"

    try:
        result = _TOOL_DISPATCH[name](**args)
    except Exception as e:
        # Surface the error back to the model instead of crashing the
        # request -- lets Groq explain the failure gracefully to the user.
        return f"Error calling {name}: {e}"

    if name == "log_incident":
        return "Incident logged successfully."
    return json.dumps(result)


def analyze_alert(alert_description: str, service: str | None = None, max_tool_hops: int = 3) -> str:
    """
    Main entry point for the AI part. Give it a new alert's description
    (and optionally a service name); it returns a final text answer --
    having consulted Hindsight memory via tool calls if it decided to.

    This is what the integration teammate should call from wherever
    they wire it in (e.g. a new FastAPI endpoint like
    POST /incidents/{id}/analyze).
    """
    ensure_bank_exists()

    user_content = alert_description
    if service:
        user_content += f"\n\n(Service: {service})"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    for _ in range(max_tool_hops):
        try:
            response = _groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                tools=GROQ_TOOLS,
                tool_choice="auto",
            )
        except Exception as e:
            # Groq itself is down/erroring -- fail gracefully during the demo
            # instead of throwing a 500.
            return f"AI analysis unavailable right now (Groq error: {e}). Please check the incident manually."

        choice = response.choices[0].message

        if not choice.tool_calls:
            return choice.content

        # Groq wants to call one or more tools -- run them and feed the
        # results back so it can produce a final answer.
        messages.append(choice)
        for tool_call in choice.tool_calls:
            result_text = _execute_tool_call(tool_call)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result_text,
            })

    return "Reached tool-call limit without a final answer -- please investigate manually."


def log_resolved_incident(**kwargs) -> str:
    """
    Convenience wrapper for the integration teammate: call this when an
    incident's status changes to resolved, passing the fields
    format_incident_memory() needs: incident_id, service, symptom,
    error_signature, root_cause, resolution_steps, runbook_used,
    outcome, resolved_by, timestamp.
    """
    log_incident(**kwargs)
    return "Incident logged into Hindsight memory."


if __name__ == "__main__":
    # Quick manual smoke test -- run `python agent_orchestrator.py` to
    # sanity-check the whole loop before wiring it into anything.
    test_alert = "checkout-service returning HTTP 502 errors, latency spiking on database calls"
    print(analyze_alert(test_alert, service="checkout-service"))