# curate-vision

End-to-end vision dataset curation & pipeline toolkit.

Turn messy image folders into clean, deduplicated, training-ready datasets —
no GPU required.

## Why

High-quality data beats raw quantity for training computer-vision models, but
the tooling is scattered across a dozen half-maintained repos. `curate-vision`
bundles the common stages — **intake → clean → dedup → export** — into one
typed, offline-first pipeline with a simple CLI.

## Install

```bash
pip install curate-vision
```

Optional extras:

```bash
pip install "curate-vision[datasets]"   # HuggingFace Dataset export
pip install "curate-vision[all]"        # everything (incl. dev tooling)
```

## Quick start

```bash
curate-vision run ./photos \
  --out-dir out \
  --min-width 512 \
  --min-height 512 \
  --blur-threshold 60 \
  --dedup-tolerance 6 \
  --export-manifest \
  --export-coco
```

### Pipeline stages

| # | Stage    | What it does                                                        |
|---|----------|---------------------------------------------------------------------|
| 1 | Intake   | Scans a folder (recursive), reads image metadata, flags corrupt files |
| 2 | Filters  | Drops undersized, bad-aspect, or blurry images (variance-of-Laplacian) |
| 3 | Dedup    | Perceptual pHash/dHash near-duplicate detection within a Hamming tolerance |
| 4 | Export   | JSONL manifest, COCO JSON, YOLO `.txt` labels, HuggingFace Dataset (Arrow) |

### Outputs

```
out/
├── manifest.jsonl       # every item + flags (kept/dropped + why)
├── coco.json            # COCO-format annotations (if --export-coco)
├── labels/*.txt         # YOLO format labels (if --export-yolo)
└── huggingface/         # Arrow dataset (if --export-hf)
```

### Library usage

```python
from curate_vision import PipelineConfig, run_pipeline

cfg = PipelineConfig(
    input_dir="photos",
    min_width=512,
    min_height=512,
    blur_threshold=60,
    dedup_tolerance=6,
)
result = run_pipeline(cfg)
print(result.summary())   # {'total': ..., 'kept': ..., 'dropped': ..., ...}
```

## Roadmap

- [x] Intake: local folder
- [x] Filters: size, aspect, blur
- [x] Dedup: perceptual hashing
- [x] Export: JSONL / COCO / YOLO / HuggingFace
- [ ] Intake: HuggingFace datasets, video frame extraction
- [ ] Enrichment: VLM captioning (Qwen2.5-VL, MiniCPM) via Ollama/llama.cpp
- [ ] Quality scoring: aesthetics + relevance composite score
- [ ] NSFW & poison filtering

## License

Apache-2.0