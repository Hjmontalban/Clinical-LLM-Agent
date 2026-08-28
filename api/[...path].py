import sys
from pathlib import Path

# Catch-all Vercel Python entrypoint for /api/* subpaths (e.g. /api/research, /api/health)
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.main import app  # noqa: E402
