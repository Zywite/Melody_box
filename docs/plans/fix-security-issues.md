---
plan name: fix-security-issues
plan description: Fix SonarQube security findings
plan status: done
---

## Idea
Fix all SonarQube security findings from the static analysis report. Three categories: (1) Generate uv.lock to pin dependency versions for reproducible builds. (2) Sanitize user-controlled filenames in songs.py upload endpoint to prevent path traversal and argument injection to ffprobe subprocess. (3) Centralize test passwords into a shared TEST_PASSWORD constant in conftest.py to eliminate ~20 hard-coded credential warnings across 4 test files and conftest.py itself.

## Implementation
- Install uv via pip and generate uv.lock from requirements.txt (uv pip compile -o uv.lock)
- Add [project] section to pyproject.toml with basic metadata for uv compatibility
- Sanitize file.filename in songs.py:_process_upload_file using Path(...).name to strip directory traversal, and reject filenames starting with '-' (argument injection to ffprobe)
- Define TEST_PASSWORD constant in conftest.py with a # nosec suppression
- Update all conftest.py fixtures (test_user, other_user, admin_user, other_admin_user) to use TEST_PASSWORD
- Update test_e2e_auth_flow.py — import TEST_PASSWORD, replace all hard-coded password strings
- Update test_auth_api.py — import TEST_PASSWORD, replace all hard-coded password strings
- Update rate_limit_standalone.py — import TEST_PASSWORD, replace all hard-coded password strings
- Update test_user_service.py — import TEST_PASSWORD, replace all hard-coded password strings
- Run existing tests to verify all fixes are non-breaking

## Required Specs
<!-- SPECS_START -->
- clean-code-spec
- security-fixes
<!-- SPECS_END -->