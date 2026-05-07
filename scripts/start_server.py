#!/usr/bin/env python
"""
Script para iniciar el servidor MelodyBox
Soporta opciones de línea de comandos y manejo graceful de señales.
"""

import sys
import os
import argparse
import subprocess
import logging
import socket
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_venv_python(project_dir):
    """Buscar ejecutable de Python en el entorno virtual (cross-platform)"""
    venv_dir = Path(project_dir) / '.venv'

    if os.name == 'nt':  # Windows
        python_exe = venv_dir / 'Scripts' / 'python.exe'
    else:  # Linux/Mac
        python_exe = venv_dir / 'bin' / 'python'

    return python_exe if python_exe.exists() else None

def is_port_available(host, port):
    """Verificar si el puerto está disponible"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False

def main():
    parser = argparse.ArgumentParser(description='Iniciar servidor MelodyBox')
    parser.add_argument('--host', default='0.0.0.0', help='Host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8001, help='Puerto (default: 8001)')
    parser.add_argument('--no-reload', action='store_true', help='Desactivar auto-reload (modo producción)')
    parser.add_argument('--config', help='Ruta al archivo .env (opcional)')
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    src_dir = project_dir / 'src'

    venv_python = find_venv_python(project_dir)
    if not venv_python:
        logger.error("No se encontro el entorno virtual (.venv)")
        logger.info("Ejecuta: python -m venv .venv && pip install -r requirements.txt")
        sys.exit(1)

    if not is_port_available(args.host if args.host != '0.0.0.0' else '127.0.0.1', args.port):
        logger.error(f"El puerto {args.port} ya está en uso")
        logger.info(f"Usa --port para especificar otro puerto")
        sys.exit(1)

    env = os.environ.copy()
    if args.config:
        env['ENV_FILE'] = str(Path(args.config).absolute())

    logger.info("=" * 50)
    logger.info("  MelodyBox")
    logger.info("=" * 50)
    logger.info(f"  Server:   http://localhost:{args.port}")
    logger.info(f"  API Docs: http://localhost:{args.port}/docs")
    logger.info(f"  Reload:   {'disabled' if args.no_reload else 'enabled'}")
    logger.info("  Press Ctrl+C to stop")
    logger.info("=" * 50)

    cmd = [
        str(venv_python), "-m", "uvicorn",
        "app.main:app",
        "--host", args.host,
        "--port", str(args.port)
    ]

    if not args.no_reload:
        cmd.append("--reload")

    try:
        process = subprocess.run(cmd, cwd=str(src_dir), env=env)
    except KeyboardInterrupt:
        logger.info("\nCerrando servidor...")
        sys.exit(0)

if __name__ == "__main__":
    main()
