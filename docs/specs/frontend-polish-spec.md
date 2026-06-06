# Spec: frontend-polish-spec

Scope: feature

# Frontend Polish Spec

Items covered by the `frontend-polish` plan. New code is written in
TypeScript (gradual migration). Existing `.js` files stay as-is until
touched.

> **Status (post `performance-tuning` round):** Only item 8
> (TypeScript scaffolding) has shipped. Items 1–7 are still pending
> and remain in the `active` plan.

## 1. AddToPlaylistModal.vue

> **Status:** pending.

**Purpose**: One modal used everywhere the "add to playlist" action is
exposed. Removes the four `// TODO: Implement` stubs.

**API**:
- Props: `song: Song | null` (the song to add, or `null` to close).
- Emits: `close` (modal dismissed), `added` (playlist id chosen).
- Consumes `usePlaylistsStore` for the list and the `addSongToPlaylist`
  mutation.
- Empty state when the user has no playlists: shows a "Crear playlist"
  button that opens `CreatePlaylistModal` (already exists) and refreshes
  the list on close.

**Call sites**:
- `LibraryView.vue:231` — `showAddToPlaylist(song)`.
- `HomeView.vue:135` — `showAddToPlaylist(song)`.
- `SearchView.vue:90` — `showAddToPlaylist(song)`.
- `PlayerBar.vue:175` — `addToPlaylist()` (uses the current song from
  the player store).

## 2. SearchInput debounce

> **Status:** pending.

**Component**: `frontend/src/components/common/SearchInput.vue`.

- Internal `setTimeout` (300ms) + `clearTimeout` on each keystroke.
- Exposes a `search` event that fires with the debounced value.
- `v-model` is kept synchronous so the input still feels responsive.
- `clearSearch()` flushes the debounce and fires `search` immediately.
- Removes the duplicated CSS block (lines 38-105 and 106-149 both define
  the same selectors).

## 3. LibraryView virtual scroll

> **Status:** pending.

**Component**: `frontend/src/views/LibraryView.vue`.

- Replaces `v-for` over `filteredSongs` with `<VirtualList>` (already
  extracted for `FFTView`).
- `itemHeight` is **84 px** (matches `SongCard` artwork 56 px + padding
  14 px × 2 = 84 px). The 8 px gap is dropped; visual rhythm is
  preserved by an internal `margin-bottom` on the row.
- Pagination stays in the store: a single batch of 100 is fetched on
  mount; "load more" still appends in pages of 50 and the virtual list
  reuses the existing array. No special-casing needed.

## 4. PlaylistDetailView Map lookup

> **Status:** pending.

**Component**: `frontend/src/views/PlaylistDetailView.vue`.

- In `onMounted`, build `songMap = new Map(allSongs.map(s => [s.id, s]))`.
- `getSongData(songId)` becomes a single `songMap.get(songId)`.
- The fallback `{ id, title: 'Unknown', artist: 'Unknown' }` is kept.
- `allSongs` is kept as a ref (still needed to build the map and to
  pass into `playAll` / `shuffleAll`).

## 5. Vitest setup

> **Status:** pending.

**Files**:
- `frontend/vitest.config.ts` — jsdom env, alias `@` → `src`.
- `frontend/src/stores/__tests__/songs.spec.ts` — SWR cache hit (returns
  cached data within 30s), miss (refetches after stale), invalidate
  clears sessionStorage.
- `frontend/src/stores/__tests__/favorites.spec.ts` — optimistic add
  inserts locally, server call, success keeps it; failure removes
  local. Same for remove.
- `frontend/package.json` — add `test` script (`vitest run`) and dev
  deps `vitest`, `@vue/test-utils`, `jsdom`.

Mocks: stub `useApi` and `useAuthStore` with `vi.mock()`.

## 6. useApi 401 retry cap

> **Status:** pending.

**File**: `frontend/src/composables/useApi.js`.

- The current `_retry` boolean only blocks immediate double-fire. A
  persistent invalid token can still trigger one retry per request,
  which the server will keep rejecting. Cap retries at 1 with
  `_retryCount` and clear auth state as soon as the count is hit
  (instead of waiting for the second 401).

## 7. SearchView loading state

> **Status:** pending.

**File**: `frontend/src/views/SearchView.vue`.

- Local `isSearching` ref toggled around `api.searchSongs(q)`.
- A small spinner / "Buscando..." text appears next to the search input
  while in flight.
- Cleared in `finally`.

## 8. TypeScript scaffolding

> **Status:** done (shipped in the `performance-tuning` round, commit
> `8dbf6cb`).

**Files**:
- `frontend/tsconfig.json` — strict-ish (`strict: true`,
  `noImplicitAny: true`, `skipLibCheck: true`).
- `frontend/src/env.d.ts` — Vue SFC module declaration.
- `frontend/vite.config.js` → rename to `vite.config.ts`; add
  `vue-tsc` build step. Keep all existing plugins verbatim.
- New `.ts` files for stores and tests; `AddToPlaylistModal.vue` is
  the first typed component (with `<script setup lang="ts">`).