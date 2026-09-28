# Demo script (target ~3:15) - Meridian Commerce Incident Response Agent

One-line story: **generic on day one, then it recalls, gets corrected, and applies the lesson.**
Inputs come from `data/live_demo.json`. Keep the word "hackathon" out of the video, title, description and on-screen text.

## Pre-flight (before recording)

1. `python build_dataset.py` then `python seed_extra_incidents.py` (once). Check the Hindsight dashboard: 4 seeded + 8 new incidents.
2. Create `.env` on the recording machine (it does not come with `git clone`).
3. Ask Person 2 for a **memory-off switch** for the cold-start clip (there is only one shared bank, so an "empty bank" is not possible). If not available, record the cold-start clip with memory tools disabled in the agent config.
4. Rehearse S1-S3 on the real integrated system at least twice. Type the alert text from `live_demo.json` EXACTLY; it is worded to resemble seeded incidents.
5. **Scoped vs unscoped recall.** Memories are tagged by service and `recall_similar_incidents(service=...)` filters on that tag. If the agent passes `service`, S2 will not surface INC-1042 (checkout-service) and S3 on checkout-service will not find the S2 correction (tagged inventory-service). Ask Person 2 to call recall WITHOUT `service` by default (cross-service is the design). If it cannot, use `S3_fallback` (same service) instead of S3.
6. Note the real agent answers and edit the "say" column below to match what it actually says.
7. Terminal font 18pt+, notifications off, 1080p, tabs ready: agent console, Hindsight dashboard.

## Timeline

| Time | Beat | On screen | Say (roughly, not verbatim) |
|---|---|---|---|
| 0:00-0:25 | Intro | Face cam, repo | "I'm [name]. When production breaks, the hard part isn't the logs, it's remembering how your team fixed this last time. We built an incident agent with persistent memory on Hindsight." |
| 0:25-0:55 | Problem (no memory) | Console with memory OFF, paste S1 alert | "Payment errors at 47%. With no memory it gives textbook advice: check the database, restart pods, scale up. All things this team already tried, and they failed." |
| 0:55-1:45 | Recall (S1) | Memory ON, paste the same S1 alert; show the 'past incidents cited' panel | "Same alert. Now it says: this matches three earlier incidents, all right after a deploy, all pool exhaustion. Roll back first. Scaling the database didn't work last time. That fix went from 71 minutes to 16 over those incidents." |
| 1:45-2:30 | Wrong, then corrected (S2) | Paste S2 (inventory-service). Agent suggests raising the pool. Click **Mark resolved** and enter the real cause | "It recalls a pool-exhaustion fix and suggests raising the pool. That's wrong this time: Postgres itself is out of connections because a nightly job left sessions idle in transaction. The engineer corrects it, and the app writes that as a new memory." Show the new incident (INC-1101) in the dashboard. |
| 2:30-3:00 | Learned (S3) | Paste S3 (checkout-service), framed as "a week later" | "Different service, same error. It no longer suggests a bigger pool. It cites the correction and tells us to check `pg_stat_activity` for idle-in-transaction sessions first." |
| 3:00-3:15 | Takeaway | Architecture slide or repo | "What surprised me: memory didn't just make answers faster, it stopped the agent repeating our mistakes. Link to the repo below." |

Optional 20 seconds if under time (S4_bonus): ask "Anything we should worry about in the next two weeks?" and the agent projects the 90-day TLS expiry to 2026-10-11.

If Person 1 can refresh the Team-wide Production Reliability Profile after the S2 correction, show the before/after profile as one more "it got smarter" moment. Confirm with them first that a refresh exists.

## Recording notes

- One take per scenario is fine; keep going after small mistakes, authenticity beats polish.
- If S2 or S3 goes off-script (agent answers differently), don't fake it: adjust the alert wording, not the agent.
- Thumbnail: Nano Banana (see the content guide), then post to YouTube as public.
