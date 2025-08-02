"""
Sistema Empresarial de Análisis de Ventas
=========================================

Sistema profesional de análisis de datos de ventas con arquitectura modular,
implementando patrones Clean Architecture, SOLID y mejores prácticas de desarrollo.

Funcionalidades principales:
- Conexión automatizada con Google Sheets
- Análisis estadístico avanzado de ventas
- Generación de reportes profesionales
- Envío automático por email
- Análisis estratégico con IA

Ejemplo de uso básico:
    >>> from sistema_ventas import analisis_empresarial
    >>> resultado = analisis_empresarial("DB_sales")

Ejemplo de uso avanzado:
    >>> from sistema_ventas import SistemaVentasMain
    >>> sistema = SistemaVentasMain()
    >>> resultado = sistema.ejecutar_analisis_completo("Mi_Hoja")
"""

__version__ = "2.0.0"
__author__ = "Sistema Empresarial de Ventas"
__description__ = "Sistema profesional de análisis de ventas con arquitectura modular"

# =============================================================================
# IMPORTACIONES PRINCIPALES
# =============================================================================

try:
    # Configuración
    from .config import settings

    # Excepciones principales
    from .core.exceptions import (
        SistemaVentasError,
        EmailServiceError,
        SheetsServiceError,
        DataAnalysisError,
        ConfigurationError
    )

    # Interfaces principales
    from .core.interfaces.email_interface import EmailServiceInterface
    from .core.interfaces.sheets_interface import SheetsServiceInterface
    from .core.interfaces.data_interface import DataServiceInterface

    # Servicios principales
    from .services import EmailService
    from .services.sheets_service import SheetsService
    from .services.data_analysis_service import DataAnalysisService

    # Modelos principales
    from .models import (
        SalesData,
        KPIMetrics,
        TrendAnalysis,
        SalesReport,
        APIResponse,
        TipoReporte,
        EstadoVenta,
        PeriodoAnalisis
    )

    # Utilidades principales
    from .utils import (
        logger,
        DataValidator,
        FileUtils,
        FormatUtils,
        TimeUtils,
        log_execution_time,
        handle_exceptions,
        retry
    )

    # Factory para servicios
    from .factories import (
        ServiceFactory,
        BusinessServiceFactory,
        get_email_service,
        get_sheets_service,
        get_data_analysis_service,
        get_complete_services
    )

    # Clase principal y función de compatibilidad
    from .main import SistemaVentasMain, analisis_empresarial

except ImportError as e:
    import warnings
    warnings.warn(f"Error importando módulos del sistema: {e}", ImportWarning)

    # Definir versiones básicas para evitar errores
    class SistemaVentasError(Exception):
        """Excepción base básica."""
        pass

    def analisis_empresarial(*args, **kwargs):
        """Función de fallback."""
        raise SistemaVentasError("Sistema no inicializado correctamente. Verifique las dependencias.")

# =============================================================================
# FUNCIONES DE CONVENIENCIA
# =============================================================================

def get_version():
    """
    Obtiene la versión del sistema.

    Returns:
        str: Versión actual del sistema
    """
    return __version__


def get_system_info():
    """
    Obtiene información completa del sistema.

    Returns:
        dict: Información del sistema
    """
    try:
        return {
            'version': __version__,
            'description': __description__,
            'author': __author__,
            'configuration_valid': settings.validate_all() if 'settings' in globals() else False,
            'modules_loaded': [
                'config', 'core', 'services', 'models',
                'utils', 'factories', 'main'
            ]
        }
    except Exception:
        return {
            'version': __version__,
            'description': __description__,
            'error': 'No se pudo obtener información completa del sistema'
        }


def check_dependencies():
    """
    Verifica que todas las dependencias estén disponibles.

    Returns:
        dict: Estado de las dependencias
    """
    dependencies = {
        'pandas': False,
        'numpy': False,
        'gspread': False,
        'google-auth': False,
        'requests': False,
        'psutil': False
    }

    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            dependencies[dep] = True
        except ImportError:
            dependencies[dep] = False

    return {
        'all_available': all(dependencies.values()),
        'details': dependencies,
        'missing': [dep for dep, available in dependencies.items() if not available]
    }


def quick_start(nombre_hoja="DB_sales"):
    """
    Función de inicio rápido para nuevos usuarios.

    Args:
        nombre_hoja: Nombre de la hoja de Google Sheets

    Returns:
        dict: Resultado del análisis
    """
    try:
        print("INICIO RÁPIDO - Sistema de Análisis de Ventas")
        print("=" * 50)

        # Verificar dependencias
        deps = check_dependencies()
        if not deps['all_available']:
            print(f"Dependencias faltantes: {', '.join(deps['missing'])}")
            print("Ejecute: pip install -r requirements.txt")
            return None

        # Ejecutar análisis
        return analisis_empresarial(nombre_hoja)

    except Exception as e:
        print(f"Error en inicio rápido: {e}")
        return None


# =============================================================================
# CONFIGURACIÓN DE LOGGING GLOBAL
# =============================================================================

def setup_global_logging(level="INFO"):
    """
    Configura el logging global del sistema.

    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    try:
        if 'logger' in globals():
            import logging
            logger.setLevel(getattr(logging, level.upper()))
            logger.info(f"Logging configurado a nivel: {level}")
    except Exception as e:
        print(f"Error configurando logging: {e}")


# =============================================================================
# EXPORTACIONES PRINCIPALES
# =============================================================================

__all__ = [
    # Versión y información
    '__version__',
    'get_version',
    'get_system_info',
    'check_dependencies',
    'quick_start',

    # Configuración
    'settings',
    'setup_global_logging',

    # Excepciones principales
    'SistemaVentasError',
    'EmailServiceError',
    'SheetsServiceError',
    'DataAnalysisError',
    'ConfigurationError',

    # Interfaces
    'EmailServiceInterface',
    'SheetsServiceInterface',
    'DataServiceInterface',

    # Servicios
    'EmailService',
    'SheetsService',
    'DataAnalysisService',

    # Modelos principales
    'SalesData',
    'KPIMetrics',
    'TrendAnalysis',
    'SalesReport',
    'APIResponse',
    'TipoReporte',
    'EstadoVenta',
    'PeriodoAnalisis',

    # Utilidades principales
    'logger',
    'DataValidator',
    'FileUtils',
    'FormatUtils',
    'TimeUtils',
    'log_execution_time',
    'handle_exceptions',
    'retry',

    # Factory
    'ServiceFactory',
    'BusinessServiceFactory',
    'get_email_service',
    'get_sheets_service',
    'get_data_analysis_service',
    'get_complete_services',

    # Clases y funciones principales
    'SistemaVentasMain',
    'analisis_empresarial',
]

# =============================================================================
# INICIALIZACIÓN AUTOMÁTICA
# =============================================================================

# Configurar logging por defecto
try:
    setup_global_logging("INFO")
except Exception:
    pass

# Mensaje de bienvenida (solo en modo interactivo)
if __name__ != "__main__":
    try:
        import sys
        if hasattr(sys, 'ps1'):  # Modo interactivo
            print(f"Sistema de Análisis de Ventas v{__version__} cargado correctamente")
            print("Usa quick_start() para comenzar o analisis_empresarial() para ejecutar")
    except Exception:
        pass
