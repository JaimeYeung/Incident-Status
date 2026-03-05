"""Config: data directory and API key. Data dir is parent of app/ so we read incident data from repo root."""
import os

# When running from app/, data files are in parent directory
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), ".."))
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
