import sys
from pathlib import Path

# Ensure backend package is importable on Vercel
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app  # noqa: E402
