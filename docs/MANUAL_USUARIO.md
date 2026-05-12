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
  Server:   http://localhost:8001
  API Docs: http://localhost:8001/docs
  Press Ctrl+C to stop
==================================================
```

### Abrir la aplicación

En tu navegador ve a: **http://localhost:8001**

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
2. Para cada archivo aparece un campo de **título** (prellenado) y **artista**
3. Opcional: ingresa un **álbum** que aplica a todos los archivos
4. Haz click en **"Subir N archivos"**

### Método 2: Seleccionar archivos

1. Haz click en el área de upload para abrir el selector
2. Elige uno o más archivos
3. Sigue los mismos pasos que arriba

> Todos los archivos se suben en una sola petición. El análisis FFT (espectro de frecuencias) se encola automáticamente en segundo plano.

### Formatos aceptados

| Tipo | Extensiones |
|---|---|
| Audio | `.mp3`, `.wav`, `.flac`, `.ogg`, `.m4a` |
| Video | `.mp4`, `.mkv`, `.avi`, `.webm`, `.mov` |

---

## 5. Descargar desde YouTube

Ve a la sección **"Subir"** → pestaña **"YouTube"**.

1. Busca un video por nombre o artista
2. Selecciona el **formato** de salida (MP3, M4A, WAV, FLAC, MP4, etc.)
3. Selecciona la **calidad** (320kbps, 256kbps, 128kbps para audio; 1080p, 720p para video)
4. Opcional: personaliza **título** y **artista**
5. Haz click en **"Descargar"**
6. La descarga se procesa en segundo plano; la canción aparece automáticamente en la biblioteca

> Requiere `yt-dlp` instalado. En Docker ya viene incluido.

---

## 6. Biblioteca

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

## 7. Visualización FFT (Espectro de frecuencias)

MelodyBox puede analizar el espectro de frecuencias de tus canciones.

1. Reproduce una canción desde la biblioteca
2. Abre el **FFT Analyzer** desde el menú lateral o haciendo click en "Ver FFT"
3. Verás dos gráficos:
   - **Espectro** — Frecuencias en tiempo real (bass, mid, treble)
   - **Espectrograma** — Evolución del espectro en el tiempo
4. El análisis se ejecuta en segundo plano; si es la primera vez, espera unos segundos

> El análisis FFT se encola automáticamente al subir archivos y se procesa en un worker asíncrono.

---

## 9. Buscar

Ve a **"Buscar"** en el menú lateral.

1. Escribe en la barra de búsqueda
2. Los resultados aparecen automáticamente (después de 2 caracteres)
3. Busca por **título**, **artista** o **álbum**
4. Haz click en cualquier resultado para reproducirlo

---

## 10. Playlists

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

1. Desde la biblioteca, pasa el mouse sobre una canción
2. Haz click en el botón **"Agregar a playlist"**
3. Selecciona la playlist deseada del menú
4. La canción se agrega automáticamente

### Eliminar una playlist

> Se hace desde la API.

```bash
curl -X DELETE http://localhost:8001/playlists/{playlist_id} \
  -H "Authorization: Bearer {token}"
```

---

## 11. Favoritos

### Marcar como favorito

1. En la biblioteca, pasa el mouse sobre una canción
2. Haz click en el **corazón** (♡) que aparece
3. El corazón se llena () indicando que es favorito
4. Vuelve a hacer click para quitarlo de favoritos

También puedes marcar/desmarcar favoritos desde la barra de reproducción mientras la canción está sonando.

---

## 12. Acceder desde otro dispositivo

1. Asegúrate de que ambos dispositivos estén en la **misma red WiFi**
2. En tu laptop, averigua tu IP:
   - Windows: `ipconfig` → busca "Dirección IPv4"
   - Linux/Mac: `ip addr` o `ifconfig`
3. En el otro dispositivo, abre el navegador y ve a:
   ```
   http://TU_IP:8001
   ```
4. Regístrate o inicia sesión normalmente

> **Tip:** Si la red bloquea la comunicación entre dispositivos, crea un hotspot desde tu celular y conecta ambos ahí.

---

## 13. Cerrar sesión

Haz click en **"Cerrar sesión"** en la parte inferior del menú lateral.

---

## 14. Atajos y consejos

- **Modo oscuro** — Usa el botón de tema (/) en el menú lateral para alternar
- **Ctrl+Shift+R** — Hard refresh si la interfaz no se actualiza
- **Arrastra múltiples archivos** — Cada archivo tiene su propio título y artista
- **Barra de progreso** — Haz click en cualquier punto para saltar
- **Volumen** — Click en el icono  para silenciar/activar
- **FFT Analyzer** — Disponible desde el menú lateral para cualquier canción reproducida
