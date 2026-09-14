from __future__ import annotations

import cv2
import numpy as np

from curate_vision.config import PipelineConfig
from curate_vision.schema import ImageItem


def variance_of_laplacian(image: np.ndarray) -> float:
    """Classic sharpness metric; higher = sharper."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def apply_filters(items: list[ImageItem], cfg: PipelineConfig) -> list[ImageItem]:
    """Mutate each item's flags/included state based on filter rules.

    An item is kept only if it passes every filter. Filters read existing
    metadata (width/height/file_size) and compute blur lazily via OpenCV.
    """
    for item in items:
        if "corrupt" in item.flags:
            item.included = False
            continue

        checks: list[str] = []
        if item.width < cfg.min_width or item.height < cfg.min_height:
            checks.append("too_small")
        if item.width and item.height:
            ratio = max(item.width / item.height, item.height / item.width)
            if ratio > cfg.max_aspect_ratio:
                checks.append("bad_aspect")
        if item.file_size < cfg.min_file_size:
            checks.append("too_small_file")

        if checks:
            item.flags.extend(checks)
            item.included = False
            continue

        try:
            image = cv2.imread(str(item.path))
            item.blur_score = variance_of_laplacian(image)
            if item.blur_score < cfg.blur_threshold:
                item.flags.append("blurry")
                item.included = False
        except Exception:
            item.flags.append("read_error")
            item.included = False

    return items