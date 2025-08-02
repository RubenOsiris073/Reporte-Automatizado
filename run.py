#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA EMPRESARIAL DE ANÁLISIS DE VENTAS - PUNTO DE ENTRADA
Archivo principal para ejecutar el sistema refactorizado con arquitectura modular.

Uso:
    python run.py [nombre_hoja]

Ejemplo:
    python run.py                    # Usa "DB_sales" por defecto
    python run.py "Mi_Hoja_Ventas"   # Usa hoja personalizada
"""

import sys
import argparse
from pathlib import Path

# Agregar el directorio del sistema al path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from sistema_ventas.main import analisis_empresarial, SistemaVentasMain
    from sistema_ventas.config import settings
    from sistema_ventas.utils import logger
    from sistema_ventas.core.exceptions import SistemaVentasError
except ImportError as e:
    print(f"ERROR: Error importando módulos del sistema: {e}")
    print("Asegúrese de que todos los módulos estén instalados correctamente.")
    print("Ejecute: pip install -r requirements.txt")
    sys.exit(1)


def mostrar_banner():
    """Muestra el banner del sistema."""
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                 SISTEMA EMPRESARIAL DE VENTAS                ║
║                    Análisis Profesional                      ║
╠══════════════════════════════════════════════════════════════╣
║ Versión: {settings.base.VERSION:<20} Arquitectura: Modular ║
║ Desarrollado con principios Clean Architecture & SOLID       ║
╚══════════════════════════════════════════════════════════════╝

Funcionalidades:
   • Conexión automatizada con Google Sheets
   • Análisis estadístico avanzado de ventas
   • Generación de reportes profesionales
   • Envío automático por email
   • Análisis estratégico con IA (Ollama)

Configuración:
   • Email SMTP: {settings.email.SMTP_SERVER}
   • Destinatario: {settings.email.DEFAULT_TO_EMAIL}
   • Directorio de reportes: {settings.base.REPORTS_DIR}
   • Logs del sistema: {settings.base.LOGS_DIR}
"""
    print(banner)


def verificar_configuracion():
    """
    Verifica que la configuración del sistema sea válida.

    Returns:
        bool: True si la configuración es válida
    """
    print("Verificando configuración del sistema...")

    validacion = settings.validate_all()

    for modulo, es_valido in validacion.items():
        estado = "[OK]" if es_valido else "[ERROR]"
        print(f"   {estado} {modulo.title()}: {'OK' if es_valido else 'ERROR'}")

    configuracion_valida = all(validacion.values())

    if not configuracion_valida:
        print("\nADVERTENCIAS DE CONFIGURACIÓN:")
        if not validacion.get('email', True):
            print("   • Configuración de email incompleta")
        if not validacion.get('sheets', True):
            print("   • Archivo credentials.json no encontrado")
            print("   • Descarga las credenciales de Google Cloud Console")

        print("\nEl sistema intentará continuar, pero algunas funciones pueden fallar.")

    return configuracion_valida


def mostrar_ayuda():
    """Muestra ayuda detallada del sistema."""
    ayuda = """
GUÍA DE USO DEL SISTEMA

EJECUCIÓN BÁSICA:
   python run.py                    # Análisis con hoja por defecto
   python run.py "DB_sales"         # Especificar hoja de Google Sheets
   python run.py --help             # Mostrar esta ayuda

REQUISITOS PREVIOS:
   1. Instalar dependencias: pip install -r requirements.txt
   2. Configurar credentials.json de Google Sheets
   3. Configurar variables de email en config/__init__.py
   4. (Opcional) Tener Ollama ejecutándose para análisis con IA

PROCESO DE ANÁLISIS:
   1. Conecta con Google Sheets
   2. Carga y procesa datos de ventas
   3. Genera análisis estadístico completo
   4. Ejecuta análisis estratégico con IA (si disponible)
   5. Genera reporte en archivo .txt
   6. Envía reporte por email automáticamente

CONFIGURACIÓN:
   • Editar sistema_ventas/config/__init__.py para personalizar
   • Logs disponibles en: {settings.base.LOGS_DIR}
   • Reportes generados en: {settings.base.REPORTS_DIR}

SOLUCIÓN DE PROBLEMAS:
   • Error de conexión Sheets: Verificar credentials.json
   • Error de email: Verificar configuración SMTP
   • Error de IA: Verificar que Ollama esté ejecutándose
   • Ver logs detallados en {settings.base.LOGS_DIR}/sistema_ventas.log
"""
    print(ayuda)


def main():
    """Función principal del sistema."""

    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(
        description="Sistema Empresarial de Análisis de Ventas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run.py                     # Usar hoja por defecto
  python run.py "MiHojaVentas"      # Usar hoja personalizada
  python run.py --help              # Mostrar ayuda completa
  python run.py --check-config      # Solo verificar configuración
        """
    )

    parser.add_argument(
        'nombre_hoja',
        nargs='?',
        default='DB_sales',
        help='Nombre de la hoja de Google Sheets (por defecto: DB_sales)'
    )

    parser.add_argument(
        '--check-config',
        action='store_true',
        help='Solo verificar configuración y salir'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mostrar información detallada'
    )

    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='No mostrar banner inicial'
    )

    parser.add_argument(
        '--help-detailed',
        action='store_true',
        help='Mostrar ayuda detallada del sistema'
    )

    args = parser.parse_args()

    # Mostrar ayuda detallada si se solicita
    if args.help_detailed:
        mostrar_ayuda()
        return 0

    # Mostrar banner a menos que se solicite lo contrario
    if not args.no_banner:
        mostrar_banner()

    # Solo verificar configuración si se solicita
    if args.check_config:
        configuracion_ok = verificar_configuracion()
        if configuracion_ok:
            print("\nConfiguración del sistema: VÁLIDA")
            return 0
        else:
            print("\nConfiguración del sistema: TIENE PROBLEMAS")
            return 1

    try:
        # Verificar configuración antes de ejecutar
        if args.verbose:
            verificar_configuracion()

        # Mostrar información de inicio
        print(f"Iniciando análisis de ventas...")
        print(f"Hoja de Google Sheets: {args.nombre_hoja}")
        print(f"Reporte se enviará a: {settings.email.DEFAULT_TO_EMAIL}")
        print("-" * 60)

        # Ejecutar análisis completo
        logger.info(f"Iniciando análisis desde run.py con hoja: {args.nombre_hoja}")

        resultado = analisis_empresarial(args.nombre_hoja)

        if resultado and resultado.get('analisis_completado'):
            print("\n¡ANÁLISIS COMPLETADO EXITOSAMENTE!")
            print(f"Reporte: {resultado.get('archivo_reporte', 'N/A')}")
            print(f"Email: {'Enviado' if resultado.get('email_enviado') else 'No enviado'}")

            if args.verbose:
                print(f"\nResumen de resultados:")
                print(f"   • Timestamp: {resultado.get('timestamp', 'N/A')}")
                if 'resultados' in resultado:
                    resumen = resultado['resultados'].get('resumen_principal', {})
                    if 'metricas_ventas' in resumen:
                        mv = resumen['metricas_ventas']
                        print(f"   • Ventas totales: ${mv.get('ventas_totales', 0):,.2f}")
                        print(f"   • Transacciones: {mv.get('num_transacciones', 0):,}")

            logger.info("Análisis completado exitosamente desde run.py")
            return 0
        else:
            print("\nEl análisis no se completó correctamente")
            print("Revise los logs para más detalles:")
            print(f"   {settings.base.LOGS_DIR}/sistema_ventas.log")
            logger.error("Análisis no completado desde run.py")
            return 1

    except KeyboardInterrupt:
        print("\n\nEjecución interrumpida por el usuario")
        logger.info("Ejecución interrumpida por el usuario desde run.py")
        return 130

    except SistemaVentasError as e:
        print(f"\nERROR DEL SISTEMA: {e}")
        if args.verbose and hasattr(e, 'details'):
            print(f"   Detalles: {e.details}")
        logger.error(f"Error del sistema desde run.py: {e}")
        return 1

    except Exception as e:
        print(f"\nERROR INESPERADO: {e}")
        print(f"Revise los logs para más información:")
        print(f"   {settings.base.LOGS_DIR}/errores.log")
        logger.error(f"Error inesperado desde run.py: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\nERROR CRÍTICO EN EL SISTEMA: {e}")
        sys.exit(1)
