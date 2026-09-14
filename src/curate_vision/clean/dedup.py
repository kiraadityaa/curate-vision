from __future__ import annotations

import imagehash
from PIL import Image

from curate_vision.config import PipelineConfig
from curate_vision.schema import ImageItem


def _phash_hex(item: ImageItem) -> str:
    with Image.open(item.path) as img:
        return str(imagehash.phash(img))


def _dhash_hex(item: ImageItem) -> str:
    with Image.open(item.path) as img:
        return str(imagehash.dhash(img))


def _hamming(a: str, b: str) -> int:
    return imagehash.hex_to_hash(a) - imagehash.hex_to_hash(b)


def _find_duplicate(phash: str, kept_buckets: dict[str, str], tolerance: int) -> str | None:
    for kept_hash in kept_buckets:
        if _hamming(phash, kept_hash) <= tolerance:
            return kept_buckets[kept_hash]
    return None


def deduplicate(items: list[ImageItem], cfg: PipelineConfig) -> list[ImageItem]:
    """Perceptual near-duplicate detection using pHash.

    Images are compared within ``dedup_tolerance`` Hamming bits. The first
    member of a duplicate group is kept; later members get
    ``duplicate_of=<kept path>`` and are excluded from exports.
    """
    hashes: list[tuple[ImageItem, str, str]] = []
    for item in items:
        if not item.included or "corrupt" in item.flags:
            continue
        try:
            ph = _phash_hex(item)
            dh = _dhash_hex(item)
        except Exception:
            item.flags.append("hash_error")
            item.included = False
            continue
        item.phash, item.dhash = ph, dh
        hashes.append((item, ph, dh))

    kept_buckets: dict[str, str] = {}
    for item, ph, _ in hashes:
        dup = _find_duplicate(ph, kept_buckets, cfg.dedup_tolerance)
        if dup is not None:
            item.included = False
            item.duplicate_of = dup
        else:
            kept_buckets[ph] = str(item.path)
            item.duplicate_of = None

    return items