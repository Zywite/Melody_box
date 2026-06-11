-- PostgreSQL setup script (local development)
-- Run as superuser (postgres)
-- Local credentials in .env: postgres:saki7089@localhost:5432/Spotofy
-- Docker uses credentials from docker-compose.yml

-- Create the database if it does not exist (psql)
SELECT 'CREATE DATABASE "Spotofy"'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'Spotofy')\gexec
