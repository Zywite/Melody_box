---
plan name: dark-mode-toggle
plan description: Add dark mode toggle
plan status: done
---

## Idea
Add dark mode toggle with kawaii accent colors preserved, save user preference to localStorage, and update Tailwind config

## Implementation
- Add dark theme CSS variables in main.css using [data-theme='dark'] selector with dark backgrounds (#0a0a0a, #121212)
- Preserve kawaii accent colors (pink/purple) in dark mode
- Create ThemeToggle.vue component with cute sun/moon icon animation
- Add theme toggle to AppSidebar.vue footer next to user info
- Implement theme switching logic with localStorage persistence
- Update Tailwind config to support dark theme colors
- Add smooth transition when switching themes
- Test both themes work correctly with all components

## Required Specs
<!-- SPECS_START -->
<!-- SPECS_END -->