from __future__ import annotations

import sys
from pathlib import Path
import os

os.environ.pop("ALL_PROXY", None)
os.environ.pop("all_proxy", None)

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / 'src'
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from app.cli import main

if __name__ == '__main__':
    raise SystemExit(main())
