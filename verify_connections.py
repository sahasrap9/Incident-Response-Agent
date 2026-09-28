"""
Quick connectivity check -- run this BEFORE touching agent_orchestrator.py.
It isolates three things that can each fail independently:
  1. Does .env actually load and populate the env vars?
  2. Does the Hindsight client connect with those credentials?
  3. Does the Groq client connect, and what models are actually
     available on this API key (so we know the right GROQ_MODEL string)?

Place this file at the REPO ROOT (same level as main.py) and run:
    python verify_connections.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("1. Checking .env values loaded")
print("=" * 60)

hindsight_url = os.getenv("HINDSIGHT_BASE_URL")
hindsight_key = os.getenv("HINDSIGHT_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")

def show(name, value):
    if value:
        # Never print the full secret -- just enough to confirm it loaded.
        print(f"  {name}: FOUND (starts with '{value[:6]}...', length {len(value)})")
    else:
        print(f"  {name}: MISSING -- check your .env file and its location")

show("HINDSIGHT_BASE_URL", hindsight_url)
show("HINDSIGHT_API_KEY", hindsight_key)
show("GROQ_API_KEY", groq_key)

if not (hindsight_url and hindsight_key and groq_key):
    print("\nStopping here -- fix the missing .env value(s) above first.")
    raise SystemExit(1)

print("\n" + "=" * 60)
print("2. Checking Hindsight connectivity")
print("=" * 60)

try:
    from hindsight_client import Hindsight

    client = Hindsight(base_url=hindsight_url, api_key=hindsight_key)
    try:
        client.create_bank(bank_id="meridian-commerce-incidents", name="Meridian Commerce — Incident History")
        print("  Bank created successfully.")
    except Exception as e:
        # If the bank already exists, most Hindsight clients raise here --
        # that's actually a GOOD sign (means auth worked, bank was already made).
        print(f"  create_bank raised (likely 'already exists', which is fine): {e}")
    print("  Hindsight connectivity: OK")
except Exception as e:
    print(f"  Hindsight connectivity: FAILED -- {e}")

print("\n" + "=" * 60)
print("3. Checking Groq connectivity + listing available models")
print("=" * 60)

try:
    from groq import Groq

    groq_client = Groq(api_key=groq_key)
    models = groq_client.models.list()
    print("  Groq connectivity: OK")
    print("  Available models on this API key:")
    for m in models.data:
        print(f"    - {m.id}")
except Exception as e:
    print(f"  Groq connectivity: FAILED -- {e}")

print("\nDone.")