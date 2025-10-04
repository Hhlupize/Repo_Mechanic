import sys
from pathlib import Path

# Ensure the fixture package root is on sys.path so `from calc import ...` works
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

