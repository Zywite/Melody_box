#!/bin/bash
# Script para iniciar el servidor MelodyBox (Linux/Mac)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR" || exit 1

echo "============================================"
echo "  MelodyBox - Server"
echo "============================================"
echo ""
echo "Starting server on http://localhost:8001"
echo "API Docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================"
echo ""

if [ ! -d ".venv" ]; then
    echo "Error: No se encontro el entorno virtual (.venv)"
    echo "Ejecuta: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
