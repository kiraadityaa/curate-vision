# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `curate-vision run` CLI for the full pipeline.
- Intake stage: recursive folder scanning with corrupt-file detection.
- Filters: minimum resolution, aspect ratio, blur (variance-of-Laplacian).
- Perceptual near-duplicate removal via pHash/dHash + Hamming distance.
- Exporters: JSONL manifest, COCO JSON, YOLO `.txt` labels, HuggingFace Dataset (Arrow).
- Checkpoint/resume support for long-running curation jobs.
- Library API: `PipelineConfig`, `run_pipeline()`, `ImageItem`.
- GitHub Actions CI (lint + tests on Python 3.10–3.13).
- Sample dataset under `examples/data/`.

## [0.1.0] - 2026-09-14

Initial release of the MVP pipeline.