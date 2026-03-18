from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from unified_bot.cli import main as cli_main


if __name__ == "__main__":
    args = sys.argv[1:] or ["chat"]
    raise SystemExit(cli_main(args))
