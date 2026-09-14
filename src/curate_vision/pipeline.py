from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.progress import track

from curate_vision.config import PipelineConfig
from curate_vision.io.loaders import load_images
from curate_vision.clean.filters import apply_filters
from curate_vision.clean.dedup import deduplicate
from curate_vision.schema import ImageItem

CHECKPOINT_FILE = "curate_vision_checkpoint.json"


class PipelineResult:
    """Summary of a completed pipeline run."""

    def __init__(
        self,
        items: list[ImageItem],
        checkpoint_every: int,
    ) -> None:
        self.items = items
        self.checkpoint_every = checkpoint_every

    @property
    def total(self) -> int:
        return len(self.items)

    @property
    def kept(self) -> int:
        return sum(1 for i in self.items if i.included)

    @property
    def duplicates(self) -> int:
        return sum(1 for i in self.items if i.duplicate_of is not None)

    @property
    def dropped(self) -> int:
        return self.total - self.kept

    def summary(self) -> dict:
        flags: dict[str, int] = {}
        for item in self.items:
            for flag in item.flags:
                flags[flag] = flags.get(flag, 0) + 1
        return {
            "total": self.total,
            "kept": self.kept,
            "dropped": self.dropped,
            "duplicates": self.duplicates,
            "flags": flags,
        }


def run_pipeline(
    cfg: PipelineConfig,
    console: Console | None = None,
) -> PipelineResult:
    """Execute intake -> clean -> dedup stages and return the result."""
    console = console or Console()
    checkpoint = _load_checkpoint(cfg.checkpoint_every)

    console.print("[bold]Stage 1/3[/bold] Intake")
    items = load_images(cfg)
    console.print(f"  discovered {len(items):,} image(s)")

    console.print("[bold]Stage 2/3[/bold] Filters")
    apply_filters(items, cfg)
    kept_after_filters = sum(1 for i in items if i.included)
    console.print(f"  kept {kept_after_filters:,} after filters")

    if cfg.enable_dedup and checkpoint is None:
        console.print("[bold]Stage 3/3[/bold] Perceptual dedup")
        for chunk in _chunks(items, cfg.batch_size):
            deduplicate(chunk, cfg)
            _maybe_checkpoint(items, cfg.checkpoint_every)
    else:
        console.print("[bold]Stage 3/3[/bold] Dedup skipped (disabled or resumed)")

    return PipelineResult(items, cfg.checkpoint_every)


def _chunks(items: list[ImageItem], size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _maybe_checkpoint(items: list[ImageItem], every: int) -> None:
    if every <= 0:
        return
    if len([i for i in items if i.phash]) % every == 0:
        _write_checkpoint(items)


def _write_checkpoint(items: list[ImageItem]) -> None:
    payload = {
        "items": [i.to_dict() for i in items],
        "version": 1,
    }
    Path(CHECKPOINT_FILE).write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )


def _load_checkpoint(every: int) -> list[ImageItem] | None:
    if every <= 0:
        return None
    path = Path(CHECKPOINT_FILE)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data["items"]
    except Exception:
        return None