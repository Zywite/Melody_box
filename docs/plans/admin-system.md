---
plan name: admin-system
plan description: Admin user & content management
plan status: active
---

## Idea
Add an admin role system to MelodyBox with an auto-created default admin account, role-based access control, and a full admin panel in the frontend sidebar for managing users (CRUD, activate/deactivate) and content (songs, playlists). The admin is created on first server startup with credentials from .env or defaults.

## Implementation
- 1. Add `role` field (Enum: 'user' | 'admin') to User model + migration logic
- 2. Create default admin on startup (read credentials from .env, fallback to admin@melodybox.com / admin123)
- 3. Check `is_active` in get_current_user dependency (reject disabled users)
- 4. Create admin-only dependency `require_admin` that checks current_user.role == 'admin'
- 5. Create backend admin routes: GET /admin/users (list), PATCH /admin/users/{id} (edit), DELETE /admin/users/{id}, PATCH /admin/users/{id}/toggle-active, GET /admin/users/{id}/stats
- 6. Create backend admin routes for content: GET /admin/songs, DELETE /admin/songs/{id}, GET /admin/playlists, DELETE /admin/playlists/{id}
- 7. Add frontend auth store: persist role, expose isAdmin getter
- 8. Add admin nav link in AppSidebar.vue (visible only when isAdmin)
- 9. Create AdminUsersView.vue (table with search, edit modal, activate/deactivate toggle, delete)
- 10. Create AdminContentView.vue (songs & playlists tabs with delete)
- 11. Create AdminStatsView.vue or integrate stats into users view
- 12. Add Vue Router guard for /admin routes (requires admin role)
- 13. Update tests for new role + admin endpoints

## Required Specs
<!-- SPECS_START -->
- clean-code-spec
- admin-system-spec
<!-- SPECS_END -->