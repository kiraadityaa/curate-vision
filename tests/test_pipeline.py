from __future__ import annotations

from pathlib import Path

import pytest

from curate_vision.config import PipelineConfig
from curate_vision.pipeline import _chunks, _load_checkpoint, run_pipeline
from curate_vision.schema import ImageItem


def _base_cfg(image_dir: Path) -> PipelineConfig:
    return PipelineConfig(
        input_dir=image_dir,
        min_width=1,
        min_height=1,
        blur_threshold=0.0,
        min_file_size=0,
    )


def test_run_pipeline_end_to_end(image_dir: Path):
    result = run_pipeline(_base_cfg(image_dir))

    assert result.total == 5
    assert result.kept + result.dropped == result.total
    assert result.duplicates < result.total
    assert result.summary()["total"] == 5
    assert "flags" in result.summary()


def test_run_pipeline_dedup_marks_duplicates(sharp_duplicate_dir: Path):
    result = run_pipeline(_base_cfg(sharp_duplicate_dir))

    assert result.duplicates == 1
    assert result.kept == 1
    dropped = [i for i in result.items if i.duplicate_of]
    assert len(dropped) == 1
    assert dropped[0].duplicate_of.endswith("a.png")


def test_run_pipeline_with_dedup_disabled(image_dir: Path):
    cfg = _base_cfg(image_dir)
    cfg.enable_dedup = False
    result = run_pipeline(cfg)

    assert result.duplicates == 0
    assert all(i.duplicate_of is None for i in result.items)


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_run_pipeline_writes_no_checkpoint_by_default(image_dir: Path, tmp_path: Path):
    cfg = _base_cfg(image_dir)
    cfg.input_dir = image_dir
    run_pipeline(cfg)
    # Checkpoint file is only written when checkpoint_every > 0
    from curate_vision.pipeline import CHECKPOINT_FILE

    assert not (Path.cwd() / CHECKPOINT_FILE).exists()


def test_chunks_split_evenly():
    items = [ImageItem(path=Path(f"{i}.png")) for i in range(7)]
    assert [len(c) for c in _chunks(items, 3)] == [3, 3, 1]


def test_checkpoint_write_and_load(tmp_path: Path, monkeypatch):
    import curate_vision.pipeline as pipeline

    cp = tmp_path / "ckpt.json"
    monkeypatch.setattr(pipeline, "CHECKPOINT_FILE", str(cp))
    pipeline._write_checkpoint([ImageItem(path=Path("a.png"), phash="abc")])

    loaded = _load_checkpoint(500)
    assert loaded is not None
    assert loaded[0]["phash"] == "abc"


def test_checkpoint_disabled_or_missing(tmp_path: Path, monkeypatch):
    import curate_vision.pipeline as pipeline

    assert _load_checkpoint(0) is None
    monkeypatch.setattr(pipeline, "CHECKPOINT_FILE", str(tmp_path / "nope.json"))
    assert _load_checkpoint(500) is None


def test_checkpoint_corrupt_returns_none(tmp_path: Path, monkeypatch):
    import curate_vision.pipeline as pipeline

    cp = tmp_path / "bad.json"
    cp.write_text("not json", encoding="utf-8")
    monkeypatch.setattr(pipeline, "CHECKPOINT_FILE", str(cp))
    assert _load_checkpoint(500) is None


def test_maybe_checkpoint_respects_every(tmp_path: Path, monkeypatch):
    import curate_vision.pipeline as pipeline

    cp = tmp_path / "ck.json"
    monkeypatch.setattr(pipeline, "CHECKPOINT_FILE", str(cp))
    items = [
        ImageItem(path=Path("a.png"), phash="1"),
        ImageItem(path=Path("b.png"), phash="2"),
    ]

    pipeline._maybe_checkpoint(items, 2)
    assert cp.exists()

    cp.unlink()
    pipeline._maybe_checkpoint(items, 3)  # 2 % 3 != 0 -> no write
    assert not cp.exists()

    pipeline._maybe_checkpoint(items, 0)  # disabled
    assert not cp.exists()
