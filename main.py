import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.api.api import app
