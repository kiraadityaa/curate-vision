# Security Policy

We take the security of `curate-vision` seriously.

## Supported versions

Security fixes are applied to the latest stable release. Older versions are
patched on a best-effort basis.

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a vulnerability

Please **do not** open a public issue for security problems. Instead, report
privately:

- Open a [private security advisory](https://github.com/kiraadityaa/curate-vision/security/advisories/new),
- or email the maintainer (see the `authors` field in `pyproject.toml`).

Please include:

- The affected version(s).
- A description of the vulnerability and its impact.
- A minimal reproduction (code sample or commands).
- Suggested fix, if you have one.

We aim to acknowledge reports within 72 hours and will keep you updated as the
issue is triaged, investigated, and fixed. We ask that you give us a reasonable
time window to respond before disclosing the issue publicly.

## Scope

- Code in this repository (CLI, library, CI workflows).
- Dependencies are out of scope for direct reports; please use their upstream
  vulnerability reporting channels.