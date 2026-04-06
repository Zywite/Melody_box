# 🚀 Instalación y Configuración de PostgreSQL — MelodyBox

## Opción 1: Windows (Recomendado)

### Paso 1: Descargar PostgreSQL
1. Ve a https://www.postgresql.org/download/windows/
2. Descarga la versión más reciente (15 o superior)
3. Ejecuta el instalador

### Paso 2: Instalación
- **Nombre de usuario**: postgres (por defecto)
- **Contraseña**: Recuerda esta contraseña
- **Puerto**: 5432 (por defecto)
- **Componentes**: Selecciona PostgreSQL Server, pgAdmin, Command Line Tools

### Paso 3: Verificar instalación
```bash
# En PowerShell o CMD
psql --version
psql -U postgres
```

### Paso 4: Crear base de datos
Opción A - Con PgAdmin (Interfaz gráfica):
1. Abre pgAdmin
2. Conecta con servidor local
3. Click derecho en "Databases" → "Create" → "Database"
4. Nombre: `spotify_local`
5. Owner: `postgres`

Opción B - Con línea de comandos:
```bash
# Conectar como superusuario
psql -U postgres

# En la terminal psql, ejecutar:
CREATE USER spotify_user WITH PASSWORD 'spotify_password';
CREATE DATABASE spotify_local OWNER spotify_user;
GRANT ALL PRIVILEGES ON DATABASE spotify_local TO spotify_user;
\q
```

## Verificar conexión desde la aplicación

### Método 1: Usando el .env
El archivo `.env` ya tiene la configuración:
```
DATABASE_URL=postgresql://spotify_user:spotify_password@localhost/spotify_local
```

### Método 2: Prueba de conexión
```python
# En Python
from sqlalchemy import create_engine
engine = create_engine("postgresql://spotify_user:spotify_password@localhost/spotify_local")
connection = engine.connect()
print("Conexión exitosa!")
connection.close()
```

## Alternativas a PostgreSQL Local

Si no quieres instalar PostgreSQL localmente:

### SQLite (Sin instalación)
Cambiar `.env`:
```
DATABASE_URL=sqlite:///./spotify.db
```

### Usar Docker
```bash
docker run --name spotify-postgres -e POSTGRES_PASSWORD=spotify_password -p 5432:5432 -d postgres:15
```

---

**Próximos pasos**: Una vez configurado, ejecuta el servidor con:
```bash
cd backend
python -m app.main
```

El servidor estará en: http://localhost:8000
API docs: http://localhost:8000/docs
