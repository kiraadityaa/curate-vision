from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from curate_vision import __version__
from curate_vision.config import PipelineConfig
from curate_vision.io.exporters import (
    export_coco_json,
    export_hf_dataset,
    export_json_manifest,
    export_yolo_txt,
)
from curate_vision.pipeline import run_pipeline

app = typer.Typer(help="curate-vision: curate vision datasets end-to-end.")
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"curate-vision {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    pass


@app.command()
def run(
    input_dir: Path = typer.Argument(..., help="Directory of images to curate."),
    out_dir: Path = typer.Option(
        Path("out"), help="Directory for all outputs."
    ),
    recursive: bool = typer.Option(True, help="Scan subdirectories."),
    min_width: int = typer.Option(128, help="Minimum image width (px)."),
    min_height: int = typer.Option(128, help="Minimum image height (px)."),
    blur_threshold: float = typer.Option(
        50.0, help="Variance-of-Laplacian blur threshold."
    ),
    dedup: bool = typer.Option(True, help="Enable perceptual dedup."),
    dedup_tolerance: int = typer.Option(
        6, help="Max Hamming distance for a duplicate match."
    ),
    export_manifest: bool = typer.Option(True, help="Write JSONL manifest."),
    export_coco: bool = typer.Option(False, help="Write COCO JSON."),
    export_yolo: bool = typer.Option(False, help="Write YOLO label files."),
    export_hf: bool = typer.Option(False, help="Write HuggingFace dataset."),
    checkpoint_every: int = typer.Option(500, help="Checkpoint every N items."),
) -> None:
    """Curate images from INPUT_DIR through filters and dedup."""
    if not input_dir.is_dir():
        console.print(f"[red]Input directory not found:[/red] {input_dir}")
        raise typer.Exit(code=1)

    cfg = PipelineConfig(
        input_dir=input_dir,
        recursive=recursive,
        min_width=min_width,
        min_height=min_height,
        blur_threshold=blur_threshold,
        enable_dedup=dedup,
        dedup_tolerance=dedup_tolerance,
        export_manifest=export_manifest,
        export_coco=export_coco,
        export_yolo=export_yolo,
        export_hf=export_hf,
        checkpoint_every=checkpoint_every,
    )
    result = run_pipeline(cfg, console=console)

    out_dir.mkdir(parents=True, exist_ok=True)
    if cfg.export_manifest:
        path = export_json_manifest(result.items, out_dir / "manifest.jsonl")
        console.print(f"[green]manifest[/green] -> {path}")
    if cfg.export_coco:
        path = export_coco_json(result.items, out_dir / "coco.json")
        console.print(f"[green]coco[/green] -> {path}")
    if cfg.export_yolo:
        path = export_yolo_txt(result.items, out_dir / "labels")
        console.print(f"[green]yolo labels[/green] -> {path}")
    if cfg.export_hf:
        path = export_hf_dataset(result.items, out_dir / "huggingface")
        console.print(f"[green]hf dataset[/green] -> {path}")

    _print_summary(result.summary())


def _print_summary(summary: dict) -> None:
    table = Table(title="Curation summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    for key, value in summary.items():
        if key == "flags":
            continue
        table.add_row(key.replace("_", " "), str(value))
    console.print(table)
    if summary["flags"]:
        console.print("[bold]Dropped reasons:[/bold]")
        for flag, count in summary["flags"].items():
            console.print(f"  {flag}: {count}")


if __name__ == "__main__":
    app()