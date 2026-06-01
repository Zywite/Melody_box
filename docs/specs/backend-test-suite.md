# Spec: backend-test-suite

Scope: feature

# Backend Test Suite - MelodyBox

## Stack
- **Framework:** pytest + httpx (TestClient para FastAPI)
- **DB:** SQLite en memoria (para tests de integración)
- **Cobertura objetivo:** >80% en servicios, >70% en routes

## Estructura de directorios
```
src/tests/
├── conftest.py              # Fixtures globales (DB, client, auth)
├── test_security.py         # Tests de hashing y JWT
├── test_user_service.py     # Tests unitarios UserService
├── test_song_service.py     # Tests unitarios SongService
├── test_playlist_service.py # Tests unitarios PlaylistService
├── test_fft_service.py      # Tests unitarios FFTService
├── test_auth_api.py         # Tests integración endpoints /auth
├── test_songs_api.py        # Tests integración endpoints /songs
├── test_playlists_api.py    # Tests integración endpoints /playlists
├── test_favorites_api.py    # Tests integración endpoints /favorites
└── test_tasks_api.py        # Tests integración endpoints /tasks
```

## Test Data / Seeds
- Usuario de prueba (id fijo, email fijo)
- 2-3 canciones de prueba
- 1 playlist de prueba con canciones
- 1 favorito de prueba

## Reglas de Negocio a testear

### Auth
1. Registro exitoso crea usuario y hashea password
2. Registro rechaza email duplicado (400)
3. Registro rechaza username duplicado (400)
4. Registro rate-limited a 3/min
5. Login exitoso devuelve JWT + username
6. Login rechaza credenciales incorrectas (401)
7. Login rate-limited a 5/min

### Songs
1. Subida con extensión permitida → éxito
2. Subida con extensión no permitida → 400
3. Subida sin autenticación → 401
4. Subida rate-limited a 10/min
5. Listar canciones con paginación (skip/limit)
6. Búsqueda por título (case-insensitive)
7. Búsqueda por artista
8. Obtener canción por ID → 404 si no existe
9. Stream de canción existente → 200 con Content-Type correcto
10. Stream de canción sin archivo → 404
11. Eliminar canción (autenticado) → elimina de DB y del disco
12. Subida múltiple con metadata correcta
13. Subida múltiple con mismatch files/metadata → 400
14. Subida múltiple con error parcial → devuelve errores individuales

### Playlists
1. Crear playlist autenticado → éxito
2. Crear playlist sin auth → 401
3. Obtener playlists del usuario autenticado
4. Obtener playlist por ID (owner) → éxito
5. Obtener playlist por ID (no owner) → 403
6. Obtener playlist inexistente → 404
7. Agregar canción existente a playlist (owner)
8. Agregar canción duplicada → no crea duplicado (retorna existente)
9. Agregar canción inexistente → 404
10. Agregar canción sin ser owner → 403
11. Eliminar canción de playlist (owner)
12. Eliminar playlist (owner)
13. Eliminar playlist sin ser owner → 403

### Favorites
1. Agregar favorito autenticado → éxito con datos de canción
2. Agregar favorito sin auth → 401
3. Agregar canción inexistente → 404
4. Agregar favorito duplicado → 400
5. Listar favoritos del usuario
6. Eliminar favorito existente → éxito
7. Eliminar favorito inexistente → 404

### FFT
1. Obtener FFT de canción sin datos → crea tarea o respuesta pending
2. Obtener FFT de canción inexistente → 404
3. Analyze-all procesa canciones sin FFT

### YouTube
1. Búsqueda con query → lista de resultados
2. Descarga con formato no soportado → 400

### Tasks
1. Obtener task por ID → datos completos
2. Obtener task inexistente → 404

### Seguridad
1. Password hashing produce hash válido
2. verify_password funciona con hash correcto
3. verify_password rechaza password incorrecto
4. JWT creación y decoding funciona
5. Token expirado es rechazado
6. Endpoint protegido sin token → 401
7. Endpoint protegido con token inválido → 401