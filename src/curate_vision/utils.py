from __future__ import annotations

from pathlib import Path

from curate_vision.config import PipelineConfig
from curate_vision.schema import ImageItem


def is_supported_image(path: Path, extensions: set[str]) -> bool:
    return path.suffix.lower() in extensions