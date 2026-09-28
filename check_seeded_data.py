"""
Checks what's already in the Hindsight bank before we decide whether
seeding still needs to happen. Run from repo root:
    python check_seeded_data.py
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from src.memory.hindsight_tools import _client
from src.memory.schema import BANK_ID

# Broad, generic queries designed to surface whatever's in the bank,
# regardless of which service/incident it's about.
PROBE_QUERIES = [
    "incident",
    "error",
    "service outage",
    "database",
    "deployment",
]

seen = set()

print(f"Probing bank: {BANK_ID}\n")

for q in PROBE_QUERIES:
    result = _client.recall(bank_id=BANK_ID, query=q)
    for r in result.results:
        # Use the first line (INCIDENT ID + service) as a dedupe key.
        first_line = r.text.strip().splitlines()[0]
        if first_line not in seen:
            seen.add(first_line)
            print(f"- {first_line}")

print(f"\nTotal distinct incident records found: {len(seen)}")

# Also check for an existing mental model.
print("\nChecking for existing mental model(s)...")
models = _client.list_mental_models(bank_id=BANK_ID)
if models.items:
    for m in models.items:
        print(f"- '{m.name}' (id: {m.id}, last_refreshed_at: {m.last_refreshed_at})")
else:
    print("No mental models found yet.")