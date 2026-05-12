#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR" || exit 1

echo "============================================"
echo "  MelodyBox - Worker (ARQ)"
echo "============================================"
echo ""

if [ ! -d ".venv" ]; then
    echo "Error: No se encontro el entorno virtual (.venv)"
    exit 1
fi

source .venv/bin/activate
cd src || exit 1
echo "Starting ARQ worker..."
echo ""
python -m arq worker.WorkerSettings
