# Incident-Response-Agent

An AI on-call assistant that **remembers every past incident** and uses that history to help engineers diagnose and resolve new ones faster. Built on [Hindsight](https://github.com/vectorize-io/hindsight) for long-term agent memory and [Groq](https://groq.com) for fast LLM inference.

Most incident tools forget. Postmortems get filed and buried, and the same failure returns months later with a different engineer on call. This agent retains each incident as structured memory, recalls similar past cases when something breaks, and consolidates everything into a living "reliability profile" that improves as more incidents are logged.

## How It Works

```
 New alert ──► Agent (Groq LLM) ──► recall_similar_incidents ──► Hindsight memory bank
                    │                                                  ▲
                    ▼                                                  │
        Briefing: likely root cause,            log_incident (write-back after resolution)
        past fixes, risky actions, first checks
```

1. **Recall**: when an incident starts, the agent searches memory for semantically similar past incidents, optionally scoped to one service.
2. **Brief**: it returns a concise briefing covering likely root causes, mitigations that worked, actions to avoid, and first checks for the on-call engineer.
3. **Retain**: once resolved, the incident is written back to memory so the next recall is smarter.
4. **Consolidate**: a team-wide mental model, the *Team-wide Production Reliability Profile*, distills recurring failure patterns, service dependencies, and warning signals across all incidents.

## Memory Architecture

| Decision | Choice |
|---|---|
| Bank strategy | One shared bank (`meridian-commerce-incidents`) for the whole company, enabling cross-service pattern recall |
| Scoping | Memories tagged by service (e.g. `checkout-service`) at write time; recall can run team-wide or tag-filtered |
| Content | Incidents and canonical runbooks live in the same bank |
| Mental model | One team-wide model, refreshed on demand so refresh timing is controlled (a production setup would refresh automatically after consolidation) |

The demo scenario is a fictional company, **Meridian Commerce**, with four services: `checkout-service`, `payment-gateway`, `auth-service`, and `inventory-service`. Historical incidents are synthetic but realistic, with detailed symptoms, root causes, and resolutions.

## Project Structure

```
├── demo/                  # Demo experience for the agent
├── scripts/
│   ├── test_connection.py             # Verify Hindsight + Groq connectivity
│   ├── seed_hindsight.py              # Load historical incidents into the bank
│   ├── test_recall.py                 # Try similarity recall on sample queries
│   ├── setup_mental_model.py          # Create the team-wide mental model
│   └── refresh_and_view_mental_model.py  # Refresh and print consolidated patterns
├── src/memory/
│   ├── schema.py          # Bank ID and incident-to-memory formatting
│   ├── hindsight_tools.py # log_incident, recall_similar_incidents, get_incident_briefing, Groq tool definitions
│   └── mental_model.py    # Create, find, refresh, and read the mental model
├── requirements.txt
└── LICENSE
```

## Getting Started

**Prerequisites:** Python 3.10+, a Hindsight account/API key, and a Groq API key.

```bash
git clone https://github.com/sahasrap9/Incident-Response-Agent.git
cd Incident-Response-Agent
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root with your credentials:

```
GROQ_API_KEY=your_groq_key
HINDSIGHT_API_KEY=your_hindsight_key
```

Then set up and explore the memory layer:

```bash
python scripts/test_connection.py                 # 1. confirm everything is reachable
python scripts/seed_hindsight.py                  # 2. seed historical incidents
python scripts/test_recall.py                     # 3. query similar incidents
python scripts/setup_mental_model.py              # 4. create the reliability profile
python scripts/refresh_and_view_mental_model.py   # 5. consolidate and view patterns
```

## Tech Stack

- **Memory:** Hindsight (`hindsight-client`), covering retain, recall, and mental models
- **LLM inference:** Groq, using tool calling for memory access
- **Language:** Python, with `python-dotenv` for configuration
- **UI:** Streamlit

## License

Released under the [MIT License](LICENSE).
