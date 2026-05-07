---
plan name: reorganize-project-structure
plan description: Reorganize files to follow conventions
plan status: active
---

## Idea
Move data files (music_storage/, spotify_local.db) out of src/ to proper data/ directory at root level, update all path references in code, and clean up misplaced files (ejemplo_documento.pdf, texmint.json)

## Implementation
- Update src/app/main.py: Change MUSIC_DIR from BASE_DIR/'src'/'music_storage' to BASE_DIR/'data'/'music'
- Update src/app/core/database.py: Change fallback db path from BASE_DIR/'spotify_local.db' to BASE_DIR/'data'/'spotify_local.db'
- Update src/app/core/config.py: Change default DATABASE_URL to sqlite:///./data/spotify_local.db
- Update src/app/core/config.py: MUSIC_STORAGE_PATH already uses BASE_DIR/'music_storage' - change to BASE_DIR/'data'/'music'
- Move physical directory: src/music_storage/ -> data/music/
- Move physical file: src/spotify_local.db -> data/spotify_local.db
- Update .gitignore: Change music_storage/ to data/
- Update .gitignore: Add data/*.db pattern
- Move ejemplo_documento.pdf from root to docs/
- Move texmint.json from root to docs/
- Check if public/ directory at root is needed - if not, add to .gitignore
- Verify frontend/dist/ is in .gitignore
- Test: Run validate_setup.py to ensure paths are correct
- Test: Check that config.py loads correct paths

## Required Specs
<!-- SPECS_START -->
<!-- SPECS_END -->