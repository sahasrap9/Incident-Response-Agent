#!/usr/bin/env python3
"""
Builds the Person-4 dataset in the EXACT shape Person 1's log_incident() expects:

    incident_id, service, symptom, error_signature, root_cause,
    resolution_steps, runbook_used, outcome, resolved_by, timestamp      (all strings)

Outputs (in ./data):
  history_incidents.jsonl  - 8 historical incidents that EXTEND the 4 seeded ones (INC-1042/1055/1071/1088)
  live_demo.json           - the live demo scenarios: alert text to type + the incident to log when resolved

Run:  python build_dataset.py        (validates everything; exits with an error if a rule is broken)

Design (this is what makes memory visibly pay off):
  * payment-gateway: 3 post-deploy connection-pool incidents, time to fix 71 -> 34 -> 16 min (a learning curve).
    Early ones include FAILED attempts (scale DB, restart pods) so the agent learns what not to do.
  * INC-1042 (seeded) taught "raise the pool size". Demo S2 is a pool-exhaustion look-alike where that is WRONG
    (idle-in-transaction leak) -> agent is corrected -> S3 shows it applied the lesson.
  * auth-service TLS expiry twice, exactly 90 days apart -> next one due 2026-10-11 (predictive bonus).
No history incident mentions idle-in-transaction connections: the demo must teach that live.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data")

FIELDS = ["incident_id", "service", "symptom", "error_signature", "root_cause",
          "resolution_steps", "runbook_used", "outcome", "resolved_by", "timestamp"]
SERVICES = {"checkout-service", "payment-gateway", "auth-service", "inventory-service"}
SEEDED_IDS = {"INC-1042", "INC-1055", "INC-1071", "INC-1088"}

# ----------------------------------------------------------------------------------------------
# HISTORY (extends the 4 seeded incidents)
# ----------------------------------------------------------------------------------------------
HISTORY = [
    dict(
        incident_id="INC-1090", service="auth-service",
        symptom="Login and token refresh failing for all web and mobile clients for ~52 minutes; auth.meridiancommerce.com showing 'certificate expired' in browsers",
        error_signature="httpx.ConnectError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate has expired (_ssl.c:1006)",
        root_cause="TLS certificate for auth.meridiancommerce.com expired at 08:00 UTC; the ingress secret was pinned to a specific certificate version, so the renewed certificate in the vault was never picked up",
        resolution_steps="Issued a new certificate, stored it in the vault, updated the ingress TLS secret to the new version, restarted ingress-nginx pods, verified with `openssl s_client -connect auth.meridiancommerce.com:443` from 3 regions",
        runbook_used="TLS-Certificate-Rotation-Runbook",
        outcome="Resolved in 52 minutes, no data loss. Action item: move the ingress secret to auto-renewal (cert-manager)",
        resolved_by="Sana I.", timestamp="2026-04-14T08:02:00Z"),
    dict(
        incident_id="INC-1091", service="payment-gateway",
        symptom="POST /v1/payments/authorize returning HTTP 500/504 for ~71 minutes starting 14 minutes after release v2.15.0; readiness probes failing on 4 of 6 pods; database CPU normal at 34%",
        error_signature="sqlalchemy.exc.TimeoutError: QueuePool limit of size 10 overflow 5 reached, connection timed out, timeout 30.00 (Background on this error at: https://sqlalche.me/e/20/3o7r)",
        root_cause="Release v2.15.0 leaked database sessions: refund reconciliation path returned early without calling session.close(), so each pod exhausted its pool of 15 within minutes",
        resolution_steps="Tried scaling the RDS instance from 8 to 16 vCPU (no effect: pool limit is client-side); rolling restart of pods (errors returned within 7 minutes); finally correlated the alert with the deploy window and rolled back with `kubectl rollout undo deployment/payment-gateway -n payments`; recycled pods; confirmed pool utilisation below 40% for 15 minutes",
        runbook_used="Bad-Release-Rollback-Runbook",
        outcome="Resolved in 71 minutes after two failed attempts. Lesson: when errors begin within an hour of a deploy, roll back first",
        resolved_by="Priya N.", timestamp="2026-06-04T08:22:00Z"),
    dict(
        incident_id="INC-1092", service="checkout-service",
        symptom="Carts randomly emptying and users being signed out during checkout for ~38 minutes; p95 latency up from 180ms to 4.2s",
        error_signature="redis.exceptions.TimeoutError: Timeout reading from socket (used_memory 99.4% of maxmemory, evicted_keys=61,204/min)",
        root_cause="Cart session TTL was raised from 7 days to 30 days without resizing Redis; maxmemory-policy allkeys-lru began evicting live cart sessions",
        resolution_steps="Scaled the Redis instance from 6GB to 13GB, reverted cart session TTL to 7 days via config change, confirmed evicted_keys returned to 0 and p95 latency to under 250ms",
        runbook_used="Redis-Memory-Eviction-Runbook",
        outcome="Resolved in 38 minutes, ~1,900 carts lost, no orders affected",
        resolved_by="Meera N.", timestamp="2026-06-19T09:43:00Z"),
    dict(
        incident_id="INC-1093", service="inventory-service",
        symptom="Stock levels on product pages stale by 25+ minutes; inventory consumer stuck in a rebalance loop",
        error_signature="kafka.errors.CommitFailedError: Commit cannot be completed since the group has already rebalanced and assigned the partitions to another member. Time between subsequent calls to poll() was longer than max_poll_interval_ms (300000)",
        root_cause="Bulk stock-import messages took over 5 minutes to process, exceeding max_poll_interval_ms, so the broker kept evicting the consumer and triggering rebalances",
        resolution_steps="Raised max_poll_interval_ms from 300000 to 900000, reduced max_poll_records from 500 to 100, restarted the consumer group once, verified lag drained to zero in 14 minutes",
        runbook_used="Kafka-Consumer-Rebalance-Runbook",
        outcome="Resolved in 29 minutes, no stock data lost",
        resolved_by="Rahul V.", timestamp="2026-07-02T06:15:00Z"),
    dict(
        incident_id="INC-1094", service="auth-service",
        symptom="Login and token refresh failing for all clients for ~31 minutes; browsers and mobile apps reporting expired certificate for auth.meridiancommerce.com",
        error_signature="httpx.ConnectError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate has expired (_ssl.c:1006)",
        root_cause="Same as INC-1090: certificate expired 90 days after the previous rotation; ingress secret still pinned to a fixed certificate version and the cert-manager migration had not been done",
        resolution_steps="Followed TLS-Certificate-Rotation-Runbook: issued a new certificate, updated the ingress TLS secret, restarted ingress-nginx pods, verified handshake from 3 regions",
        runbook_used="TLS-Certificate-Rotation-Runbook",
        outcome="Resolved in 31 minutes. Recurring every 90 days. The action item to move to cert-manager auto-renewal is STILL OPEN; next expiry expected 2026-10-11",
        resolved_by="Sana I.", timestamp="2026-07-13T08:02:00Z"),
    dict(
        incident_id="INC-1095", service="payment-gateway",
        symptom="Payment authorisation failing with HTTP 500/504 for ~34 minutes, starting 11 minutes after release v2.16.1; checkout-service reporting upstream timeouts; database CPU normal",
        error_signature="sqlalchemy.exc.TimeoutError: QueuePool limit of size 10 overflow 5 reached, connection timed out, timeout 30.00 (Background on this error at: https://sqlalche.me/e/20/3o7r)",
        root_cause="Release v2.16.1 added an N+1 query in GET /v1/orders/{id}/summary: each request opened ~14 short-lived sessions, exhausting the pool under normal traffic",
        resolution_steps="Recognised the pattern from INC-1091 (errors starting shortly after a deploy plus pool timeouts); rolled back with `kubectl rollout undo deployment/payment-gateway -n payments`; recycled pods; confirmed pool utilisation under 40%. Did not scale the database",
        runbook_used="Bad-Release-Rollback-Runbook",
        outcome="Resolved in 34 minutes, no failed attempts this time",
        resolved_by="Arjun M.", timestamp="2026-07-16T09:48:00Z"),
    dict(
        incident_id="INC-1096", service="auth-service",
        symptom="Login latency rising from 220ms to 9s and intermittent HTTP 504 at the ingress for ~26 minutes after release v3.4.0",
        error_signature="[CRITICAL] WORKER TIMEOUT (pid:412) - gunicorn worker killed after 30s; kubectl top pods showing CPU at limit (1000m/1000m)",
        root_cause="Release v3.4.0 raised the bcrypt cost factor from 10 to 14 (about 16x more CPU per login); pods were CPU-throttled and gunicorn workers timed out",
        resolution_steps="Reverted bcrypt cost factor to 12 via config change (kept 12 as the compromise), rolled out with `kubectl rollout restart deployment/auth-service -n identity`, raised CPU limit from 1000m to 1500m as a stopgap",
        runbook_used="Auth-CPU-Regression-Runbook",
        outcome="Resolved in 26 minutes, no security impact",
        resolved_by="Kiran R.", timestamp="2026-08-05T07:30:00Z"),
    dict(
        incident_id="INC-1097", service="payment-gateway",
        symptom="Payment authorisation errors for ~16 minutes, starting 9 minutes after release v2.17.2; error rate peaked at 38%",
        error_signature="sqlalchemy.exc.TimeoutError: QueuePool limit of size 10 overflow 5 reached, connection timed out, timeout 30.00 (Background on this error at: https://sqlalche.me/e/20/3o7r)",
        root_cause="Release v2.17.2 added a retry decorator with no backoff or jitter; sessions stayed checked out while the database was briefly slow, exhausting the pool",
        resolution_steps="Matched to INC-1091 and INC-1095 within 2 minutes; rolled back immediately with `kubectl rollout undo deployment/payment-gateway -n payments`; recycled pods; opened a bug for retry backoff",
        runbook_used="Bad-Release-Rollback-Runbook",
        outcome="Resolved in 16 minutes. Third occurrence: on-call now rolls back first, root-causes second",
        resolved_by="Priya N.", timestamp="2026-09-03T10:30:00Z"),
]

# ----------------------------------------------------------------------------------------------
# LIVE DEMO (held out: do NOT seed these before the demo)
# ----------------------------------------------------------------------------------------------
LIVE = {
    "note": "Held-out live demo inputs. 'alert_text' is what you type/paste into the console. 'expected' is what a good run looks like. "
            "'log_on_resolve' is the incident the real 'mark resolved' flow should write via log_incident(). "
            "Rehearse the alert wording exactly; it is written to resemble seeded incidents so recall surfaces them.",
    "cold_start_baseline": {
        "use": "Run S1 with memory turned OFF (ask Person 2 for a flag) to show generic advice. There is only one shared bank, so an 'empty bank' is not available.",
        "expected_generic_answer": "Check database health, review recent logs, consider restarting pods or scaling the database. All of which failed in INC-1091."},
    "scenarios": [
        {"id": "S1", "title": "Deja vu after a deploy (recall wins)",
         "service": "payment-gateway", "fired_at": "2026-09-28T09:41:00Z",
         "alert_text": "payment-gateway: POST /v1/payments/authorize returning HTTP 500 and 504, error rate 47% over the last 5 minutes. Logs show sqlalchemy.exc.TimeoutError: QueuePool limit of size 10 overflow 5 reached, connection timed out, timeout 30.00. Release v2.18.0 finished deploying 19 minutes ago. Database CPU is normal.",
         "expected": {"recalls": ["INC-1091", "INC-1095", "INC-1097"],
                      "behaviour": "Connects the alert to the post-deploy pool-exhaustion pattern (3 prior incidents), recommends rolling back v2.18.0 first (`kubectl rollout undo deployment/payment-gateway -n payments`), and says scaling the database and restarting pods did NOT work in INC-1091."}},
        {"id": "S2", "title": "The confident wrong answer (agent gets corrected)",
         "service": "inventory-service", "fired_at": "2026-09-28T11:05:00Z",
         "alert_text": "inventory-service: requests failing with psycopg2.OperationalError: FATAL: remaining connection slots are reserved for non-replication superuser connections. No flash sale and no recent deploy, traffic is normal. Application pool is already set to 75.",
         "expected": {"recalls": ["INC-1042"],
                      "behaviour": "Agent matches INC-1042 (checkout-service pool exhaustion) and suggests raising the connection pool size. That is WRONG here: the pool was not the bottleneck, Postgres max_connections (100) was, because a nightly reconciliation job left ~60 connections 'idle in transaction'."},
         "correction_via_mark_resolved": "Engineer marks resolved and enters the real cause below; the app calls log_incident() with log_on_resolve.",
         "log_on_resolve": dict(
             incident_id="INC-1101", service="inventory-service",
             symptom="inventory-service requests failing for ~41 minutes with Postgres connection slots exhausted; traffic normal, no deploy, no promotion",
             error_signature="psycopg2.OperationalError: FATAL: remaining connection slots are reserved for non-replication superuser connections (max_connections=100)",
             root_cause="Nightly stock-reconciliation job left ~60 connections in 'idle in transaction' state (missing commit/rollback on its error path). This is NOT a pool-size problem: raising the application pool from 75 to 150 made it worse by hitting Postgres max_connections faster",
             resolution_steps="Found leaked sessions with `SELECT pid, state, query_start FROM pg_stat_activity WHERE state = 'idle in transaction'`; terminated them with pg_terminate_backend(pid); set idle_in_transaction_session_timeout = '60s'; fixed the missing rollback in the reconciliation job; reverted the pool size to 75. Do NOT raise the pool size when traffic is normal and connections are idle in transaction",
             runbook_used="DB-Connection-Pool-Exhaustion-Runbook (does not apply here; pool size was not the cause)",
             outcome="Resolved in 41 minutes. First attempt (raising pool 75 -> 150) made it worse. Correct diagnosis: check pg_stat_activity for idle-in-transaction sessions BEFORE changing pool size",
             resolved_by="Arjun M.", timestamp="2026-09-28T11:52:00Z")},
        {"id": "S3", "title": "One week later: the agent applies the lesson",
         "service": "checkout-service", "fired_at": "2026-10-05T10:12:00Z",
         "alert_text": "checkout-service: HTTP 502s on /api/checkout, logs show psycopg2.OperationalError: FATAL: remaining connection slots are reserved for non-replication superuser connections. Traffic is normal, no deploy today, connection pool is not saturated on the application side.",
         "expected": {"recalls": ["INC-1101", "INC-1042"],
                      "behaviour": "Agent does NOT recommend raising the pool size. It cites INC-1101, asks the engineer to check pg_stat_activity for 'idle in transaction' sessions first, and proposes idle_in_transaction_session_timeout."}},
        {"id": "S3_fallback", "title": "Use instead of S3 if the agent scopes recall to one service (see DEMO_SCRIPT)",
         "service": "inventory-service", "fired_at": "2026-10-05T10:12:00Z",
         "alert_text": "inventory-service: HTTP 500s on /api/stock/reserve, logs show psycopg2.OperationalError: FATAL: remaining connection slots are reserved for non-replication superuser connections. Traffic is normal, no deploy today, application pool is not saturated.",
         "expected": {"recalls": ["INC-1101"],
                      "behaviour": "Same as S3, on the same service the correction was tagged with, so a service-scoped recall still finds INC-1101."}},
        {"id": "S4_bonus", "title": "Predictive: the certificate will expire again (optional, 20 sec)",
         "service": "auth-service", "fired_at": "2026-10-01T04:00:00Z",
         "alert_text": "Anything we should worry about in the next two weeks?",
         "expected": {"recalls": ["INC-1090", "INC-1094"],
                      "behaviour": "Agent notices two TLS expiries exactly 90 days apart (2026-04-14, 2026-07-13), projects the next to 2026-10-11, and flags that the cert-manager auto-renewal action item is still open."}},
    ],
}


def validate():
    errs, seen = [], set()
    rows = list(HISTORY) + [s["log_on_resolve"] for s in LIVE["scenarios"] if "log_on_resolve" in s]
    for r in rows:
        iid = r.get("incident_id", "?")
        if list(r.keys()) != FIELDS:
            errs.append(f"{iid}: fields must be exactly {FIELDS} in order, got {list(r.keys())}")
        for k, v in r.items():
            if not isinstance(v, str) or not v.strip():
                errs.append(f"{iid}.{k}: must be a non-empty string")
        if r.get("service") not in SERVICES:
            errs.append(f"{iid}: invalid service {r.get('service')!r}")
        if not re.fullmatch(r"INC-\d{4}", iid) or iid in SEEDED_IDS or iid in seen:
            errs.append(f"{iid}: bad, duplicate or seeded incident id")
        seen.add(iid)
        if not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", r.get("timestamp", "")):
            errs.append(f"{iid}: timestamp must look like 2026-08-14T09:12:00Z")
    for s in LIVE["scenarios"]:
        if s["service"] not in SERVICES:
            errs.append(f"scenario {s['id']}: invalid service {s['service']!r}")
    for i in re.findall(r"INC-\d{4}", json.dumps(LIVE)):  # every cited ID must exist
        if i not in seen and i not in SEEDED_IDS:
            errs.append(f"live_demo cites unknown incident {i}")
    return errs


def main():
    errs = validate()
    if errs:
        print("VALIDATION FAILED:\n  " + "\n  ".join(errs))
        sys.exit(1)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "history_incidents.jsonl"), "w", encoding="utf-8") as f:
        for r in HISTORY:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(OUT, "live_demo.json"), "w", encoding="utf-8") as f:
        json.dump(LIVE, f, indent=2, ensure_ascii=False)
    print(f"OK: {len(HISTORY)} history incidents + {len(LIVE['scenarios'])} live scenarios written to {OUT}")


if __name__ == "__main__":
    main()
