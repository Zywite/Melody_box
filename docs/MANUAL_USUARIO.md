# Manual de Usuario — MelodyBox

## 1. Primeros pasos

### Iniciar el servidor

```bash
python scripts/start_server.py
```

Verás este mensaje:

```
==================================================
  MelodyBox
==================================================
  Server:   http://localhost:8000
  API Docs: http://localhost:8000/docs
  Press Ctrl+C to stop
==================================================
```

### Abrir la aplicación

En tu navegador ve a: **http://localhost:8000**

---

## 2. Registro e inicio de sesión

Al abrir la app verás la pantalla de login.

### Crear cuenta

1. Haz click en **"Regístrate gratis"**
2. Completa los campos:
   - **Usuario** — Tu nombre de pantalla
   - **Email** — Tu correo electrónico
   - **Contraseña** — Mínimo 6 caracteres
   - **Confirmar contraseña** — Repite la contraseña
3. Haz click en **"Crear cuenta"**
4. Serás redirigido al login

### Iniciar sesión

1. Ingresa tu **email** y **contraseña**
2. Haz click en **"Iniciar sesión"**
3. Si las credenciales son correctas, entrarás a la app

---

## 3. Página de inicio

Es la primera página que ves al entrar. Muestra:

- **Panel de estadísticas** — Cantidad de canciones, videos y playlists
- **Reproduciendo ahora** — Muestra la canción/video que estás reproduciendo
- **Reproductor de video** — Aparece automáticamente cuando reproduces un video

---

## 4. Subir archivos

Ve a la sección **"Subir"** en el menú lateral.

### Método 1: Arrastrar y soltar

1. Arrastra archivos desde tu explorador al área punteada
2. Se te pedirá un **artista/creador por defecto** para todos los archivos
3. Se te pedirá un **álbum/colección** (opcional)
4. Para cada archivo se pedirá el **título** (viene prellenado con el nombre del archivo)

### Método 2: Seleccionar archivos

1. Haz click en **"Seleccionar archivos"**
2. Elige uno o más archivos
3. Sigue los mismos pasos que arriba

### Formatos aceptados

| Tipo | Extensiones |
|---|---|
| Audio | `.mp3`, `.wav`, `.flac`, `.ogg`, `.m4a` |
| Video | `.mp4`, `.mkv`, `.avi`, `.webm`, `.mov` |

---

## 5. Biblioteca

Ve a **"Biblioteca"** en el menú lateral.

### Ver todo el contenido

La lista muestra todos tus archivos subidos con:
- Icono de tipo (audio o video)
- Título y artista
- Duración
- Botón de **reproducir** (▶)
- Botón de **eliminar** (🗑️)

### Filtrar por tipo

Usa las pestañas superiores:
- **Todo** — Muestra audio y video
- **Audio** — Solo canciones
- **Video** — Solo videos

### Eliminar un archivo

1. Pasa el mouse sobre el archivo
2. Haz click en el icono 🗑️
3. Confirma la eliminación

> El archivo se elimina tanto de la base de datos como del disco.

---

## 6. Reproducir contenido

### Reproducir una canción

1. En la biblioteca, haz click en el archivo o en el botón ▶
2. Aparecerá la **barra de reproducción** en la parte inferior
3. La canción comienza a reproducirse automáticamente

### Reproducir un video

1. Haz click en el archivo de video
2. Se abrirá el **reproductor de video** en la página de inicio
3. El video se reproduce con controles completos

### Controles del reproductor

| Control | Función |
|---|---|
| ⏮ Anterior | Canción anterior en la lista |
| ▶ / ⏸ | Reproducir / Pausar |
| ⏭ Siguiente | Siguiente canción |
| Barra de progreso | Click para saltar a ese punto |
| 🔊 Volumen | Slider para ajustar |
| Silenciar | Click en el icono de volumen |

### Lista de reproducción

Al reproducir un archivo, toda la biblioteca se carga como playlist. Puedes avanzar y retroceder entre canciones con los botones anterior/siguiente.

---

## 7. Buscar

Ve a **"Buscar"** en el menú lateral.

1. Escribe en la barra de búsqueda
2. Los resultados aparecen automáticamente (después de 2 caracteres)
3. Busca por **título**, **artista** o **álbum**
4. Haz click en cualquier resultado para reproducirlo

---

## 8. Playlists

Ve a **"Playlists"** en el menú lateral.

### Crear una playlist

1. Haz click en **"Nueva playlist"**
2. Ingresa el **nombre**
3. Ingresa la **descripción** (opcional)
4. La playlist aparece en la lista

### Ver una playlist

1. Haz click en la tarjeta de la playlist
2. Se muestran las canciones que contiene
3. Puedes reproducirlas desde ahí

### Agregar canciones a una playlist

> Actualmente se hace desde la API. En futuras versiones se agregará desde la interfaz.

```bash
# Ejemplo con curl
curl -X POST http://localhost:8000/playlists/{playlist_id}/songs \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"song_id": "{song_id}"}'
```

### Eliminar una playlist

> Se hace desde la API.

```bash
curl -X DELETE http://localhost:8000/playlists/{playlist_id} \
  -H "Authorization: Bearer {token}"
```

---

## 9. Favoritos

> Actualmente se gestiona desde la API. En futuras versiones se agregará interfaz.

```bash
# Agregar a favoritos
curl -X POST http://localhost:8000/favorites \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"song_id": "{song_id}"}'

# Ver favoritos
curl http://localhost:8000/favorites \
  -H "Authorization: Bearer {token}"

# Quitar de favoritos
curl -X DELETE http://localhost:8000/favorites/{song_id} \
  -H "Authorization: Bearer {token}"
```

---

## 10. Acceder desde otro dispositivo

1. Asegúrate de que ambos dispositivos estén en la **misma red WiFi**
2. En tu laptop, averigua tu IP:
   - Windows: `ipconfig` → busca "Dirección IPv4"
   - Linux/Mac: `ip addr` o `ifconfig`
3. En el otro dispositivo, abre el navegador y ve a:
   ```
   http://TU_IP:8000
   ```
4. Regístrate o inicia sesión normalmente

> **Tip:** Si la red bloquea la comunicación entre dispositivos, crea un hotspot desde tu celular y conecta ambos ahí.

---

## 11. Cerrar sesión

Haz click en **"Cerrar sesión"** en la parte inferior del menú lateral.

---

## Atajos y consejos

- **Ctrl+Shift+R** — Hard refresh si la interfaz no se actualiza
- **Arrastra múltiples archivos** — Se pide el artista una sola vez para todos
- **Barra de progreso** — Haz click en cualquier punto para saltar
- **Volumen** — Click en el icono 🔊 para silenciar/activar
