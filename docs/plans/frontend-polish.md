---
plan name: frontend-polish
plan description: Frontend polish and TS gradual
plan status: active
---

## Idea
Polish the MelodyBox frontend: implement the long-pending AddToPlaylistModal across 4 views, debounce the search input, switch LibraryView to virtual scrolling, optimize PlaylistDetailView's O(n) song lookup with a Map, remove duplicated CSS in SearchInput, add vitest for stores/composables, fix 401 retry loop guard, and add a "searching..." state.

Stack: Vue 3 + Vite + Pinia + Vue Router + Axios + Lucide. No existing tests; new code is written in TypeScript (gradual migration): new .ts files for stores/composables/tests, and AddToPlaylistModal.vue is the first typed .vue component. Existing .js files stay as-is.

Acceptance: each TODO add-to-playlist hook calls the new modal; search emits debounced; LibraryView uses VirtualList; PlaylistDetailView builds a Map; SearchInput CSS is deduped; vitest runs `npm test`; useApi caps retries; SearchView shows a loading indicator while searching. Build + existing 133 backend tests must still pass.

## Implementation
- [ ] **AddToPlaylistModal.vue** — Modal único reusado por LibraryView, HomeView, SearchView y PlayerBar; consume `usePlaylistsStore.addSongToPlaylist`; ofrece "Crear playlist" cuando la lista está vacía.
- [ ] **SearchInput debounce** — `setTimeout`/`clearTimeout` (300ms) que emite el evento `search` con el valor debounced; `v-model` síncrono; elimina el bloque CSS duplicado del componente.
- [ ] **LibraryView virtual scroll** — Reemplaza el `v-for` por `<VirtualList :item-height=84>` (extraído en perf-tuning) sin tocar la paginación existente.
- [ ] **PlaylistDetailView Map lookup** — Construye `songMap = new Map(allSongs.map(s => [s.id, s]))` en `onMounted`; `getSongData(id)` queda como `songMap.get(id)`.
- [ ] **Vitest setup** — `vitest.config.ts` (jsdom, alias `@`), spec para SWR + optimistic de `songs` y `favorites`, script `npm test`.
- [ ] **useApi 401 retry cap** — `_retryCount` en `composables/useApi.js`; al primer 401 persistente se limpia el estado de auth (en vez de esperar al segundo).
- [ ] **SearchView loading state** — `isSearching` ref alrededor de `api.searchSongs(q)`; spinner / "Buscando..." junto al input; limpiado en `finally`.
- [x] **TypeScript scaffolding** — `tsconfig.json` strict con alias `@/*`; `typescript` y `vue-tsc` añadidos a devDeps. Migración gradual: nuevos archivos `.ts`; los `.js` existentes se quedan como están.
- [object Object]

## Required Specs
<!-- SPECS_START -->
- frontend-polish-spec
<!-- SPECS_END -->