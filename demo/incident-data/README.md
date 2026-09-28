# Incident data & demo kit (Person 4)

Extends the 4 seeded incidents (INC-1042, 1055, 1071, 1088) with 8 more, and defines the live demo inputs.
Follows the memory cheat sheet: valid service names only, no direct Hindsight calls, no hardcoded bank name.

```bash
python build_dataset.py                          # writes and validates data/*
python seed_extra_incidents.py --dry-run         # preview
python seed_extra_incidents.py --limit 2         # cheap first test against the real bank
python seed_extra_incidents.py                   # log all 8 (once!)
```

| File | Purpose |
|---|---|
| `build_dataset.py` | Source of truth for all data; validates the schema (10 string fields, valid service, unique IDs, ISO timestamps) |
| `data/history_incidents.jsonl` | 8 extra historical incidents, ready for `log_incident(**row)` |
| `data/live_demo.json` | Alert text to type live (S1-S3 + optional S4), expected agent behaviour, and the incident the 'mark resolved' flow should log |
| `seed_extra_incidents.py` | Seeds history through `log_incident()` only |
| `DEMO_SCRIPT.md` | 3-minute script and pre-flight checklist |

Planted patterns: payment-gateway post-deploy pool exhaustion (3x, 71 -> 34 -> 16 min); auth-service TLS expiry exactly 90 days apart (next 2026-10-11); one-offs on the other services. Not in history on purpose: idle-in-transaction connection leaks (taught live in S2).
