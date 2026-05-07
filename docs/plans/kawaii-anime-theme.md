---
plan name: kawaii-anime-theme
plan description: Kawaii anime aesthetic
plan status: done
---

## Idea
Transform MelodyBox frontend to cute/kawaii anime aesthetic with pastel colors (sakura pink, mint green), sakura petal falling effects, rounder corners (24-32px), lighter theme, and cute typography (Nunito/Mochiy Pop)

## Implementation
- Update frontend/src/assets/main.css: Replace dark theme CSS variables with pastel palette (--bg-primary: #fff5f7, --bg-secondary: #ffeef2, --accent: #ff9ebb, etc.)
- Update frontend/src/assets/main.css: Increase border radius globally (--radius: 24px, --radius-lg: 32px, --radius-xl: 40px)
- Update frontend/tailwind.config.js: Add pastel color palette matching main.css variables
- Update frontend/tailwind.config.js: Add cute fonts (Nunito, Mochiy Pop P One, Yomogi) and update fontFamily config
- Update frontend/src/assets/main.css: Change Google Fonts import to include Nunito, Mochiy Pop P One instead of DM Sans/Space Grotesk
- Create frontend/src/components/effects/SakuraPetal.vue: New component for falling sakura petal animation using CSS/Canvas
- Update frontend/src/App.vue: Add SakuraPetal component with conditional rendering (only in light theme)
- Update frontend/src/components/layout/AppSidebar.vue: Apply pastel hover states, rounder corners (24px), softer glass effects
- Update frontend/src/components/player/PlayerBar.vue: Rounder artwork (24px radius), pastel progress bar, cute play button with bounce animation
- Update frontend/src/components/common/SongCard.vue: Rounder artwork, pastel hover states, cute playing animation
- Update frontend/src/components/common/PlaylistCard.vue: Rounder cover (24px+), pastel gradient overlay, bouncy hover scale(1.05)
- Update frontend/src/views/AuthView.vue: Lighter glass panels, pastel gradient top border, rounder inputs (24px), cute button styling
- Update frontend/src/views/HomeView.vue: Pastel stat cards, rounder corners, cute empty state with kawaii illustrations
- Update frontend/src/views/LibraryView.vue: Rounder tabs (pill shape 9999px), pastel filter buttons, cute empty states
- Add bouncy animations: Create spring-like transitions in main.css (transform: scale() with cubic-bezier(.34,1.56,.64,1))
- Add sakura petal keyframes in main.css: floating, rotating, fade-out animation
- Update all components to use new pastel variables instead of dark theme colors
- Test: Run npm run dev to verify visual changes look correct
- Test: Verify sakura petals animation performance (check for jank on lower-end devices)

## Required Specs
<!-- SPECS_START -->
<!-- SPECS_END -->