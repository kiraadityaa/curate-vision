# Contributing to curate-vision

Thanks for your interest in improving `curate-vision`! Every contribution —
bug reports, feature requests, documentation, code — is welcome.

## Table of contents

- [Code of conduct](#code-of-conduct)
- [Getting started](#getting-started)
- [Development setup](#development-setup)
- [Running checks](#running-checks)
- [Project layout](#project-layout)
- [Submitting changes](#submitting-changes)
- [Guidelines](#guidelines)

## Code of conduct

Please read and follow our [Code of Conduct](./CODE_OF_CONDUCT.md).

## Getting started

- **Found a bug?** [Open an issue](https://github.com/kiraadityaa/curate-vision/issues/new?template=bug_report.yml) using the bug template.
- **Have an idea?** [Open a feature request](https://github.com/kiraadityaa/curate-vision/issues/new?template=feature_request.yml).
- **Want to fix something?** Search issues/PRs first to avoid duplicates, then
  comment on the issue to claim it.

## Development setup

Requires Python 3.10+.

```bash
git clone https://github.com/kiraadityaa/curate-vision.git
cd curate-vision
python -m venv .venv
source .venv/bin/activate          # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

The `[dev]` extra installs:

| Tool         | Purpose                              |
|--------------|--------------------------------------|
| `pytest`     | Unit tests                           |
| `pytest-cov` | Code coverage reports                |
| `ruff`       | Linting and formatting               |

## Running checks

Run these locally before pushing:

```bash
ruff check .             # lint
ruff format --check .    # formatting
pytest                   # tests
pytest --cov             # tests + coverage
```

## Project layout

```
src/curate_vision/
├── cli.py          # Typer command-line interface
├── config.py       # Pydantic PipelineConfig
├── pipeline.py     # Stage orchestration (intake -> clean -> dedup)
├── schema.py       # ImageItem dataclass
├── clean/
│   ├── filters.py  # Resolution / aspect / blur filters
│   └── dedup.py    # Perceptual hashing near-duplicates
└── io/
    ├── loaders.py  # Input: folder scanning
    └── exporters.py# Output: JSONL / COCO / YOLO / HuggingFace
```

## Submitting changes

1. Create a branch: `git checkout -b feat/my-change`.
2. Make your changes, keeping the diff focused.
3. Update or add tests in `tests/`.
4. Run all checks (see [Running checks](#running-checks)) until everything passes.
5. Update `CHANGELOG.md` under an `Unreleased` section.
6. Commit with a clear message:

   ```
   feat: add description
   fix: correct description
   docs: update description
   ```

7. Open a pull request against `main` using the PR template.

## Guidelines

- Keep the public API small and typed. Use `from __future__ import annotations`.
- New images-processing stages belong under `clean/`; new I/O under `io/`.
- Prefer optional dependencies (extras) for heavy deps like `datasets`.
- Preserve backward compatibility; bump `CHANGELOG.md` and `__version__` accordingly.