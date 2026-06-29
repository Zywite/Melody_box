# Spec: final-eval-spec

Scope: feature

# Especificación: Preparación Evaluación Final — MelodyBox

## 1. Reglas de Negocio Faltantes (desde SRS en `infor.tex`)

### RN-003: Política de Contraseñas
- **Validar en `UserRegister` schema**: mínimo 8 caracteres, al menos 1 número, al menos 1 mayúscula
- **Implementar en `UserService.create_user`**: lanzar excepción si no cumple
- **Tests**: unitario para validación + integración para rechazo en API

### RN-005: Límite de 50 playlists por usuario
- **Implementar en `PlaylistService.create_playlist`**: contar playlists del usuario, rechazar si >= 50
- **Tests**: unitario para límite, integración para HTTP 400

### RN-006: Límite de 500 canciones por playlist
- **Implementar en `PlaylistService.add_song_to_playlist`**: contar canciones, rechazar si >= 500
- **Tests**: unitario + integración

### RN-008a: Tamaño máximo 100MB por archivo
- **Verificar en `routes/songs.py` upload**: usar `settings.MAX_FILE_SIZE` (104857600 bytes)
- **Añadir constante** si no existe en `core/config.py`
- **Tests**: integración con archivo muy grande -> HTTP 413

### RN-015: Nombres de playlist únicos por usuario
- **Implementar en `PlaylistService.create_playlist`**: verificar que no exista playlist con mismo nombre para ese user_id
- **Tests**: unitario + integración

## 2. Mejora de Cobertura de Tests

### Módulos bajo 70% (deben alcanzar >70%)
| Módulo | Cobertura actual | Target |
|--------|:-:|:-:|
| `core/redis_helper.py` | 21% | >70% |
| `services/youtube_service.py` | 34% | >70% |
| `routes/youtube.py` | 48% | >70% |
| `services/fft_service.py` | 53% | >70% |
| `routes/dependencies.py` | 55% | >70% |
| `core/database.py` | 67% | >70% |
| `core/selective_gzip.py` | 69% | >70% |
| `main.py` | 64% | >70% |

### Estrategia por módulo:
- **redis_helper.py**: Tests con redis mockeado (AsyncMock ya en conftest)
- **youtube_service/routes**: Tests con mock de yt-dlp
- **fft_service.py**: Tests con archivos .wav sintéticos
- **dependencies.py**: Tests para get_optional_user, cache invalidation
- **database.py**: Tests para pool error handling
- **selective_gzip.py**: Tests para compresión condicional
- **main.py**: Tests para lifespan, migraciones, SPA fallback

## 3. Pipeline CI - Verificaciones

- [ ] `ruff check src/` pasa sin errores
- [ ] `ruff format --check src/` pasa sin errores
- [ ] `pytest src/tests/ --cov=app --cov-report=xml --cov-fail-under=70` pasa
- [ ] SonarQube analysis se ejecuta sin blockers
- [ ] Frontend build (`npm run build`) no da errores
- [ ] Makefile targets funcionan todos

## 4. Presentación (Diapositivas)

### Estructura sugerida:
1. **Portada**: Nombre proyecto, integrantes, fecha
2. **Arquitectura**: Diagrama de capas (Routes → Services → Models), justificación de patrón seleccionado
3. **Pipeline CI**: Captura de GitHub Actions passing, Makefile targets
4. **Autenticación**: Diagrama flujo JWT + Refresh Tokens + bcrypt
5. **Testing**: 3 categorías, cobertura 77%, cómo se ejecutan
6. **SonarQube**: Captura de scan, reporte de calidad, cobertura >70%
7. **Funcionalidades clave**: Demo en vivo (auth, upload, stream, playlist, YouTube)
8. **Casos de uso vs SRS**: Tabla mostrando cumplimiento
9. **Decisiones técnicas**: FastAPI, SQLAlchemy, Vue 3, bcrypt directo, UUID, byte-range streaming
10. **Conclusiones**: Logros, limitaciones conocidas, trabajo futuro

## 5. Demo Script

### Flujo de demostración (5-7 min):
1. Iniciar app (Docker o local)
2. Registrar nuevo usuario
3. Iniciar sesión (mostrar token JWT)
4. Subir archivo de audio
5. Reproducir canción (mostrar streaming byte-range)
6. Crear playlist y agregar canciones
7. Marcar favoritos
8. Buscar canciones
9. Mostrar admin panel (gestionar usuarios)
10. Mostrar FFT analysis
11. (Opcional) YouTube download

## 6. Checklist Final de Verificación

- [ ] Cobertura de código >= 70% general
- [ ] Ningún módulo crítico bajo 70%
- [ ] 150+ tests pasando
- [ ] CI pipeline verde (lint + format + tests + cobertura)
- [ ] SonarQube sin blockers
- [ ] Todas las reglas de negocio del SRS implementadas
- [ ] JWT + Refresh Tokens funcional
- [ ] Rate limiting en endpoints de auth
- [ ] Roles (user/admin) funcionales
- [ ] Diapositivas listas
- [ ] Demo script ensayado
- [ ] Repositorio limpio (sin secretos, sin node_modules, sin __pycache__)