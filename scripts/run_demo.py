import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

from src.memory.hindsight_tools import recall_similar_incidents
from src.memory.hindsight_tools import close as hindsight_close
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

SYSTEM_PROMPT = """You are a senior incident response engineer for a commerce platform.
You are given a NEW live alert and the most relevant PAST incidents pulled from
long-term memory. Use the past incidents as precedent.

Reply with exactly these sections:
ASSESSMENT: one paragraph on what is happening.
MOST RELEVANT PRIOR INCIDENT: name the single past incident that best matches.
RECOMMENDED ACTIONS: 3-5 concrete, ordered steps grounded in what worked before.
RISKS / CAVEATS: what could go wrong or what to verify first.

Be specific. Never invent an incident id, error code, or number that is not in
the context you were given."""


def get_groq_recommendation(query: str, service: str | None, memories: list[str]) -> str:
    """Passes the live alert plus the memories Hindsight retrieved to Groq."""
    context = "\n\n".join(f"MEMORY {i}:\n{m}" for i, m in enumerate(memories, start=1))
    if not context:
        context = "(no prior incidents found in memory)"

    user_message = (
        f"NEW ALERT\nService: {service or 'unknown'}\nDescription: {query}\n\n"
        f"PAST INCIDENTS RETRIEVED FROM MEMORY\n{context}"
    )

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )
    return completion.choices[0].message.content


def run_scenario(query: str, service: str | None = None, retrieval_limit: int = 3):
    print("=" * 72)
    print("NEW INCIDENT ALERT")
    print("=" * 72)
    print(f"Service : {service or 'all services'}")
    print(f"Query   :\n{query}\n")

    print("-" * 72)
    print("STEP 1 - RETRIEVED HISTORICAL INCIDENTS")
    print("-" * 72)

    memories = recall_similar_incidents(
        alert_description=query,
        service=service,
        limit=retrieval_limit,
    )

    if not memories:
        print("No historical incidents found.")
    else:
        for i, text in enumerate(memories, start=1):
            print(f"\n[Match {i}]\n{text}")

    print("\n" + "-" * 72)
    print(f"STEP 2 - AI RECOMMENDATION (Groq {GROQ_MODEL})")
    print("-" * 72)

    try:
        recommendation = get_groq_recommendation(query, service, memories)
    except Exception as exc:
        print(f"Groq call failed: {type(exc).__name__}: {exc}")
        print("BLOCKER: GROQ_API_KEY missing/invalid or the Groq API is unreachable.")
        return

    print(recommendation)
    print("\n" + "=" * 72)


def main():
    path = os.path.join(os.path.dirname(__file__), "live_scenarios.json")
    with open(path, encoding="utf-8") as f:
        scenarios = json.load(f)

    if len(sys.argv) > 1:
        selected = next((s for s in scenarios if s["id"] == sys.argv[1]), None)
        if selected is None:
            print(f"Unknown scenario id: {sys.argv[1]}")
            print("Available:", ", ".join(s["id"] for s in scenarios))
            return
        scenarios = [selected]

    try:
        for scenario in scenarios:
            run_scenario(
                query=scenario["query"],
                service=scenario.get("service") or None,
            )
    finally:
        hindsight_close()


if __name__ == "__main__":
    main()
