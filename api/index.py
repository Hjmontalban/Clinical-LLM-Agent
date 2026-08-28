import sys
from pathlib import Path

# Vercel Python entrypoint — import FastAPI app from backend package
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.main import app  # noqa: E402
