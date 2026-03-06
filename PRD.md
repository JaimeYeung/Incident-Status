# Product Requirements Document: AI-Enhanced Incident Management Communications

**Version:** 1.0  
**Status:** Draft  
**Author:** Take-Home Assignment

---

## 1. Key Assumptions

### 1.1 Current Process

- **Ownership:** Incident communications are owned by a mix of Technical Support and Engineers (incident commanders). Drafting and review are manual and can create bottlenecks.
- **Data sources:** Incident context already exists across PagerDuty, Slack (#incidents), CloudWatch, Prometheus, GitHub deployments, and similar tools. (*PagerDuty* = incident alerting and on-call lifecycle; *CloudWatch* = application logs and metrics, e.g. AWS; *Prometheus* = time-series metrics, e.g. latency and error rates.) These are used ad hoc during response, and there is no single “incident narrative” generated automatically.
- **Output:** External updates are published to Abnormal’s product status page (e.g. Statuspage.io). The format is consistent (Title, Status, Message) and follows internal guidelines and example (e.g. `status_page_examples.md`). The same structure applies across severity levels (SEV-0 through SEV-3); urgency affects timing and tone, not the update format.
- **Update cadence:** Internal guidance (e.g. initial update within 15–30 minutes, then every 30–60 minutes until resolved) exists but is often missed when drafting is manual.
- **Pain:** Under pressure, quality and consistency vary; there is risk of over-sharing internal details or under-communicating customer impact. Deriving “what to tell customers” from raw technical signals is time-consuming and error-prone.

### 1.2 Stakeholders

| Role | Need |
|------|------|
| **Incident Commander (Eng/SRE)** | Fast, accurate first draft so they can validate and publish instead of writing from scratch. |
| **Technical Support** | Consistent, on-brand messaging and clear customer impact so they can align customer conversations. |
| **Customers** | Clear, timely, honest updates (what’s affected, what we’re doing, when to expect resolution) without internal jargon. |

We assume routine status updates do not require separate approval from Comms or Leadership; the incident commander (or designated delegate) can publish after review.

### 1.3 Constraints

- **Human in the loop:** All customer-facing text must be reviewable and editable by a human before publish. AI assists and does not auto-publish.
- **Single source of truth:** PagerDuty (or equivalent) is the canonical source for incident lifecycle (trigger, acknowledge, resolve) and severity.
- **Data availability:** We assume read access to PagerDuty, Slack, CloudWatch, Prometheus, GitHub (or equivalent) within the incident response environment.
- **Data use for AI:** We assume incident data used for drafting (logs, metrics, Slack excerpts) is sanitized or anonymized as needed so it can be processed by the AI solution without exposing PII or sensitive customer data.
- **Latency:** We assume draft generation within roughly 1–2 minutes is acceptable. There is no sub-second real-time requirement.
- **Coordination cost:** We assume the workflow does not require synchronous sign-off or heavy back-and-forth between Incident Commander and Technical Support for each update. Async review or Commander-only publish is acceptable so that coordination time and cost stay low.
- **Data quirks:** We assume the provided incident dataset (and similar anonymized data) may have known ambiguities (e.g. timestamps labeled UTC but aligned to PT; recovery time in one source differing from another). We adopt a single, documented interpretation so that drafts are consistent; see **Section 4.3 Data Conventions**.

---

## 2. North Star Vision & Scope

### 2.1 North Star

**Within 10 minutes of incident acknowledgment, the incident commander has a customer-ready status page update draft (Investigating/Identified/Monitoring/Resolved) that requires only light edits, follows Abnormal’s tone, and contains zero internal-only details.**

### 2.2 Scope (In Scope for This Initiative)

- **Input:** Raw technical data for a single incident (logs, metrics, deployments, PagerDuty record, Slack excerpts).
- **Processing:** Normalize and synthesize this data into an internal “incident summary” (timeline, impact, root cause in one sentence, current status). Use that summary plus **retrieval over writing guidelines and examples** (RAG) to generate drafts.
- **Output:** Draft status page updates in the standard format (Title, Status, Message) that match Abnormal’s tone and structure (as in `status_page_examples.md`). Each draft is accompanied by (1) an **internal summary** (timeline, impact, root cause, status) visible to the commander and (2) **source references**: the list of data sources used to generate the draft (e.g. PagerDuty, Prometheus, CloudWatch, Slack, GitHub), so the commander can verify and correct. Crawl: document-level “Sources used” list; later phases may add per-claim attribution.
- **Interaction:** Web UI for “Generate draft” and “Review / Edit / Copy or Publish.” Commander can view internal summary and sources used alongside the draft. No automatic publishing; optional future integration with Status page API.

### 2.3 Out of Scope (Initial)

- Automatic publishing to the status page (human must approve).
- Automated severity classification or “should we post an update?” decisions.
- Cross-incident analytics or postmortem automation.
- Real-time ingestion from all sources (prototype can work on a snapshot of data, e.g. from a folder or API pull).

---

## 3. User Experience & User Stories

### 3.1 High-Level Flow

1. **Trigger:** Incident is created/acknowledged in PagerDuty (or user starts from a given incident ID).
2. **Ingest:** System pulls (or user provides) relevant logs, metrics, Slack, deployments for that incident and time window.
3. **Synthesize:** System produces a short internal summary (timeline, impact, root cause, status). Commander can view this summary in the UI.
4. **Generate draft:** User selects target update type (e.g. Investigating, Identified, Resolved). System retrieves relevant guidelines/examples (RAG) and generates a draft (Title + Status + Message) and records which data sources were used.
5. **Review:** User sees the draft, the internal summary, and the list of sources used for the draft; edits if needed, then copies to clipboard or (later) publishes via API.

### 3.2 User Stories

- **As an incident commander**, I want to click “Generate [update type]” so that I get a customer-ready draft I can review with only light edits and post, instead of writing from scratch.
- **As an incident commander**, I want to see the internal summary so that I understand what’s going on and can verify the draft is accurate before publishing.
- **As an incident commander**, I want to see the list of sources used for the draft (e.g. PagerDuty, Prometheus, CloudWatch) so that I can trust the facts and correct them if a source is wrong.
- **As an incident commander**, I want the draft to follow our status page tone and structure and contain zero internal-only details so that I don’t have to rewrite it for brand compliance.
- **As support**, I want status updates to describe customer impact clearly (e.g. “slower API response times”) so that I can align my replies with the status page.

---

## 4. Implementation Approach & Technical Design

### 4.1 Workflow Overview

```
Trigger → Ingest → Normalize → Synthesize → [RAG: Retrieve] → Draft → Review → Publish
    ↑                                                                              │
    └────── On new evidence or status change, re-run Synthesize → RAG → Draft ─────┘
```

- **Trigger:** PagerDuty webhook or manual “Generate update” for a given incident.
- **Ingest:** Fetch or read incident-related data (CloudWatch, Prometheus, GitHub, PagerDuty, Slack) for the incident time window and service(s).
- **Normalize:** Unify timestamps (e.g. to PT), schema, and identifiers; output a single “evidence” set.
- **Synthesize:** Rules + optional LLM summarize evidence into an **internal summary**: timeline, customer-observable impact, one-line root cause, current status. No customer-facing wording yet.
- **RAG Retrieve:** Query a vector store (or equivalent) with “update type + severity” (e.g. “Resolved, API performance, SEV-2”) to retrieve the most relevant **guideline and example chunks** from `status_page_examples.md` (and optionally past status updates). Do **not** expose internal evidence directly to customers.
- **Draft:** LLM receives (1) retrieved guidelines/examples and (2) internal summary + target status. It generates **Title**, **Status**, and **Message** in the same format as the examples. The system records which data sources were used to produce the draft (for source attribution).
- **Review:** Human sees the draft, the internal summary, and the list of sources used; edits and approves in a simple web UI.
- **Publish:** Copy to clipboard, or (future) call Status page API.

### 4.2 RAG Design

- **Corpus (prep, one-time or low-frequency):**
  - **Primary:** `status_page_examples.md` chunked by section (e.g. by `##` / `###`), or as a single chunk for MVP. Each chunk is embedded and stored in a vector store.
  - **Optional later:** Historical status updates chunked by incident type and update type for style consistency.
- **Query at draft time:** Constructed from target update type and severity (e.g. “Resolved update, API performance degradation, SEV-2”). Retrieve top-k chunks.
- **Prompt assembly:** System prompt = “Write a status page update following the guidelines and examples below.” Context = retrieved chunks. User prompt = internal summary + target status. Output = Title, Status, Message.
- **Why RAG:** Keeps the model anchored to the exact format and tone of the examples; makes it easy to add more guideline docs or past updates later without changing code.

### 4.3 Data Conventions

- **Timestamps:** Stored data may be labeled UTC (`Z`) but in the provided dataset the values align with **Pacific Time** (e.g. `14:23Z` matches 2:23 PM PT in incident_context). For this prototype we **treat all such timestamps as PT** and display them as PT in customer-facing text (e.g. “2:23 PM PT”). Document this assumption in code or README to avoid confusion.
- **Recovery / resolved time:** If different sources disagree (e.g. PagerDuty resolved_at, Prometheus recovery, GitHub deployment time), use **PagerDuty + metrics** (or Slack narrative) for the customer-facing resolved time; treat GitHub deployment timestamp as deployment record time, not necessarily the moment customers saw recovery.
- **Multi-source consistency (Walk/Run):** When multiple sources give different times for the same kind of event (e.g. GitHub “deployment at 3:45” vs metrics “recovery at 3:00”), define a **single source of truth per event type** and document it (e.g. in this PRD or a runbook): (1) **When did customers stop being impacted?** → Metrics (e.g. Prometheus) or Slack/narrative; (2) **When was the incident formally closed?** → PagerDuty; (3) **When was a deployment recorded?** → GitHub (use for “what” happened, not as the primary “when” for customer-facing resolution). In code, use the authoritative source for each field; use other sources only as context (e.g. “Rollback deployed; service recovered by ~3:00 PM PT per metrics”). When sources disagree, optionally **cross-check and flag** (e.g. log or surface in internal summary) so the convention can be tuned in Run.
- **Customer impact:** Never pre-assumed. Derived from evidence (e.g. “p99 latency spike” → “slower API response times”; “connection pool exhausted” → not stated; “500 errors” → “intermittent errors” or “some requests may fail”).
- **Handling missing fields:** All ingest and normalize steps should tolerate missing or optional fields (e.g. `diff_snippet`, partial Slack threads).
- **Source attribution:** Every draft must be traceable to the data sources used to generate it. At minimum, show a **“Sources used”** list (e.g. PagerDuty incident PXXX123, Prometheus api-gateway 14:20–15:00, CloudWatch api-gateway logs, Slack #incidents, GitHub deployments). Crawl: document-level list only. Walk/Run: optional per-claim or per-sentence attribution in UI.

### 4.4 Prototype Scope (MVP)

- **Input:** Read incident data from the provided folder (JSON + `incident_context.txt`) instead of live APIs.
- **Synthesize:** Rule-based or simple LLM pass over normalized data to produce internal summary (timeline, impact, status).
- **RAG:** Load `status_page_examples.md` (whole doc as one chunk is acceptable); optionally implement chunking + vector store for “Resolved” (and one other) update type.
- **Draft:** One LLM call with guidelines + internal summary → Title + Status + Message for the chosen update type (e.g. Resolved). Record which ingested sources were used (for “Sources used” list).
- **Review:** Web page that displays the draft, the internal summary, and the list of sources used; allows editing; offers “Copy to clipboard” (publish step can be manual paste to status page).
- **Output format:** Matches `status_page_examples.md` (Title, Status, Message; no internal details). Draft is accompanied by internal summary and “Sources used” list.

---

## 5. Phased Rollout (Crawl, Walk, Run)

| Phase | Goal | Capabilities |
|-------|------|--------------|
| **Crawl** | Prove value with minimal surface area. | Single incident data source (e.g. folder or one PagerDuty + one log source). Synthesize → Draft (Resolved only). Whole `status_page_examples.md` in prompt or as single RAG chunk. Web UI: “Load data → Generate draft → Edit → Copy.” No auto-publish. |
| **Walk** | Integrate into real workflow and multiple update types. | Ingest from PagerDuty + CloudWatch + Prometheus + Slack (or equivalents). Support all update types (Investigating, Identified, Monitoring, Resolved). **Data:** Formalize **single source of truth per event type** (e.g. customer impact end = metrics; formal close = PagerDuty; deployment = GitHub for “what” not “when”); implement in Normalize/Synthesize; **cross-check when sources disagree** and flag or surface in internal summary. **RAG:** Once guidelines or examples grow (longer doc, multiple playbooks, or historical status updates), use **chunked RAG**—chunk by section, embed, retrieve top-k by update type/severity—so only the most relevant guidance is used per draft. Optional past-incident updates in corpus for style consistency. “Generate draft” triggered from Slack or PagerDuty. Review UI + optional Status page API publish. |
| **Run** | Scale and improve quality. | More data sources and regions. **Data:** Validate and tune source-of-truth rules (e.g. from “accepted vs edited” drafts); auto-resolve or escalate when conflicts persist. **RAG:** Larger corpus (detailed playbooks, many past examples); tune chunking and retrieval (e.g. hybrid search, per-claim attribution) for draft quality. Optional “evidence RAG” when incident payload is large. A/B or shadow mode for draft quality. Feedback loop (accepted vs edited drafts) to tune prompts and retrieval. |

---

## 6. Success Metrics & Evaluation Framework

### 6.1 Operational Metrics

- **Time to first draft:** From “Generate” click to draft displayed. Target: &lt; 60 seconds for Crawl.
- **Time to published update:** From incident acknowledge to first status page update. Target: reduction of 30%+ vs baseline (manual drafting).
- **Edit rate:** % of drafts published with no or minimal edits. Track to improve prompts and RAG.

### 6.2 AI Output Quality

- **Format compliance:** Draft includes Title, Status, Message and matches the structure in `status_page_examples.md`. Automated check on schema.
- **Tone and safety:** No internal-only terms (e.g. “connection pool,” “PR #12345,” “rds-prod-main”). Human review checklist; optionally LLM or keyword-based guardrail.
- **Accuracy:** Stated timeline and impact align with underlying data (e.g. start/end time, “API slower” vs metrics). Spot-check or sample review.
- **Source attribution:** Draft is traceable to ingested sources; at minimum a “Sources used” list is shown. No unsupported factual claims; commander can verify and correct.
- **Consistency:** Same incident + update type produces similar tone and structure across runs; compare multiple generations for the same inputs.

### 6.3 Evaluation Approach

- **Crawl:** Manual review of 10–20 drafts (different incidents/update types) against a rubric (format, tone, no internal leak, accuracy). Iterate on prompt and RAG.
- **Walk/Run:** Add automated format checks; periodic human sampling; track edit rate and time-to-publish. Optionally collect “approved as-is” vs “edited” to fine-tune or select models.

---

## 7. Summary

This PRD describes an AI-assisted workflow for status page updates: **Ingest → Normalize → Synthesize → RAG (guidelines/examples) → Draft → Human Review → Publish.** The goal: within 10 minutes of acknowledgment, the commander has a customer-ready draft (any update type) that needs only light edits, follows Abnormal’s tone, and contains zero internal-only details. The commander sees an **internal summary** and **source references** (“Sources used”) alongside each draft for trust and verification. The AI is used to (1) optionally summarize technical evidence into an internal summary and (2) generate customer-facing drafts grounded in Abnormal’s writing guidelines via RAG. Humans remain responsible for approval and publishing. The prototype validates the pipeline on provided incident data and produces drafts in the same format and style as `status_page_examples.md`.
