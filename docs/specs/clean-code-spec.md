# Spec: clean-code-spec

Scope: repo

# Especificación de Refactorización Clean Code — MelodyBox

## Objetivo
Refactorizar todo el código base (backend Python/FastAPI, frontend Vue 3, tests pytest) para cumplir con principios de Clean Code: DRY, SRP, nombres significativos, tipo explícito, manejo de errores consistente, y separación de preocupaciones.

## Temas verticales (orden de implementación)

---

## TEMA 1: Eliminar duplicación de código

### Backend
1. **Extraer lógica YouTube a servicio compartido**
   - Crear `src/app/services/youtube_service.py`
   - Mover `YTDLP_FORMAT_MAP`, `QUALITY_MAP`, lógica de descarga
   - `worker.py` y `youtube.py` consumen del mismo servicio
2. **Extraer lógica FFT a FFTService**
   - Crear `FFTService.process_and_store_fft(db, song, task)` en `fft_service.py`
   - `songs.py:282-297` y `worker.py:30-39` usan el mismo método
3. **Extraer helper `_check_playlist_ownership`**
   - Las 4 repeticiones en `playlists.py` usan una función común
4. **Extraer helper `_format_favorite_response`**
   - `favorites.py:22-35` y `favorites.py:67-80` unificados
5. **Extraer helper `_split_and_strip`** en `config.py`

### Frontend
6. **Crear composable `useFavorite`**
   - Unificar `isSongFavorite` y `toggleFavorite` (duplicado en 4 vistas)
7. **Crear composable `usePolling`**
   - Extraer patrón `setInterval` + `maxAttempts` + `clearInterval` de `FFTView.vue` y `YouTubeDownloader.vue`
8. **Crear utilidad `formatTime`**
   - Mover `formatTime`/`formatDuration` (4 duplicados) a `src/utils/format.js`

---

## TEMA 2: Refactorizar componentes grandes (frontend)

1. **Dividir `FFTView.vue` (1118 → ~400 líneas)**
   - Extraer `FFTCanvas.vue` (renderizado canvas: `drawCanvas`, `drawSpectrogram`, `getColor`)
   - Extraer `FFTControls.vue` (botones de análisis, selección de canciones)
   - Extraer composable `useFFTCanvas.js` para toda la lógica de canvas
2. **Dividir `VideoFlyout.vue` (710 → ~300 líneas)**
   - Extraer `VideoPlayer.vue` (reproductor + controles base)
   - Extraer `VideoControls.vue` (volumen, progreso, fullscreen)
3. **Dividir `YouTubeDownloader.vue` (723 → ~350 líneas)**
   - Extraer `YouTubeSearch.vue` (búsqueda + filtros)
   - Extraer `VideoCard.vue` (tarjeta de resultado individual)
4. **Dividir `LibraryView.vue` (502 → ~200 líneas)**
   - Extraer `SongTab.vue`, `PlaylistTab.vue`, `FavoritesTab.vue`
5. **Dividir `PlayerBar.vue` (513 → ~300 líneas)**

---

## TEMA 3: Mutaciones de store y acoplamiento (frontend)

1. **Agregar acciones faltantes en `player.js`**
   - `setCurrentTime(seconds)`, `setDuration(seconds)`, `removeFromQueue(index)`
   - Reemplazar todas las mutaciones directas en `App.vue:63,67`, `VideoFlyout.vue`, `QueuePanel.vue`
2. **Desacoplar `SongCard.vue` del store**
   - Recibir `favorite` y `onToggleFavorite` como props/emits
   - Mover `api.deleteSong()` al store o al padre
3. **Desacoplar `PlayerBar.vue` del store**
   - `toggleFavorite` debe ir por el store, no llamar API directo
4. **Implementar feature "Add to playlist"**
   - Eliminar los 4 stubs `// TODO: Implement`
   - Agregar lógica completa con el `CreatePlaylistModal` existente

---

## TEMA 4: Type hints y naming (backend)

1. **Agregar tipo de retorno a todas las funciones públicas**
   - `security.py`: `create_access_token -> str`, `decode_token -> Optional[dict]`
   - `song_service.py`: `get_song -> Optional[Song]`, `get_all_songs -> list[Song]`
   - `user_service.py`: todos los métodos
   - `playlist_service.py`: todos los métodos
   - `database.py`: `_create_engine_with_fallback -> Engine`, `get_db -> Generator`
   - `worker.py`: `compute_fft -> None`, `download_youtube -> None`
2. **Agregar tipo a parámetros faltantes**
3. **Mover constantes de `worker.py` a nivel de módulo**
   - `YTDLP_FORMAT_MAP`, `QUALITY_MAP` (líneas 72, 83 dentro de función → mover afuera)

---

## TEMA 5: Código muerto y magic numbers

### Backend
1. **Eliminar imports sin usar**
   - `song_service.py`: `settings`, `time`, `Path`
   - `youtube.py`: `os`, `EXTENSION_MAP`
2. **Eliminar asignación muerta** en `worker.py:69` (`ext = fmt if fmt in [...] else fmt`)
3. **Extraer magic numbers a constantes**
   - `FFT_CACHE_TTL = 86400` en `redis_helper.py`
   - `TITLE_MAX_LENGTH = 50` en `youtube_service.py`
   - `EPSILON = 1e-10`, `MAX_FRAMES = 200`, `BASS_LIMIT = 250`, `MID_LIMIT = 2000` en `fft_service.py`
   - `TOKEN_EXPIRY_MINUTES = 15` en `security.py`
   - `DB_RETRY_COUNT = 3`, `DB_RETRY_DELAY = 2` en `main.py`

### Frontend
4. **Eliminar console.logs de producción**
   - `player.js:66,75,97`, `FFTView.vue` (~10 líneas), `UploadView.vue`
5. **Extraer constantes**
   - `BAR_COUNT = 64`, `POLL_INTERVAL = 2000`, `MAX_POLL_ATTEMPTS = 60`
   - `REPEAT_MODES = ['none', 'all', 'one']`
   - Colores CSS hardcodeados en canvas → variables CSS o tema
6. **Eliminar imports sin usar**
   - `FFTView.vue:watch`, `LibraryView.vue:PlaylistCard`, `UploadView.vue:playerStore`
   - Tests: los 10 imports no usados listados en el análisis

---

## TEMA 6: Error handling y logging

### Backend
1. **Reemplazar `except Exception: pass` en `redis_helper.py`**
   - Agregar `logger.exception(...)` en cada catch
2. **Especificar excepciones en `dependencies.py:51`**
   - `except jwt.InvalidTokenError` en vez de `except Exception`
3. **Refactorizar migración SQL inline en `main.py:44-58`**
   - Mover raw SQL a un módulo `app/core/migrations.py` o agregar Alembic

### Frontend
4. **Unificar manejo de errores**
   - Decisión global: errores de API → siempre `toast.error()` (nunca `console.error` solo)
   - Aplicar en `HomeView.vue:145-147`, `SearchView.vue:102-104`, `LibraryView.vue:236`
5. **Agregar UI de error para fallos de carga**
   - `HomeView.vue:112-119` — si fallan los 3 fetch, mostrar mensaje al usuario

---

## TEMA 7: Tests — assertions, fixtures y limpieza

1. **Arreglar tests de FFT que pasan sin hacer assertions**
   - `test_fft_service.py:62-68,74,82` — quitar `if result is not None` o agregar `pytest.fail()`
2. **Especificar excepciones en tests**
   - `test_user_service.py:65-66,71-72` — `pytest.raises(IntegrityError)` en vez de `Exception`
3. **Estandarizar assertions bilingües**
   - 6 tests con `"no encontrada" or "not found"` — elegir un idioma o asertar solo status code
4. **Extraer mocks duplicados**
   - FFT mock dict → fixture `mock_fft_result`
   - Redis mock setup → helper compartido `tests/utils.py`
5. **Eliminar código muerto**
   - `e2e/conftest.py:20` — rama `if False` nunca ejecutada
   - 10 imports sin usar (listados en análisis)
6. **Mover imports inline a nivel de módulo**
   - `__import__("math")`, `__import__("io")` → imports normales al tope
   - Demás imports inline en tests de integración
7. **Renombrar test engañoso**
   - `test_token_uses_correct_algorithm` → arreglar assertion o renombrar a `test_token_decodes_successfully`
8. **Centralizar infraestructura de tests**
   - Crear `tests/helpers.py` para engine, redis mocking, override_get_db

---

## TEMA 8: CSS y temas

1. **Consolidar estilos duplicados en `main.css`**
   - `.empty-state`, `.spinner`, `.section-title`, `.filter-btn`, `.tab-btn`
   - `@keyframes fadeIn` (definido en 5 componentes)
2. **Reemplazar colores hardcodeados en canvas**
   - `FFTView.vue:400,414,460-467,483,544,548,575-577,582-593` → usar variables CSS
   - `FFTVisualizer.vue:69-71` → lo mismo
3. **Reemplazar colores hardcodeados en `VideoFlyout.vue`**
   - `#0a0a0a`, `#e11d48`, `#7c3aed` → variables CSS del tema

---

## TEMA 9: Mejoras menores

1. **Agregar docstrings** en funciones clave sin documentación
   - `security.py`, `songs.py:_process_upload_file`, `dependencies.py`
2. **Arreglar comentario bilingüe** en `dependencies.py:36`
3. **Agregar `__all__` o eliminar `__init__.py`** vacíos en `core/`, `routes/`, `services/`
4. **Arreglar path relativo** en `FFTVisualizer.vue:9` → usar alias `@/stores/player`
5. **Eliminar import innecesario** de `KeepAlive` en `App.vue:35`
6. **Reemplazar `confirm()`** con modal Vue en `SongCard.vue:109` y `PlaylistDetailView.vue:127`

---

## Criterios de aceptación

- [ ] Cero duplicación de lógica de negocio (YouTube, FFT, favorites)
- [ ] Todos los componentes < 400 líneas
- [ ] Sin `console.log` en producción
- [ ] Sin `except Exception: pass` sin logging
- [ ] Todos los tests pasan con assertions reales
- [ ] Type hints en todas las funciones públicas del backend
- [ ] Sin imports sin usar
- [ ] Sin mutaciones directas del store desde componentes
- [ ] CSS sin duplicación entre componentes
- [ ] Zero magic numbers — todos extraídos a constantes con nombre