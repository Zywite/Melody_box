#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR" || exit 1

IP=$(hostname -I | awk '{print $1}')

echo "============================================"
echo "  MelodyBox - Modo Presentacion"
echo "============================================"
echo ""
echo "  Local:   http://localhost:8001"
echo "  Red:     http://$IP:8001"
echo ""
echo "  Presiona Ctrl+C para detener"
echo "============================================"
echo ""

docker compose up --build
