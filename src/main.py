from __future__ import annotations

import sys
from pathlib import Path
import os

os.environ.pop("ALL_PROXY", None)
os.environ.pop("all_proxy", None)

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from app.cli import main

if __name__ == '__main__':
    raise SystemExit(main())
