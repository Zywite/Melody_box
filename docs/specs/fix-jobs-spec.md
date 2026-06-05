# Spec: fix-jobs-spec

Scope: feature

# Fix Jobs and CI Specification

## Problems

1. **CI test failure (exit code 4)**: `pyproject.toml` references `starlette.exceptions.StarletteDeprecationWarning` which was removed in Starlette >= 0.40. The installed Starlette 0.52.1 no longer has this class, so pytest crashes when parsing the filter.

2. **YouTube download file not found for audio formats**: In `worker.py:69` and `youtube.py:134`, the extension variable for audio formats is wrapped in parentheses: `f"({fmt})"` instead of `fmt`. This produces extensions like `"(mp3)"` instead of `"mp3"`, causing the downloaded file lookup to fail.

3. **run_worker.bat fails to start worker**: After `cd src`, the script references `.venv\Scripts\python.exe` relative to `src/`, but `.venv` is at the project root. Also missing `PYTHONPATH` for module imports.

## Requirements

- CI tests must pass without parse errors
- YouTube downloads in audio formats (mp3, m4a, wav, flac, ogg) must complete successfully
- `run_worker.bat` must start the ARQ worker from the project root