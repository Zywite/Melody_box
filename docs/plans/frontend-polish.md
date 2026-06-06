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
- [object Object]
- [object Object]
- [object Object]
- [object Object]
- [object Object]
- [object Object]
- [object Object]
- [object Object]
- [object Object]

## Required Specs
<!-- SPECS_START -->
- frontend-polish-spec
<!-- SPECS_END -->