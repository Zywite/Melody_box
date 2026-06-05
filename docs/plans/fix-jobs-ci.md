---
plan name: fix-jobs-ci
plan description: Fix jobs and CI bugs
plan status: done
---

## Idea
Fix multiple bugs in the background job system and CI tests: (1) Remove invalid StarletteDeprecationWarning filter from pyproject.toml that breaks pytest in CI; (2) Fix the wrapper/parentheses bug in worker.py line 69 and youtube.py line 134 where audio format extensions get wrapped in parentheses like "(mp3)" instead of "mp3", causing downloaded files to not be found; (3) Fix run_worker.bat path issues with .venv location and missing PYTHONPATH; (4) Optionally verify the fixes pass tests.

## Implementation
- Remove invalid warning filter from pyproject.toml (line 6: ignore::starlette.exceptions.StarletteDeprecationWarning)
- Fix ext variable bug in worker.py:69 - change f'({fmt})' to fmt for audio formats
- Fix ext variable bug in youtube.py:134 - change f'({request.format})' to request.format
- Fix run_worker.bat: change .venv path to use project root instead of src/ after cd src
- Add PYTHONPATH export to run_worker.bat for worker module imports
- Run pytest to verify tests pass with the fix

## Required Specs
<!-- SPECS_START -->
- fix-jobs-spec
<!-- SPECS_END -->