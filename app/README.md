# Incident Status Draft — Crawl MVP

Web prototype for the PRD: **Ingest → Normalize → Synthesize → RAG (guidelines) → Draft → Review.**

## Run locally

1. **Install dependencies** (from repo root or from `app/`):
   ```bash
   pip install -r app/requirements.txt
   ```
2. **Set OpenAI API key** (required for the Draft step):
   ```bash
   export OPENAI_API_KEY=sk-...
   # or copy app/.env.example to app/.env and add OPENAI_API_KEY
   ```
3. **Start the server** (from **repo root**, i.e. the folder that contains `app/` and the incident data files):
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0
   ```
4. **Open in browser**: http://127.0.0.1:8000/

## Usage

- Choose **Update type** (Resolved / Investigating / Identified / Monitoring) and click **Generate draft**.
- Review **Internal summary** and **Sources used**, then edit the **Draft** (Title, Status, Message) if needed.
- Click **Copy to clipboard** to paste into your status page or ticket.

## Data

Reads from the parent directory of `app/`: `incident_context.txt`, `pagerduty_incident.json`, `cloudwatch_logs.json`, `prometheus_metrics.json`, `github_deployments.json`, `status_page_examples.md`. Set `DATA_DIR` to override.
