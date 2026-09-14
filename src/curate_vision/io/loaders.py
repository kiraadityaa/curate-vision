from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image

from curate_vision.config import PipelineConfig
from curate_vision.schema import ImageItem
from curate_vision.utils import is_supported_image


def _discover_files(cfg: PipelineConfig) -> list[Path]:
    """Walk the input directory and yield supported image files."""
    root = cfg.input_dir
    if not root.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {root}")
    files: list[Path] = []
    for path in root.rglob("*") if cfg.recursive else root.glob("*"):
        if path.is_file() and is_supported_image(path, cfg.extensions_lower):
            files.append(path)
    return sorted(files)


def _load_one(path: Path) -> ImageItem:
    item = ImageItem(path=path, file_size=path.stat().st_size)
    with Image.open(path) as img:
        item.format = img.format or ""
        item.width, item.height = img.size
        img.verify()
    return item


def load_images(cfg: PipelineConfig) -> list[ImageItem]:
    """Load image metadata from the configured input directory.

    Corrupted files are flagged with ``flags=[\"corrupt\"]`` instead of
    raising, so partially broken datasets can still be processed.
    """
    items: list[ImageItem] = []
    for path in _discover_files(cfg):
        try:
            items.append(_load_one(path))
        except Exception:
            item = ImageItem(path=path, file_size=path.stat().st_size)
            item.flags.append("corrupt")
            items.append(item)
    return items


def file_sha256(path: Path, chunk_size: int = 1 << 20) -> str:
    """Compute a content hash; raises if the file cannot be read."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()