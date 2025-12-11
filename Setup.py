"""
Script de compilación para CapturaOCR usando cx_Freeze
PyInstaller es más adecuado para este proyecto, pero se deja como referencia
"""
import subprocess
import sys
import os


def compilar():
    """Compila el proyecto usando cx_Freeze"""
    
    # Instalar cx_Freeze si no está
    subprocess.run([sys.executable, "-m", "pip", "install", "cx_Freeze"], check=True)

    from cx_Freeze import setup, Executable
    
    # Módulos que se incluirán explícitamente
    includes = [
        'numpy',
        'cv2',
        'requests',
        'json',
        'configparser',
        'datetime',
        'subprocess',
        'os',
        'sys'
    ]

    # Archivos adicionales que se copiarán al ejecutable
    includefiles = [
        'Setting.ini',
        'Setting.py',
        'Homeassistan.py'
    ]

    # Módulos a excluir (para reducir tamaño)
    excludes = [
        'tkinter',
        'matplotlib',
        'scipy',
        'pandas',
        'pytest',
        'setuptools'
    ]

    # Paquetes completos necesarios
    packages = [
        'cv2',
        'numpy',
        'requests',
        'configparser',
        'datetime',
        'subprocess',
        'json',
        'os',
        'sys',
        'collections'
    ]

    # Configuración de build
    build_exe_options = {
        "includes": includes,
        "excludes": excludes,
        "packages": packages,
        "include_files": includefiles,
        "optimize": 2,  # Optimización de código
    }

    # Configuración base para diferentes plataformas
    base = None
    if sys.platform == "win32":
        base = "Console"  # Usar "Win32GUI" si no quieres ventana de consola en Windows

    # Setup
    setup(
        name="CapturaOCR_N2",
        version="1.0",
        description="Sistema de captura y OCR para medidor de N2 con envío a Home Assistant",
        author="Tu Nombre",
        options={"build_exe": build_exe_options},
        executables=[
            Executable(
                "Main.py",
                base=base,
                target_name="CapturaOCR_N2"  # Nombre del ejecutable
            )
        ]
    )


if __name__ == "__main__":
    compilar()



