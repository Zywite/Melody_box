---
plan name: backend-test-suite
plan description: Backend tests with pytest
plan status: done
---

## Idea
Crear suite completa de tests unitarios y de integración para MelodyBox usando pytest, cubriendo todas las reglas de negocio identificadas: auth (registro/login con validaciones), songs (CRUD, upload con validación de extensiones, FFT), playlists (CRUD con ownership), favorites (CRUD con unicidad), youtube (search/download), tasks, y seguridad (JWT, bcrypt).

## Implementation
- 1. Crear archivo src/tests/conftest.py con fixtures: engine SQLite in-memory, session local, TestClient, auth headers, datos de prueba (usuario, canciones, playlist, favoritos)
- 2. Crear src/tests/test_security.py: tests para get_password_hash, verify_password, create_access_token, decode_token, token expirado
- 3. Crear src/tests/test_user_service.py: tests unitarios para UserService (create, get_by_email, get_by_username, verify_password)
- 4. Crear src/tests/test_song_service.py: tests unitarios para SongService (create, get, search, delete)
- 5. Crear src/tests/test_playlist_service.py: tests unitarios para PlaylistService (create, get, add/remove song, delete, duplicados)
- 6. Crear src/tests/test_fft_service.py: tests unitarios para FFTService (compute_fft, get_fft_data_json, to_json)
- 7. Crear src/tests/test_auth_api.py: tests integración /auth/register y /auth/login con rate limiting mockeado
- 8. Crear src/tests/test_songs_api.py: tests integración /songs (upload, list, search, get, stream, delete, upload-multiple, FFT endpoints)
- 9. Crear src/tests/test_playlists_api.py: tests integración /playlists (CRUD, ownership, agregar/quitar canciones)
- 10. Crear src/tests/test_favorites_api.py: tests integración /favorites (add, list, remove, duplicados)
- 11. Crear src/tests/test_tasks_api.py: tests integración /tasks/{task_id}
- 12. Agregar pytest y httpx a requirements.txt como dev dependencies
- 13. Ejecutar tests y verificar que todo pasa

## Required Specs
<!-- SPECS_START -->
- backend-test-suite
<!-- SPECS_END -->