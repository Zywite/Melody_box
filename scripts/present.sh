#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR" || exit 1

IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "")

echo "============================================"
echo "  MelodyBox - Presentation Mode"
echo "============================================"
echo ""
echo "  Local:   http://localhost:8001"
if [ -n "$IP" ]; then
    echo "  Network: http://$IP:8001"
fi
echo ""
echo "  Press Ctrl+C to stop"
echo "============================================"
echo ""

docker compose up --build
