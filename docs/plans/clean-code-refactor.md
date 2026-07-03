---
plan name: clean-code-refactor
plan description: Full clean code refactor
plan status: done
---

## Idea
Refactorizar todo el código base de MelodyBox (backend FastAPI + frontend Vue 3 + tests pytest) para cumplir principios Clean Code. Organizado por temas verticales: eliminar duplicación, dividir componentes grandes, centralizar mutaciones de store, agregar type hints, remover código muerto/magic numbers, mejorar error handling, limpiar tests, consolidar CSS y aplicar mejoras menores. ~131 issues identificados, abordados en 9 temas secuenciales.

## Implementation
- TEMA 1: Eliminar duplicación — Extraer lógica YouTube a servicio compartido (youtube_service.py), unificar FFT en FFTService, crear helpers playlist_ownership, favorite_response y config
- TEMA 1 (cont.): Frontend — Crear composables useFavorite, usePolling y utilidad formatTime. Eliminar código duplicado en 4+ vistas
- TEMA 2: Dividir componentes grandes — FFTView (1118→~400), VideoFlyout (710→~300), YouTubeDownloader (723→~350), LibraryView (502→~200), PlayerBar (513→~300)
- TEMA 3: Mutaciones de store — Agregar acciones faltantes (setCurrentTime, setDuration, removeFromQueue) en player.js. Desacoplar SongCard y PlayerBar del store. Implementar feature 'Add to playlist'
- TEMA 4: Type hints — Agregar tipos de retorno en security.py, song_service, user_service, playlist_service, database.py, worker.py. Mover constantes worker.py a nivel módulo
- TEMA 5: Código muerto y magic numbers — Eliminar imports sin usar, asignaciones muertas. Extraer ~15 constantes con nombre (FFT_CACHE_TTL, EPSILON, BAR_COUNT, etc). Remover console.logs de producción
- TEMA 6: Error handling — Reemplazar except Exception:pass con logging en redis_helper. Especificar excepciones en dependencies.py. Unificar manejo de errores frontend con toast.error siempre. Agregar UI de error en HomeView
- TEMA 7: Tests — Arreglar tests FFT sin assertions. Especificar excepciones en test_user_service. Estandarizar assertions bilingües. Extraer fixtures duplicadas. Eliminar código muerto. Mover imports inline a nivel módulo. Crear tests/helpers.py
- TEMA 8: CSS y temas — Consolidar estilos duplicados en main.css (empty-state, spinner, fadeIn). Reemplazar colores hardcodeados en canvas y VideoFlyout con variables CSS
- TEMA 9: Mejoras menores — Agregar docstrings. Arreglar comentario bilingüe. __all__ en init. Path relativo FFTVisualizer. Reemplazar confirm() con modal Vue. Eliminar import KeepAlive innecesario

## Required Specs
<!-- SPECS_START -->
- clean-code-spec
- coding-standards
<!-- SPECS_END -->