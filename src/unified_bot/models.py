from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ParseResult:
    input_path: Path
    output_path: Path
    payload: dict[str, Any]


@dataclass(slots=True)
class ToolExecutionResult:
    name: str
    content: dict[str, Any]
