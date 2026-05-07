---
plan name: improve-startup-scripts
plan description: Fix startup scripts
plan status: done
---

## Idea
Improve start_server.py and related startup scripts with cross-platform support, better error handling, configuration management, and alignment with current project structure

## Implementation
- Update start_server.py: Add cross-platform venv detection (Windows/Linux/Mac)
- Update start_server.py: Add command-line arguments for host, port, and reload options
- Update start_server.py: Add graceful shutdown with signal handlers
- Update start_server.py: Add logging instead of print statements
- Update start_server.py: Validate port availability before starting
- Fix validate_setup.py: Update to check root .env instead of src/.env
- Fix validate_setup.py: Update paths to match current project structure (frontend/dist instead of public/static)
- Fix validate_setup.py: Align checked packages with requirements.txt
- Fix run_server.sh: Correct directory reference (no 'backend' dir exists)
- Fix run_server.sh: Align port number with other scripts (8001)
- Fix run_server.bat: Add cross-platform consistency
- Add --no-reload option for production use in start_server.py
- Add option to specify config file path via environment variable

## Required Specs
<!-- SPECS_START -->
<!-- SPECS_END -->