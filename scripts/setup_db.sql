-- Script de configuración para PostgreSQL
-- Ejecutar como superusuario (postgres)

-- Crear usuario
CREATE USER spotify_user WITH PASSWORD 'spotify_password';

-- Crear base de datos
CREATE DATABASE spotify_local OWNER spotify_user;

-- Conectar a la base de datos
\c spotify_local

-- Dar permisos
GRANT ALL PRIVILEGES ON DATABASE spotify_local TO spotify_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO spotify_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO spotify_user;

-- Verificar
SELECT * FROM information_schema.tables WHERE table_schema = 'public';
