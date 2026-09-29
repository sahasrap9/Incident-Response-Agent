# Demo Script — 2-Minute Walkthrough

## Hook (0:00–0:20)
> "This is our incident-response agent. It remembers every past outage we've solved — root causes, fixes, and the runbooks we used — so the next similar incident gets resolved faster."

## Existing incident memories (0:20–0:40)
> "Our memory bank already stores four past incidents:
> - `checkout-service`: Postgres connection pool exhausted during peak traffic at max_connections=20.
> - `payment-gateway`: Downstream processor rate-limiting our IP after retries with no backoff.
> - `auth-service`: Jwt signing key rotation deployed to 2 of 6 pods, causing mismatched keys.
> - `inventory-service`: In-memory cache with no eviction policy, growing unbounded during batch sync.
>
> Each memory records the symptom, error signature, root cause, resolution steps, and the runbook used. When something new happens, the agent searches this memory for the closest match instead of starting from zero."

## New incident (0:40–1:00)
> "New alert comes in:
> **checkout-service** is returning HTTP 502 for about 8 minutes during flash-sale traffic, and the app log shows `Postgres connection pool exhausted (max_connections=20 reached)`."

## Memory retrieval (1:00–1:20)
> "The agent searches Hindsight memory for similar past incidents. It returns our `checkout-service` incident: checkout requests returning HTTP 502 for ~8 minutes during peak traffic, caused by a Postgres connection pool sized for average load, not flash-sale burst traffic. The resolution already in memory: increase pool size from 20 to 75 and add a circuit breaker so requests fail fast instead of queueing infinitely."

## AI recommendation (1:20–1:40)
> "The agent passes the retrieved incident to the AI engine and gets a clear recommendation:
> **Increase the Postgres connection pool size from 20 to 75, add a circuit breaker to fail fast instead of queueing infinitely, and verify traffic-volume patterns before the next flash sale.**
>
> Not a generic fix—a memory-backed, past-confirmed action."

## Why it matters (1:40–2:00)
> "That means on-call engineers stop guessing. A live incident gets linked to a past incident with a proven fix, so we move from alert to correction faster, and the team gets smarter with every incident."

## On-screen commands (demo run)
```bash
# Require: real values for HINDSIGHT_BASE_URL, HINDSIGHT_API_KEY, GROQ_API_KEY in .env
python scripts/seed_hindsight.py
python scripts/run_demo.py LIVE-1
```

## Critical status
Verified working end to end against the live Hindsight and Groq APIs:
- Hindsight memory bank `meridian-commerce-incidents` holds the four seeded incidents and returns relevant matches for a new alert.
- The retrieved context is passed to Groq (`openai/gpt-oss-120b`), which returns a live recommendation grounded in the prior incidents.

Optional: set `GROQ_MODEL` in `.env` to use a different Groq model.
