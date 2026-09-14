from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image


@pytest.fixture
def image_dir(tmp_path: Path) -> Path:
    """A folder with sharp and blurry/generated images for filters & dedup."""
    out = tmp_path / "images"
    out.mkdir()
    rng = np.random.default_rng(42)

    sharp = (
        rng.integers(0, 256, (256, 256, 3), dtype=np.uint8)
        * np.array([1, 2, 3], dtype=np.uint8)
    ).astype(np.uint8)
    Image.fromarray(sharp).save(out / "sharp_1.png")

    near_dup = sharp.copy()
    near_dup[::3, ::3] = 0.0
    Image.fromarray(near_dup).save(out / "sharp_2.png")

    blurry = np.full((256, 256, 3), 128, dtype=np.uint8)
    Image.fromarray(blurry).save(out / "blurry.png")

    tiny = rng.integers(0, 256, (20, 20, 3), dtype=np.uint8)
    Image.fromarray(tiny).save(out / "tiny.png")

    bad_aspect = rng.integers(0, 256, (16, 512, 3), dtype=np.uint8)
    Image.fromarray(bad_aspect).save(out / "aspect.png")

    return out


@pytest.fixture
def sharp_duplicate_dir(tmp_path: Path) -> Path:
    """Two images that are perceptually identical for dedup tests."""
    out = tmp_path / "dups"
    out.mkdir()
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[8:56, 8:56] = 200
    Image.fromarray(arr).save(out / "a.png")
    arr2 = arr.copy()
    arr2[10:54, 10:54] = 200
    Image.fromarray(arr2).save(out / "b.png")
    return out
