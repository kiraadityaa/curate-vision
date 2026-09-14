from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class PipelineConfig(BaseModel):
    """Settings that control each stage of the pipeline."""

    # --- Intake ---
    input_dir: Path = Field(default=Path("."), description="Root directory to scan.")
    extensions: set[str] = Field(
        default={".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"},
        description="Accepted file extensions.",
    )
    recursive: bool = Field(default=True, description="Scan subdirectories.")

    # --- Filters ---
    min_width: int = Field(default=128, ge=1)
    min_height: int = Field(default=128, ge=1)
    max_aspect_ratio: float = Field(default=10.0, ge=1.0)
    min_file_size: int = Field(default=0, ge=0, description="Min bytes (0 = disabled).")
    blur_threshold: float = Field(
        default=50.0,
        ge=0,
        description="Variance-of-Laplacian threshold; images below are considered blurry.",
    )

    # --- Dedup ---
    enable_dedup: bool = True
    dedup_tolerance: int = Field(
        default=6,
        ge=0,
        le=64,
        description="Hamming distance threshold for perceptual hash dedup.",
    )

    # --- Export ---
    export_manifest: bool = True
    export_coco: bool = False
    export_yolo: bool = False
    export_hf: bool = False

    # --- Pipeline ---
    checkpoint_every: int = Field(
        default=500, ge=0, description="Save checkpoint every N images."
    )
    batch_size: int = Field(default=32, ge=1)
    workers: int = Field(
        default=0, ge=0, description="Dataloader workers (0 = main thread)."
    )

    @property
    def extensions_lower(self) -> set[str]:
        return {e.lower() for e in self.extensions}
