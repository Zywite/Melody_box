# Spec: security-fixes

Scope: feature

# Spec: security-fixes

## Scope: feature (part of fix-security-issues plan)

## Issues to fix

### 1. Missing lock file (pyproject.toml)
- Install `uv` via `pip install uv`
- Run `uv pip compile requirements.txt -o uv.lock` to generate lock file
- If uv compilation fails, consider adding a `[project]` section to `pyproject.toml`
- Add `uv.lock` to the repo

### 2. Path traversal & command injection (songs.py)
- In `_process_upload_file` (L124), sanitize `file.filename`:
  - Use `Path(file.filename).name` to strip directory components (prevents `../../etc` traversal)
  - Reject filenames starting with `-` (prevents argument injection into ffprobe at L81)
  - Raise `HTTPException(400)` for invalid filenames
- This single fix addresses all 3 findings (L81, L160, L164)

### 3. Hard-coded passwords in tests
- Define `TEST_PASSWORD = "TestPass123!"` in `src/tests/conftest.py` with `# nosec` suppression
- Export it (make it importable)
- Update all conftest.py fixtures to use `TEST_PASSWORD`
- Update all test files to import and use `TEST_PASSWORD`:
  - `test_e2e_auth_flow.py` (7 occurrences)
  - `test_auth_api.py` (4 occurrences)
  - `rate_limit_standalone.py` (4 occurrences)
  - `test_user_service.py` (5 occurrences)

## Acceptance criteria
- [ ] `uv.lock` committed and build is reproducible
- [ ] Filenames with `../` or starting with `-` return 400
- [ ] Normal uploads still work correctly
- [ ] All tests pass with the shared `TEST_PASSWORD`
- [ ] Zero SonarQube security findings for these files