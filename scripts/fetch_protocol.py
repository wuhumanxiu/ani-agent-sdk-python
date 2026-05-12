"""Refresh the vendored ANI protocol contract from a local backend checkout."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BACKEND = ROOT.parent / "agent-native-im"
FILES = ["manifest.json", "openapi.yaml", "ws-events.schema.json"]


def main() -> None:
    source = DEFAULT_BACKEND / "docs" / "protocol"
    target = ROOT / "protocol"
    if not source.exists():
        raise SystemExit(f"protocol source not found: {source}")
    target.mkdir(exist_ok=True)
    for name in FILES:
        shutil.copy2(source / name, target / name)
        print(f"updated protocol/{name}")


if __name__ == "__main__":
    main()

