from __future__ import annotations

from pathlib import Path


def is_supported_image(path: Path, extensions: set[str]) -> bool:
    return path.suffix.lower() in extensions
