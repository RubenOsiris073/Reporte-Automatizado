#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script para Sistema Empresarial de Análisis de Ventas
===========================================================

Script de instalación y configuración del sistema refactorizado.
Incluye verificación de dependencias, configuración automática y validaciones.

Uso:
    python setup.py install          # Instalación completa
    python setup.py develop          # Instalación en modo desarrollo
    python setup.py verify           # Solo verificar sistema
    python setup.py check-deps       # Verificar dependencias
    python setup.py configure        # Configuración interactiva
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from setuptools import setup, find_packages, Command
from setuptools.command.install import install
from setuptools.command.develop import develop

# =============================================================================
# METADATA DEL PROYECTO
# =============================================================================

PROJECT_NAME = "sistema-ventas-empresarial"
VERSION = "2.0.0"
DESCRIPTION = "Sistema profesional de análisis de ventas con arquitectura modular"
AUTHOR = "Sistema Empresarial de Ventas"
AUTHOR_EMAIL = "admin@sistema-ventas.com"
URL = "https://github.com/tu-usuario/sistema-ventas"

# Directorio base del proyecto
BASE_DIR = Path(__file__).parent.absolute()

# =============================================================================
# DEPENDENCIAS
# =============================================================================

INSTALL_REQUIRES = [
    # Análisis de datos
    'pandas>=1.5.0',
    'numpy>=1.21.0',

    # Requests para APIs HTTP
    'requests>=2.28.0',

    # Monitoreo del sistema
    'psutil>=5.9.0',

    # Google Sheets integration
    'gspread>=5.7.0',
    'google-auth>=2.15.0',
    'google-auth-oauthlib>=0.8.0',
    'google-auth-httplib2>=0.1.0',

    # Dependencias adicionales para Google Sheets
    'oauth2client>=4.1.3',
]

EXTRAS_REQUIRE = {
    'dev': [
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
        'black>=22.0.0',
        'isort>=5.10.0',
        'flake8>=5.0.0',
        'mypy>=0.991',
    ],
    'docs': [
        'sphinx>=5.0.0',
        'sphinx-rtd-theme>=1.0.0',
    ],
    'excel': [
        'openpyxl>=3.0.0',
        'xlsxwriter>=3.0.0',
    ]
}

# =============================================================================
# COMANDOS PERSONALIZADOS
# =============================================================================

class VerifyCommand(Command):
    """Comando personalizado para verificar el sistema."""

    description = 'Verificar instalación y configuración del sistema'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Ejecuta verificación completa del sistema."""
        print("Verificando Sistema Empresarial de Análisis de Ventas...")
        print("=" * 60)

        # Verificar Python
        self._check_python_version()

        # Verificar dependencias
        self._check_dependencies()

        # Verificar estructura de archivos
        self._check_file_structure()

        # Verificar configuración
        self._check_configuration()

        # Verificar permisos
        self._check_permissions()

        print("\nVerificación completada!")

    def _check_python_version(self):
        """Verifica versión de Python."""
        print("Verificando versión de Python...")

        if sys.version_info < (3, 8):
            print("ERROR: Se requiere Python 3.8 o superior")
            print(f"   Versión actual: {sys.version}")
            sys.exit(1)
        else:
            print(f"Python {sys.version.split()[0]} - OK")

    def _check_dependencies(self):
        """Verifica dependencias instaladas."""
        print("\n📦 Verificando dependencias...")

        missing_deps = []
        for dep in INSTALL_REQUIRES:
            package_name = dep.split('>=')[0].split('==')[0]
            try:
                __import__(package_name.replace('-', '_'))
                print(f"[OK] {package_name} - Instalado")
            except ImportError:
                missing_deps.append(package_name)
                print(f"[ERROR] {package_name} - Faltante")

        if missing_deps:
            print(f"\nDependencias faltantes: {', '.join(missing_deps)}")
            print("   Ejecute: pip install -r requirements.txt")
        else:
            print("Todas las dependencias están instaladas")

    def _check_file_structure(self):
        """Verifica estructura de archivos del proyecto."""
        print("\n📁 Verificando estructura de archivos...")

        required_files = [
            'requirements.txt',
            'run.py',
            'sistema_ventas/__init__.py',
            'sistema_ventas/main.py',
            'sistema_ventas/config/__init__.py',
            'sistema_ventas/core/__init__.py',
            'sistema_ventas/services/__init__.py',
            'sistema_ventas/utils/__init__.py',
            'sistema_ventas/factories/__init__.py',
            'sistema_ventas/models/__init__.py',
        ]

        missing_files = []
        for file_path in required_files:
            if (BASE_DIR / file_path).exists():
                print(f"[OK] {file_path}")
            else:
                missing_files.append(file_path)
                print(f"[ERROR] {file_path} - Faltante")

        if missing_files:
            print(f"\nArchivos faltantes: {len(missing_files)}")
        else:
            print("Estructura de archivos completa")

    def _check_configuration(self):
        """Verifica configuración del sistema."""
        print("\nVerificando configuración...")

        # Verificar credentials.json
        credentials_file = BASE_DIR / 'credentials.json'
        if credentials_file.exists():
            print("[OK] credentials.json - Encontrado")
            try:
                with open(credentials_file) as f:
                    creds = json.load(f)
                    if 'client_email' in creds and 'private_key' in creds:
                        print("[OK] credentials.json - Estructura válida")
                    else:
                        print("[WARN] credentials.json - Estructura incompleta")
            except json.JSONDecodeError:
                print("[ERROR] credentials.json - Formato JSON inválido")
        else:
            print("[WARN] credentials.json - No encontrado")
            print("   Copie credentials.json.example y configure sus credenciales")

        # Verificar variables de entorno
        env_vars = ['SMTP_SERVER', 'SMTP_USER', 'FROM_EMAIL']
        for var in env_vars:
            if os.getenv(var):
                print(f"[OK] {var} - Configurado")
            else:
                print(f"[WARN] {var} - No configurado (usando valores por defecto)")

    def _check_permissions(self):
        """Verifica permisos de archivos."""
        print("\n🔐 Verificando permisos...")

        # Verificar permisos de escritura en directorios clave
        dirs_to_check = ['logs', 'reports', 'temp', 'data']

        for dir_name in dirs_to_check:
            dir_path = BASE_DIR / dir_name
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    print(f"[OK] {dir_name}/ - Creado")
                except PermissionError:
                    print(f"[ERROR] {dir_name}/ - Sin permisos de escritura")
            else:
                if os.access(dir_path, os.W_OK):
                    print(f"[OK] {dir_name}/ - Permisos OK")
                else:
                    print(f"[ERROR] {dir_name}/ - Sin permisos de escritura")


class CheckDepsCommand(Command):
    """Comando para verificar solo dependencias."""

    description = 'Verificar solo dependencias del sistema'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Verifica solo las dependencias."""
        verify_cmd = VerifyCommand(self.distribution)
        verify_cmd._check_python_version()
        verify_cmd._check_dependencies()


class ConfigureCommand(Command):
    """Comando para configuración interactiva."""

    description = 'Configuración interactiva del sistema'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Configuración interactiva del sistema."""
        print("🔧 Configuración Interactiva del Sistema")
        print("=" * 40)

        # Configurar Google Sheets
        self._configure_google_sheets()

        # Configurar Email
        self._configure_email()

        # Crear directorios
        self._create_directories()

        print("\n✅ Configuración completada!")
        print("Puede ejecutar el sistema con: python run.py")

    def _configure_google_sheets(self):
        """Configura Google Sheets."""
        print("\n📊 Configuración de Google Sheets")
        print("-" * 30)

        credentials_file = BASE_DIR / 'credentials.json'
        if not credentials_file.exists():
            print("⚠️  credentials.json no encontrado")

            choice = input("¿Desea crear un archivo de ejemplo? (y/n): ")
            if choice.lower() == 'y':
                example_file = BASE_DIR / 'credentials.json.example'
                if example_file.exists():
                    import shutil
                    shutil.copy(example_file, credentials_file)
                    print("✅ credentials.json creado desde ejemplo")
                    print("   ⚠️  IMPORTANTE: Edite el archivo con sus credenciales reales")
                else:
                    print("❌ credentials.json.example no encontrado")
        else:
            print("✅ credentials.json ya existe")

    def _configure_email(self):
        """Configura email."""
        print("\n📧 Configuración de Email")
        print("-" * 25)

        env_file = BASE_DIR / '.env'

        if input("¿Configurar variables de email? (y/n): ").lower() == 'y':
            smtp_server = input("SMTP Server (default: smtp-relay.brevo.com): ") or "smtp-relay.brevo.com"
            smtp_user = input("SMTP User: ")
            from_email = input("From Email: ")
            to_email = input("To Email: ")

            env_content = f"""# Configuración de Email
SMTP_SERVER={smtp_server}
SMTP_USER={smtp_user}
FROM_EMAIL={from_email}
TO_EMAIL={to_email}
"""

            with open(env_file, 'w') as f:
                f.write(env_content)

            print(f"Configuración guardada en {env_file}")
            print("   IMPORTANTE: Configure SMTP_PASSWORD manualmente")

    def _create_directories(self):
        """Crea directorios necesarios."""
        print("\n📁 Creando directorios...")

        directories = ['logs', 'reports', 'temp', 'data']
        for dir_name in directories:
            dir_path = BASE_DIR / dir_name
            dir_path.mkdir(exist_ok=True)
            print(f"[OK] {dir_name}/")


class PostInstallCommand(install):
    """Comando post-instalación."""

    def run(self):
        install.run(self)
        print("\nInstalación completada!")
        print("Ejecute 'python setup.py verify' para verificar el sistema")


class PostDevelopCommand(develop):
    """Comando post-desarrollo."""

    def run(self):
        develop.run(self)
        print("\nInstalación en modo desarrollo completada!")


# =============================================================================
# CONFIGURACIÓN DE SETUP
# =============================================================================

# Leer README para descripción larga
long_description = ""
readme_file = BASE_DIR / 'README.md'
if readme_file.exists():
    with open(readme_file, 'r', encoding='utf-8') as f:
        long_description = f.read()

# Configuración principal
setup(
    # Metadata básica
    name=PROJECT_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,

    # Clasificadores
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],

    # Configuración de paquetes
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,

    # Scripts de entrada
    entry_points={
        'console_scripts': [
            'sistema-ventas=sistema_ventas.main:main',
            'analisis-ventas=run:main',
        ],
    },

    # Archivos de datos
    package_data={
        'sistema_ventas': [
            'config/*.json',
            'templates/*.html',
        ],
    },

    # Incluir archivos adicionales
    include_package_data=True,

    # Comandos personalizados
    cmdclass={
        'verify': VerifyCommand,
        'check-deps': CheckDepsCommand,
        'configure': ConfigureCommand,
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
    },

    # Keywords para búsqueda
    keywords=[
        'sales analysis', 'business intelligence', 'data analysis',
        'google sheets', 'automated reporting', 'clean architecture',
        'SOLID principles', 'enterprise software'
    ],

    # Información del proyecto
    project_urls={
        "Bug Reports": f"{URL}/issues",
        "Source": URL,
        "Documentation": f"{URL}/docs",
    },
)

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def main():
    """Función principal para uso directo del script."""
    if len(sys.argv) == 1:
        print("Sistema Empresarial de Análisis de Ventas - Setup")
        print("=" * 50)
        print("Comandos disponibles:")
        print("  python setup.py install     - Instalación completa")
        print("  python setup.py develop     - Modo desarrollo")
        print("  python setup.py verify      - Verificar sistema")
        print("  python setup.py check-deps  - Verificar dependencias")
        print("  python setup.py configure   - Configuración interactiva")
        print("")
        print("Para más información: python setup.py --help")
    else:
        # Ejecutar setup normal
        pass


if __name__ == "__main__":
    main()
