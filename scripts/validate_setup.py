#!/usr/bin/env python
"""
Script de validación pre-inicio
Verifica que todo esté correctamente instalado y configurado
"""

import sys
import os
import json
from pathlib import Path

class ValidationReport:
    def __init__(self):
        self.checks = []
        self.issues = []
        self.warnings = []
    
    def check_python(self):
        """Verificar versión de Python"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.checks.append(f"✅ Python {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            self.issues.append(f"❌ Python 3.8+ requerido (tienes {version.major}.{version.minor})")
            return False
    
    def check_packages(self):
        """Verificar paquetes instalados"""
        required = [
            "fastapi", "uvicorn", "sqlalchemy", "pydantic", 
            "jose", "passlib", "librosa", "requests"
        ]
        
        missing = []
        for package in required:
            try:
                __import__(package)
                self.checks.append(f"✅ {package}")
            except ImportError:
                missing.append(package)
        
        if missing:
            self.issues.append(f"❌ Paquetes faltantes: {', '.join(missing)}")
            return False
        return True
    
    def check_directories(self):
        """Verificar estructura de directorios"""
        required_dirs = [
            "src/app",
            "src/app/core",
            "src/app/models",
            "src/app/routes",
            "src/app/services",
            "public/static",
            "music_storage"
        ]
        
        for dir_path in required_dirs:
            if os.path.exists(dir_path):
                self.checks.append(f"✅ Directorio: {dir_path}")
            else:
                self.issues.append(f"❌ Falta directorio: {dir_path}")
                return False
        
        return True
    
    def check_files(self):
        """Verificar archivos esenciales"""
        required_files = [
            "src/app/main.py",
            "src/app/core/config.py",
            "src/app/core/database.py",
            "src/.env",
            "public/index.html"
        ]
        
        for file_path in required_files:
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                self.checks.append(f"✅ Archivo: {file_path} ({size} bytes)")
            else:
                self.issues.append(f"❌ Falta archivo: {file_path}")
                return False
        
        return True
    
    def check_config(self):
        """Verificar configuración"""
        if os.path.isfile("src/.env"):
            with open("src/.env", "r") as f:
                env_content = f.read()
                if "DATABASE_URL" in env_content and "SECRET_KEY" in env_content:
                    self.checks.append("✅ Archivo .env configurado")
                    return True
                else:
                    self.warnings.append("⚠️ Archivo .env incompleto")
                    return True
        else:
            self.issues.append("❌ Archivo .env no encontrado")
            return False
    
    def run_all_checks(self):
        """Ejecutar todas las validaciones"""
        print("\n" + "="*60)
        print("🔍 Validación Pre-Inicio - MelodyBox")
        print("="*60 + "\n")
        
        print("Verificando configuración...\n")
        
        results = [
            ("Python", self.check_python()),
            ("Paquetes", self.check_packages()),
            ("Directorios", self.check_directories()),
            ("Archivos", self.check_files()),
            ("Configuración", self.check_config())
        ]
        
        print("\n📋 Resumen de verificaciones:")
        print("-" * 60)
        for check in self.checks:
            print(check)
        
        if self.warnings:
            print("\n⚠️ Advertencias:")
            for warning in self.warnings:
                print(warning)
        
        if self.issues:
            print("\n❌ Problemas encontrados:")
            for issue in self.issues:
                print(issue)
            print("\n" + "="*60)
            print("❌ Validación FALLIDA")
            print("="*60 + "\n")
            return False
        else:
            print("\n" + "="*60)
            print("✅ Validación EXITOSA - Listo para iniciar!")
            print("="*60 + "\n")
            print("Próximos pasos:")
            print("1. Ejecuta: python scripts/start_server.py")
            print("2. Abre: http://localhost:8001/docs")
            print("3. Registra un usuario")
            print("4. ¡Disfruta de MelodyBox! 🎵\n")
            return True

if __name__ == "__main__":
    validator = ValidationReport()
    success = validator.run_all_checks()
    sys.exit(0 if success else 1)
