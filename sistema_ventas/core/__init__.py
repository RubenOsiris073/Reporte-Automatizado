"""
Core del Sistema de Análisis de Ventas
======================================

Módulo central que contiene las interfaces, excepciones y componentes
fundamentales del sistema. Define los contratos y estructuras base
que deben seguir todas las implementaciones.

Este módulo implementa los principios de Clean Architecture:
- Interfaces: Define contratos para servicios
- Exceptions: Manejo específico de errores del dominio
- Domain Logic: Lógica de negocio pura
"""

# =============================================================================
# IMPORTACIÓN DE EXCEPCIONES
# =============================================================================

from .exceptions import (
    # Excepción base
    SistemaVentasError,

    # Excepciones de Email
    EmailServiceError,
    EmailConfigurationError,
    EmailConnectionError,
    EmailSendError,

    # Excepciones de Datos
    DataServiceError,
    DataAnalysisError,
    DataValidationError,
    DataProcessingError,
    DataExportError,

    # Excepciones de Google Sheets
    SheetsServiceError,
    SheetsConnectionError,
    SheetsAuthenticationError,
    SheetsDataError,

    # Excepciones de Configuración
    ConfigurationError,
    MissingConfigurationError,
    InvalidConfigurationError,

    # Excepciones de Reportes
    ReportServiceError,
    ReportGenerationError,
    ReportTemplateError,

    # Excepciones de Sistema
    SystemResourceError,
    FileSystemError,
    NetworkError,

    # Utilidades de excepciones
    format_error_details,
    create_error_response
)

# =============================================================================
# IMPORTACIÓN DE INTERFACES
# =============================================================================

from .interfaces.email_interface import EmailServiceInterface
from .interfaces.data_interface import DataServiceInterface
from .interfaces.sheets_interface import SheetsServiceInterface

# =============================================================================
# FUNCIONES DE UTILIDAD DEL CORE
# =============================================================================

def validate_interface_implementation(instance, interface_class):
    """
    Valida que una instancia implemente correctamente una interfaz.

    Args:
        instance: Instancia a validar
        interface_class: Clase de interfaz que debe implementar

    Returns:
        bool: True si implementa correctamente la interfaz

    Raises:
        TypeError: Si la instancia no implementa la interfaz
    """
    if not isinstance(instance, interface_class):
        raise TypeError(
            f"La instancia {type(instance).__name__} no implementa {interface_class.__name__}"
        )

    # Verificar que todos los métodos abstractos estén implementados
    abstract_methods = getattr(interface_class, '__abstractmethods__', set())
    for method_name in abstract_methods:
        if not hasattr(instance, method_name):
            raise TypeError(
                f"La instancia {type(instance).__name__} no implementa el método requerido: {method_name}"
            )

        method = getattr(instance, method_name)
        if not callable(method):
            raise TypeError(
                f"El atributo {method_name} en {type(instance).__name__} no es callable"
            )

    return True


def get_core_version():
    """
    Obtiene la versión del core del sistema.

    Returns:
        str: Versión del core
    """
    return "2.0.0"


def get_available_interfaces():
    """
    Obtiene lista de interfaces disponibles en el core.

    Returns:
        list: Lista de nombres de interfaces disponibles
    """
    return [
        'EmailServiceInterface',
        'DataServiceInterface',
        'SheetsServiceInterface'
    ]


def get_available_exceptions():
    """
    Obtiene lista de excepciones disponibles en el core.

    Returns:
        list: Lista de nombres de excepciones disponibles
    """
    return [
        'SistemaVentasError',
        'EmailServiceError',
        'DataServiceError',
        'SheetsServiceError',
        'ConfigurationError',
        'ReportServiceError',
        'SystemResourceError'
    ]


# =============================================================================
# EXPORTACIONES DEL CORE
# =============================================================================

__all__ = [
    # Interfaces
    'EmailServiceInterface',
    'DataServiceInterface',
    'SheetsServiceInterface',

    # Excepción base
    'SistemaVentasError',

    # Excepciones de Email
    'EmailServiceError',
    'EmailConfigurationError',
    'EmailConnectionError',
    'EmailSendError',

    # Excepciones de Datos
    'DataServiceError',
    'DataAnalysisError',
    'DataValidationError',
    'DataProcessingError',
    'DataExportError',

    # Excepciones de Google Sheets
    'SheetsServiceError',
    'SheetsConnectionError',
    'SheetsAuthenticationError',
    'SheetsDataError',

    # Excepciones de Configuración
    'ConfigurationError',
    'MissingConfigurationError',
    'InvalidConfigurationError',

    # Excepciones de Reportes
    'ReportServiceError',
    'ReportGenerationError',
    'ReportTemplateError',

    # Excepciones de Sistema
    'SystemResourceError',
    'FileSystemError',
    'NetworkError',

    # Utilidades de excepciones
    'format_error_details',
    'create_error_response',

    # Funciones de utilidad
    'validate_interface_implementation',
    'get_core_version',
    'get_available_interfaces',
    'get_available_exceptions'
]

# =============================================================================
# INFORMACIÓN DEL MÓDULO
# =============================================================================

__version__ = get_core_version()
__description__ = "Core del Sistema de Análisis de Ventas - Interfaces y Excepciones"
__author__ = "Sistema Empresarial de Ventas"
