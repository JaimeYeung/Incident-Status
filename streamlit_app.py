"""
Streamlit UI for Incident Status Draft — Crawl MVP.
Reuses app/pipeline.py for Ingest → Normalize → Synthesize → RAG → Draft.
"""
import os
import sys

import streamlit as st

# Make app/ importable when running from repo root
sys.path.insert(0, os.path.dirname(__file__))
from app.pipeline import ingest, normalize, synthesize, load_guidelines, draft as generate_draft


def get_api_key() -> str:
    """Resolve OpenAI API key: Streamlit secrets → env var."""
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        return os.environ.get("OPENAI_API_KEY", "")


# ─── Page config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Incident Status Draft",
    page_icon=None,
    layout="centered",
)

# ─── Header ──────────────────────────────────────────────────────────────────

st.title("Incident Status Draft")
st.caption(
    "Crawl MVP · Ingest → Normalize → Synthesize → RAG → Draft → Review"
)
st.divider()

# ─── Controls ────────────────────────────────────────────────────────────────

col1, col2 = st.columns([2, 1])
with col1:
    update_type = st.selectbox(
        "Status",
        ["Investigating", "Identified", "Monitoring", "Resolved"],
        help="Select the current incident status to draft an update for.",
    )
with col2:
    st.write("")
    st.write("")
    generate_btn = st.button("Generate draft", use_container_width=True, type="primary")

# ─── Main logic ──────────────────────────────────────────────────────────────

if generate_btn:
    api_key = get_api_key()
    if not api_key:
        st.error(
            "OPENAI_API_KEY is not set. Add it to Streamlit Secrets "
            "(`OPENAI_API_KEY = 'sk-...'`) or set the environment variable."
        )
        st.stop()

    os.environ["OPENAI_API_KEY"] = api_key

    with st.spinner("Ingesting data and generating draft…"):
        try:
            raw = ingest()
            evidence = normalize(raw)
            internal_summary = synthesize(evidence, raw)
            guidelines = load_guidelines()
            draft_out = generate_draft(guidelines, internal_summary, update_type)
            # Cache in session so edits survive re-runs
            st.session_state["result"] = {
                "internal_summary": internal_summary,
                "sources_used": evidence.get("sources_used", []),
                "draft": draft_out,
            }
        except Exception as e:
            st.error(f"Pipeline error: {e}")
            st.stop()

# ─── Results ─────────────────────────────────────────────────────────────────

if "result" in st.session_state:
    res = st.session_state["result"]

    # Internal Summary
    with st.expander("Internal Summary", expanded=True):
        st.info(res["internal_summary"])

    # Sources Used
    with st.expander("Sources Used", expanded=True):
        for src in res["sources_used"]:
            st.markdown(f"- {src}")

    # Draft
    st.subheader("Draft (edit if needed)")

    d = res["draft"]

    title_val = st.text_input("Title", value=d.get("title", ""))
    status_val = st.selectbox(
        "Status",
        ["Investigating", "Identified", "Monitoring", "Resolved"],
        index=["Investigating", "Identified", "Monitoring", "Resolved"].index(
            d.get("status", "Investigating")
        )
        if d.get("status") in ["Investigating", "Identified", "Monitoring", "Resolved"]
        else 0,
    )
    message_val = st.text_area("Message", value=d.get("message", ""), height=200)

    st.divider()

    # Formatted output ready to copy
    formatted = f"Title: {title_val}\nStatus: {status_val}\n\nMessage:\n{message_val}"
    st.caption("Copy-ready output:")
    st.code(formatted, language=None)
