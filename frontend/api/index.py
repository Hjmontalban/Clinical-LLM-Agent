import sys
from pathlib import Path

# Vercel entrypoint when project Root Directory is set to frontend/
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from app.main import app  # noqa: E402
