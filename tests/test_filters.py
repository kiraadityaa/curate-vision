from __future__ import annotations

from pathlib import Path

from curate_vision.config import PipelineConfig
from curate_vision.io.loaders import load_images
from curate_vision.clean.filters import apply_filters


def test_load_images_finds_all_supported(image_dir: Path):
    cfg = PipelineConfig(input_dir=image_dir)
    items = load_images(cfg)
    assert {i.path.name for i in items} >= {
        "sharp_1.png",
        "sharp_2.png",
        "blurry.png",
        "tiny.png",
        "aspect.png",
    }
    for item in items:
        assert item.width > 0 and item.height > 0


def test_filters_flag_undersized_and_bad_aspect(image_dir: Path):
    base = dict(min_width=128, min_height=128, blur_threshold=0.0, min_file_size=0)
    cfg = PipelineConfig(input_dir=image_dir, **base)
    items = apply_filters(load_images(cfg), cfg)
    by_name = {i.path.name: i for i in items}
    assert "too_small" in by_name["tiny.png"].flags
    assert "too_small" in by_name["aspect.png"].flags  # 16px tall
    assert by_name["sharp_1.png"].included
    # blurry excluded when threshold is high
    cfg_high = PipelineConfig(
        input_dir=image_dir, blur_threshold=1.0, min_file_size=0
    )
    items_high = apply_filters(load_images(cfg_high), cfg_high)
    by_name_high = {i.path.name: i for i in items_high}
    assert "blurry" in by_name_high["blurry.png"].flags
    assert not by_name_high["blurry.png"].included