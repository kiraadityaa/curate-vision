from __future__ import annotations

import json
from pathlib import Path

from curate_vision.config import PipelineConfig
from curate_vision.schema import ImageItem
from curate_vision.clean.filters import apply_filters
from curate_vision.clean.dedup import deduplicate
from curate_vision.io.loaders import load_images
from curate_vision.io.exporters import (
    export_coco_json,
    export_json_manifest,
    export_yolo_txt,
)


def _prepare(image_dir: Path) -> list[ImageItem]:
    cfg = PipelineConfig(
        input_dir=image_dir,
        min_width=1,
        min_height=1,
        blur_threshold=0.0,  # keep everything: focus on exporters only
        min_file_size=0,
    )
    return deduplicate(apply_filters(load_images(cfg), cfg), cfg)


def test_manifest_jsonl(image_dir: Path, tmp_path: Path):
    out = export_json_manifest(_prepare(image_dir), tmp_path / "manifest.jsonl")
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 5  # one per discovered image
    first = json.loads(lines[0])
    assert "path" in first and "phash" in first


def test_coco_json(image_dir: Path, tmp_path: Path):
    out = export_coco_json(_prepare(image_dir), tmp_path / "coco.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["images"]
    for img in data["images"]:
        assert img["width"] > 0 and img["height"] > 0


def test_yolo_txt(image_dir: Path, tmp_path: Path):
    out = export_yolo_txt(_prepare(image_dir), tmp_path / "labels")
    txts = list(out.glob("*.txt"))
    assert txts
    for txt in txts:
        tokens = txt.read_text(encoding="utf-8").split()
        assert tokens and tokens[0] == "0"