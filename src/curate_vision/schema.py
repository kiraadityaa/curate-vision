from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class ImageItem:
    """Metadata for a single image flowing through the pipeline."""

    path: Path
    width: int = 0
    height: int = 0
    format: str = ""
    file_size: int = 0
    blur_score: float = 0.0
    phash: str = ""
    dhash: str = ""
    flags: list[str] = field(default_factory=list)
    included: bool = True
    duplicate_of: Optional[str] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["path"] = str(self.path)
        return d