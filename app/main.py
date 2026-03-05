"""
FastAPI app for Crawl MVP: serve UI and /api/generate.
Run from repo root: DATA_DIR=. uvicorn app.main:app --reload --app-dir app
Or from app/: uvicorn main:app --reload
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

try:
    from .pipeline import run_pipeline
except ImportError:
    from pipeline import run_pipeline

app = FastAPI(title="Incident Status Draft (Crawl MVP)")

# Serve static files from ./static when present
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class GenerateRequest(BaseModel):
    update_type: str = "Resolved"


@app.get("/", response_class=HTMLResponse)
def index():
    """Serve the single-page UI."""
    path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return """
    <html><body>
    <h1>Incident Status Draft</h1>
    <p>Place <code>index.html</code> in <code>app/static/</code> and restart.</p>
    <p>API: POST <code>/api/generate</code> with body <code>{"update_type": "Resolved"}</code></p>
    </body></html>
    """


@app.post("/api/generate")
def generate(req: GenerateRequest):
    """Run pipeline and return internal_summary, sources_used, draft."""
    update_type = (req.update_type or "Resolved").strip() or "Resolved"
    if update_type not in ("Investigating", "Identified", "Monitoring", "Resolved"):
        update_type = "Resolved"
    result = run_pipeline(update_type=update_type)
    if result.get("error") and not result.get("draft"):
        raise HTTPException(status_code=500, detail=result["error"])
    return result
