from __future__ import annotations

from pathlib import Path

from curate_vision.config import PipelineConfig
from curate_vision.io.loaders import load_images
from curate_vision.clean.dedup import deduplicate


def test_dedup_marks_near_duplicates(sharp_duplicate_dir: Path):
    cfg = PipelineConfig(
        input_dir=sharp_duplicate_dir,
        min_width=1,
        min_height=1,
        blur_threshold=0.0,
        min_file_size=0,
    )
    items = deduplicate(load_images(cfg), cfg)

    kept = [i for i in items if i.included]
    dropped = [i for i in items if not i.included and i.duplicate_of]
    assert len(kept) == 1
    assert len(dropped) == 1
    assert dropped[0].duplicate_of == str(kept[0].path)


def test_dedup_keeps_distinct_images(image_dir: Path):
    cfg = PipelineConfig(
        input_dir=image_dir,
        min_width=1,
        min_height=1,
        blur_threshold=0.0,
        min_file_size=0,
    )
    items = deduplicate(load_images(cfg), cfg)
    phashes = {i.phash for i in items if i.included}
    assert len(phashes) >= 3  # sharp_1, sharp_2 (near-dup), tiny/distinct

    # perceptual duplicates both survive intact but flag relationship
    dups = [i for i in items if i.duplicate_of]
    assert any(i.path.stem == "sharp_1" or i.path.stem == "sharp_2" for i in dups)