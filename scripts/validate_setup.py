#!/usr/bin/env python
"""
Pre-startup validation script.
Verifies that everything is properly installed and configured.
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent


class ValidationReport:
    def __init__(self):
        self.checks = []
        self.issues = []
        self.warnings = []

    def check_python(self):
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.checks.append(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
            return True
        self.issues.append(f"[ERROR] Python 3.8+ required (you have {version.major}.{version.minor})")
        return False

    def check_packages(self):
        required = ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "jwt", "bcrypt", "yt_dlp"]
        missing = []
        for package in required:
            try:
                __import__(package)
                self.checks.append(f"[OK] {package}")
            except ImportError:
                missing.append(package)
        if missing:
            self.issues.append(f"[ERROR] Missing packages: {', '.join(missing)}")
            return False
        return True

    def check_directories(self):
        required_dirs = [
            "src/app",
            "src/app/core",
            "src/app/models",
            "src/app/routes",
            "src/app/services",
            "frontend/src",
            "data/music",
        ]
        for dir_path in required_dirs:
            full = PROJECT_DIR / dir_path
            if full.is_dir():
                self.checks.append(f"[OK] Directory: {dir_path}")
            else:
                self.issues.append(f"[ERROR] Missing directory: {dir_path}")
                return False
        return True

    def check_files(self):
        required_files = [
            "src/app/main.py",
            "src/app/core/config.py",
            "src/app/core/database.py",
            ".env",
            "requirements.txt",
        ]
        for file_path in required_files:
            full = PROJECT_DIR / file_path
            if full.is_file():
                self.checks.append(f"[OK] File: {file_path} ({full.stat().st_size} bytes)")
            else:
                self.issues.append(f"[ERROR] Missing file: {file_path}")
                return False
        return True

    def check_config(self):
        env_file = PROJECT_DIR / ".env"
        if env_file.is_file():
            env_content = env_file.read_text()
            if "DATABASE_URL" in env_content and "SECRET_KEY" in env_content:
                self.checks.append("[OK] .env file configured")
                return True
            self.warnings.append("[WARN] .env file incomplete")
            return True
        self.issues.append("[ERROR] .env file not found")
        return False

    def check_frontend(self):
        frontend_package = PROJECT_DIR / "frontend" / "package.json"
        if frontend_package.is_file():
            self.checks.append("[OK] Frontend configured (package.json)")
            return True
        self.warnings.append("[WARN] Frontend not found")
        return True

    def run_all_checks(self):
        print("\n" + "=" * 60)
        print("Pre-Startup Validation - MelodyBox")
        print("=" * 60 + "\n")

        print("Checking configuration...\n")

        self.check_python()
        self.check_packages()
        self.check_directories()
        self.check_files()
        self.check_config()
        self.check_frontend()

        print("\nCheck summary:")
        print("-" * 60)
        for check in self.checks:
            print(check)

        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(warning)

        if self.issues:
            print("\nIssues found:")
            for issue in self.issues:
                print(issue)
            print("\n" + "=" * 60)
            print("Validation FAILED")
            print("=" * 60 + "\n")
            return False

        print("\n" + "=" * 60)
        print("Validation PASSED - Ready to start!")
        print("=" * 60 + "\n")
        print("Next steps:")
        print("1. Run: python scripts/start_server.py")
        print("2. Open: http://localhost:8001/docs")
        print("3. Register a user")
        print("4. Enjoy MelodyBox!\n")
        return True


if __name__ == "__main__":
    validator = ValidationReport()
    success = validator.run_all_checks()
    sys.exit(0 if success else 1)
