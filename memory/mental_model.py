"""
Team-wide mental model for the Incident Response Agent.

A Hindsight mental model is a saved `reflect()` answer attached to a
bank, refreshed on demand (or automatically). This is the concrete
mechanism behind the "the agent gets smarter over time" demo moment --
as more incidents are logged, refreshing this model produces a richer,
more specific answer.

Decision (locked): refreshes MANUALLY, not automatically, so we control
exactly when it updates during a live demo. In a real production
deployment this would use trigger={"refresh_after_consolidation": True}
instead -- worth mentioning to judges as the intended production
behavior, separate from how we run it here.
"""

import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.memory.hindsight_tools import _client
from src.memory.schema import BANK_ID

MENTAL_MODEL_NAME = "Team-wide Production Reliability Profile"

SOURCE_QUERY = """What recurring production failure patterns has our operations team learned from approved runbooks and resolved incidents?

For each pattern, identify the services and dependencies involved, early warning signals, verified root causes, safe mitigations, risky actions to avoid, and the first checks an on-call engineer should perform. Prioritize repeated, high-severity, cross-service incidents and clearly label uncertain evidence.""".strip()


def create_team_mental_model():
    """Creates the team-wide mental model. Call this once (see helper below)."""
    result = _client.create_mental_model(
        bank_id=BANK_ID,
        name=MENTAL_MODEL_NAME,
        source_query=SOURCE_QUERY,
        max_tokens=2048,
        # No `trigger` here -- manual refresh only, by design (see docstring above).
    )
    print(f"Creating mental model (operation: {result.operation_id})")
    return result.operation_id


def find_team_mental_model():
    """Looks up the existing mental model by name, if it's already been created."""
    models = _client.list_mental_models(bank_id=BANK_ID)
    for model in models.items:
        if model.name == MENTAL_MODEL_NAME:
            return model
    return None


def create_or_get_team_mental_model():
    """Creates the mental model only if it doesn't already exist -- safe to re-run."""
    existing = find_team_mental_model()
    if existing:
        print(f"Mental model already exists: {existing.id}")
        return existing.id

    create_team_mental_model()
    # Creation is async -- wait briefly and look it up by name.
    for _ in range(10):
        time.sleep(2)
        model = find_team_mental_model()
        if model:
            return model.id
    raise TimeoutError("Mental model was created but did not appear within the wait window.")


def refresh_team_mental_model():
    """Manually re-runs the source query so the model reflects the latest incidents."""
    model = find_team_mental_model()
    if not model:
        raise ValueError("No mental model found -- run create_or_get_team_mental_model() first.")
    result = _client.refresh_mental_model(bank_id=BANK_ID, mental_model_id=model.id)
    print(f"Refreshing mental model (operation: {result.operation_id})")
    return result.operation_id


def get_team_mental_model_content(wait_for_refresh=True, timeout_seconds=30):
    """
    Fetches the mental model's current content. If a refresh was just
    triggered, content may briefly still show the previous version --
    pass wait_for_refresh=True to poll until it updates, up to timeout_seconds.
    """
    model = find_team_mental_model()
    if not model:
        raise ValueError("No mental model found -- run create_or_get_team_mental_model() first.")

    if not wait_for_refresh:
        return model.content

    previous_refreshed_at = model.last_refreshed_at
    waited = 0
    while waited < timeout_seconds:
        time.sleep(3)
        waited += 3
        model = _client.get_mental_model(bank_id=BANK_ID, mental_model_id=model.id)
        if model.last_refreshed_at != previous_refreshed_at:
            return model.content
    return model.content  # Return whatever's there if it didn't update in time.