from __future__ import annotations

from pathlib import Path
from typing import Annotated

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
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = None,
) -> None:
    pass


@app.command()
def run(
    input_dir: Annotated[Path, typer.Argument(help="Directory of images to curate.")],
    out_dir: Annotated[Path, typer.Option(help="Directory for all outputs.")] = Path(
        "out"
    ),
    recursive: Annotated[bool, typer.Option(help="Scan subdirectories.")] = True,
    min_width: Annotated[int, typer.Option(help="Minimum image width (px).")] = 128,
    min_height: Annotated[int, typer.Option(help="Minimum image height (px).")] = 128,
    blur_threshold: Annotated[
        float, typer.Option(help="Variance-of-Laplacian blur threshold.")
    ] = 50.0,
    dedup: Annotated[bool, typer.Option(help="Enable perceptual dedup.")] = True,
    dedup_tolerance: Annotated[
        int, typer.Option(help="Max Hamming distance for a duplicate match.")
    ] = 6,
    export_manifest: Annotated[bool, typer.Option(help="Write JSONL manifest.")] = True,
    export_coco: Annotated[bool, typer.Option(help="Write COCO JSON.")] = False,
    export_yolo: Annotated[bool, typer.Option(help="Write YOLO label files.")] = False,
    export_hf: Annotated[bool, typer.Option(help="Write HuggingFace dataset.")] = False,
    checkpoint_every: Annotated[
        int, typer.Option(help="Checkpoint every N items.")
    ] = 500,
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
