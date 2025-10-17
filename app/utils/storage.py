from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from filelock import FileLock

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
UPLOADS_DIR = ASSETS_DIR / "uploads"


def ensure_dirs() -> None:
    """Ensure base directories exist."""
    for folder in (DATA_DIR, ASSETS_DIR, UPLOADS_DIR):
        folder.mkdir(parents=True, exist_ok=True)


def _lock_path(path: Path) -> Path:
    return path.with_suffix(path.suffix + ".lock")


def load_json(path: Path) -> Any:
    ensure_dirs()
    lock = FileLock(str(_lock_path(path)))
    with lock:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    ensure_dirs()
    lock = FileLock(str(_lock_path(path)))
    with lock:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def uuid_str() -> str:
    import uuid

    return str(uuid.uuid4())


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


__all__ = [
    "BASE_DIR",
    "DATA_DIR",
    "ASSETS_DIR",
    "UPLOADS_DIR",
    "ensure_dirs",
    "load_json",
    "save_json",
    "uuid_str",
    "now_iso",
]
