# Spec: admin-system-spec

Scope: feature

# Spec: admin-system-spec

## Descripción
Sistema de administración con roles para MelodyBox. Permite gestionar usuarios y contenido desde un panel exclusivo para admins.

## Requisitos Funcionales

### RF1 - Modelo de Usuario con Roles
- Campo `role` de tipo Enum: `user` (default) | `admin`
- Campo `is_active` se verifica en autenticación (usuarios desactivados no pueden loguearse)

### RF2 - Admin por Defecto
- Al iniciar el servidor, si no existe un admin, se crea uno automáticamente
- Credenciales configurables via `.env`: `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_USERNAME`
- Fallback: `admin@melodybox.com` / `admin123` / `Admin`

### RF3 - Panel de Administración (Backend)
- `GET /admin/users` - Listar todos los usuarios con paginación y búsqueda
- `PATCH /admin/users/{id}` - Editar username/email de un usuario
- `DELETE /admin/users/{id}` - Eliminar usuario y sus datos asociados
- `PATCH /admin/users/{id}/toggle-active` - Activar/desactivar usuario
- `GET /admin/users/{id}/stats` - Estadísticas del usuario (canciones, playlists, espacio)
- `GET /admin/songs` - Listar todas las canciones (de todos los usuarios)
- `DELETE /admin/songs/{id}` - Eliminar cualquier canción
- `GET /admin/playlists` - Listar todas las playlists
- `DELETE /admin/playlists/{id}` - Eliminar cualquier playlist

### RF4 - Seguridad
- Dependencia `require_admin` que verifica `current_user.role == 'admin'`
- Todas las rutas `/admin/*` protegidas con `require_admin`
- El admin por defecto no se puede eliminar desde la API

### RF5 - Panel de Administración (Frontend)
- Link "Admin" en el sidebar, visible solo para usuarios con role `admin`
- Ruta `/admin/users`: tabla con usuarios (username, email, activo, fecha, acciones)
  - Modal de edición (username, email)
  - Toggle activar/desactivar
  - Botón eliminar con confirmación
  - Búsqueda y paginación
- Ruta `/admin/content`: tabs de Songs y Playlists
  - Lista de todas las canciones con indicador de usuario propietario y botón eliminar
  - Lista de todas las playlists con indicador de usuario propietario y botón eliminar
- Ruta `/admin/stats` o integrado en users: estadísticas globales y por usuario

### RF6 - Protección de Rutas Frontend
- Vue Router guard: si ruta empieza con `/admin` y `isAdmin` es falso, redirigir a home
- Si no está autenticado, redirigir a login

## Consideraciones Técnicas
- Usar SQLAlchemy enum para el campo `role`
- JWT debe incluir `role` en el payload
- Cache de usuario debe incluir/invalidar role
- Admin por defecto se crea en el lifespan de FastAPI
- Frontend: usar `localStorage` para persistir role junto con token