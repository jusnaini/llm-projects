# Allow absolute imports like: from api.router import router
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent))
