from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class LoadedPayload:
    source_path: Path
    copied_source_path: Path
    payload: dict[str, Any]


def load_source_payload(source_path: Path, artifacts_dir: Path) -> LoadedPayload:
    """Copy source JSON to artifacts and load from the copied file."""
    source = source_path.resolve()
    if not source.exists():
        raise FileNotFoundError(f"Source JSON file not found: {source}")

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    copied_source = artifacts_dir / "migration_source_copy.json"
    shutil.copy2(source, copied_source)

    with copied_source.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("Source JSON must contain an object at the root")

    return LoadedPayload(source_path=source, copied_source_path=copied_source, payload=payload)
