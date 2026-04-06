#!/usr/bin/env python
"""
Script para iniciar el servidor MelodyBox
"""

import sys
import os
import subprocess

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    src_dir = os.path.join(project_dir, 'src')
    venv_python = os.path.join(project_dir, '.venv', 'Scripts', 'python.exe')

    if not os.path.exists(venv_python):
        print("Error: No se encontro el entorno virtual (.venv)")
        print("Ejecuta: python -m venv .venv  &&  .venv\\Scripts\\activate  &&  pip install -r requirements.txt")
        sys.exit(1)

    print("=" * 50)
    print("  MelodyBox")
    print("=" * 50)
    print("  Server:   http://localhost:8001")
    print("  API Docs: http://localhost:8001/docs")
    print("  Press Ctrl+C to stop")
    print("=" * 50)
    print()

    subprocess.run([
        venv_python, "-m", "uvicorn",
        "app.main:app", "--reload",
        "--host", "0.0.0.0", "--port", "8001"
    ], cwd=src_dir)

if __name__ == "__main__":
    main()
