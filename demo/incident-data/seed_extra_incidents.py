#!/usr/bin/env python3
"""
Seeds the 8 extra historical incidents into the shared bank, using ONLY Person 1's log_incident()
(no direct Hindsight calls, no hardcoded bank name - per the memory cheat sheet).

Put this folder anywhere inside the repo (e.g. demo/incident-data/). It finds the repo root by itself.

  python seed_extra_incidents.py --dry-run          # print what would be logged, touch nothing
  python seed_extra_incidents.py --limit 2          # log just the first 2 (a cheap first test)
  python seed_extra_incidents.py                    # log all 8 (run ONCE - there is no duplicate check)
  python seed_extra_incidents.py --log-live S2      # FALLBACK ONLY: log the S2 correction by hand.
                                                    # In the real demo use the app's 'mark resolved' flow.

Needs your local .env (Hindsight + Groq keys). The .env is NOT in git - create it from .env.example first.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")


def find_repo_root(start):
    p = start
    while True:
        if os.path.exists(os.path.join(p, "src", "memory", "hindsight_tools.py")):
            return p
        parent = os.path.dirname(p)
        if parent == p:
            raise SystemExit("Could not find src/memory/hindsight_tools.py above this folder. "
                             "Copy incident-data/ inside the cloned repo first.")
        p = parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--log-live", metavar="SCENARIO_ID", help="fallback: log a live scenario's incident (e.g. S2)")
    ap.add_argument("--pause", type=float, default=1.0, help="seconds between calls")
    a = ap.parse_args()

    if a.log_live:
        with open(os.path.join(DATA, "live_demo.json"), encoding="utf-8") as f:
            sc = next(s for s in json.load(f)["scenarios"] if s["id"] == a.log_live)
        rows = [sc["log_on_resolve"]] if "log_on_resolve" in sc else []
        if not rows:
            raise SystemExit(f"{a.log_live} has no incident to log.")
    else:
        with open(os.path.join(DATA, "history_incidents.jsonl"), encoding="utf-8") as f:
            rows = [json.loads(l) for l in f if l.strip()]
        if a.limit:
            rows = rows[:a.limit]

    if a.dry_run:
        for r in rows:
            print(f"[dry-run] would log {r['incident_id']} ({r['service']}) {r['timestamp']}")
        print(f"{len(rows)} incident(s). Nothing was written.")
        return

    root = find_repo_root(HERE)
    sys.path.insert(0, root)
    try:
        from dotenv import load_dotenv  # optional; the repo may already load .env itself
        load_dotenv(os.path.join(root, ".env"))
    except ImportError:
        pass
    from src.memory.hindsight_tools import log_incident, ensure_bank_exists  # the ONLY way we talk to memory
    ensure_bank_exists()  # safe to call every run per hindsight_tools.py

    for n, r in enumerate(rows, 1):
        try:
            log_incident(**r)  # keyword args only, exactly the 10 schema fields
            print(f"[{n}/{len(rows)}] logged {r['incident_id']} ({r['service']})")
        except Exception as e:  # noqa: BLE001
            print(f"[{n}/{len(rows)}] FAILED {r['incident_id']}: {e}", file=sys.stderr)
            print("Stopped so you can fix the problem and avoid double-logging. "
                  f"Resume with --limit or remove the first {n - 1} rows.", file=sys.stderr)
            sys.exit(1)
        time.sleep(a.pause)
    print("done")


if __name__ == "__main__":
    main()
