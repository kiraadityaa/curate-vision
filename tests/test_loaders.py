from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from curate_vision.config import PipelineConfig
from curate_vision.io.loaders import file_sha256, load_images


def _cfg(image_dir: Path, **kw) -> PipelineConfig:
    return PipelineConfig(input_dir=image_dir, **kw)


def test_load_images_flags_corrupt_files(tmp_path: Path):
    d = tmp_path / "broken"
    d.mkdir()
    (d / "ok.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"not a real png body")
    (d / "also_broken.png").write_bytes(b"\x00" * 8)
    cfg = _cfg(d)
    items = load_images(cfg)

    assert {i.path.name for i in items} >= {"ok.png", "also_broken.png"}
    assert all("corrupt" in i.flags for i in items)


def test_load_images_ignores_unsupported_extensions(image_dir: Path):
    (image_dir / "notes.txt").write_text("hello", encoding="utf-8")
    items = load_images(_cfg(image_dir))
    assert "notes.txt" not in {i.path.name for i in items}


def test_load_images_non_recursive_only_top_level(tmp_path: Path):
    from PIL import Image

    root = tmp_path / "root"
    nested = root / "nested"
    nested.mkdir(parents=True)
    Image.new("RGB", (8, 8)).save(root / "top.png")
    Image.new("RGB", (8, 8)).save(nested / "deep.png")

    top_only = load_images(_cfg(root, recursive=False))
    names = {i.path.name for i in top_only}
    assert names == {"top.png"}


def test_load_images_raises_for_missing_dir(tmp_path: Path):
    with pytest.raises(NotADirectoryError):
        load_images(_cfg(tmp_path / "does-not-exist"))


def test_file_sha256_matches_stdlib(tmp_path: Path):
    f = tmp_path / "data.bin"
    f.write_bytes(b"curate-vision" * 1000)
    assert file_sha256(f) == hashlib.sha256(f.read_bytes()).hexdigest()
