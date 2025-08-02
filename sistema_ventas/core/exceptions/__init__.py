"""
Excepciones personalizadas del sistema de ventas.
Define todas las excepciones específicas del dominio.
"""


class SistemaVentasError(Exception):
    """
    Excepción base para todos los errores del sistema de ventas.

    Todas las excepciones específicas del sistema deben heredar de esta clase.
    """

    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        error_info = f"[{self.error_code}] " if self.error_code else ""
        return f"{error_info}{self.message}"


# =============================================================================
# EXCEPCIONES DE EMAIL
# =============================================================================

class EmailServiceError(SistemaVentasError):
    """Error base para servicios de email."""
    pass


class EmailConfigurationError(EmailServiceError):
    """Error de configuración del servicio de email."""
    pass


class EmailConnectionError(EmailServiceError):
    """Error de conexión con el servidor de email."""
    pass


class EmailSendError(EmailServiceError):
    """Error al enviar email."""
    pass


# =============================================================================
# EXCEPCIONES DE DATOS
# =============================================================================

class DataServiceError(SistemaVentasError):
    """Error base para servicios de datos."""
    pass


class DataAnalysisError(DataServiceError):
    """Error durante el análisis de datos."""
    pass


class DataValidationError(DataServiceError):
    """Error de validación de datos."""
    pass


class DataProcessingError(DataServiceError):
    """Error durante el procesamiento de datos."""
    pass


class DataExportError(DataServiceError):
    """Error durante la exportación de datos."""
    pass


# =============================================================================
# EXCEPCIONES DE GOOGLE SHEETS
# =============================================================================

class SheetsServiceError(SistemaVentasError):
    """Error base para servicios de Google Sheets."""
    pass


class SheetsConnectionError(SheetsServiceError):
    """Error de conexión con Google Sheets."""
    pass


class SheetsAuthenticationError(SheetsServiceError):
    """Error de autenticación con Google Sheets."""
    pass


class SheetsDataError(SheetsServiceError):
    """Error al procesar datos de Google Sheets."""
    pass


# =============================================================================
# EXCEPCIONES DE CONFIGURACIÓN
# =============================================================================

class ConfigurationError(SistemaVentasError):
    """Error de configuración del sistema."""
    pass


class MissingConfigurationError(ConfigurationError):
    """Error por configuración faltante."""
    pass


class InvalidConfigurationError(ConfigurationError):
    """Error por configuración inválida."""
    pass


# =============================================================================
# EXCEPCIONES DE REPORTES
# =============================================================================

class ReportServiceError(SistemaVentasError):
    """Error base para servicios de reportes."""
    pass


class ReportGenerationError(ReportServiceError):
    """Error durante la generación de reportes."""
    pass


class ReportTemplateError(ReportServiceError):
    """Error relacionado con templates de reportes."""
    pass


class TemplateError(SistemaVentasError):
    """Error relacionado con templates HTML."""
    pass


# =============================================================================
# EXCEPCIONES DE SISTEMA
# =============================================================================

class SystemResourceError(SistemaVentasError):
    """Error relacionado con recursos del sistema."""
    pass


class FileSystemError(SistemaVentasError):
    """Error del sistema de archivos."""
    pass


class NetworkError(SistemaVentasError):
    """Error de red."""
    pass


# =============================================================================
# UTILIDADES PARA MANEJO DE EXCEPCIONES
# =============================================================================

def format_error_details(error: SistemaVentasError) -> dict:
    """
    Formatea los detalles de una excepción para logging o debugging.

    Args:
        error: Instancia de SistemaVentasError

    Returns:
        dict: Diccionario con información formateada del error
    """
    return {
        'error_type': type(error).__name__,
        'error_code': getattr(error, 'error_code', None),
        'message': str(error),
        'details': getattr(error, 'details', {}),
    }


def create_error_response(error: SistemaVentasError) -> dict:
    """
    Crea una respuesta estandarizada para errores.

    Args:
        error: Instancia de SistemaVentasError

    Returns:
        dict: Respuesta estandarizada del error
    """
    return {
        'success': False,
        'error': {
            'type': type(error).__name__,
            'code': getattr(error, 'error_code', 'UNKNOWN_ERROR'),
            'message': str(error),
            'details': getattr(error, 'details', {})
        }
    }


# Lista de todas las excepciones disponibles
__all__ = [
    # Base
    'SistemaVentasError',

    # Email
    'EmailServiceError',
    'EmailConfigurationError',
    'EmailConnectionError',
    'EmailSendError',

    # Datos
    'DataServiceError',
    'DataAnalysisError',
    'DataValidationError',
    'DataProcessingError',
    'DataExportError',

    # Sheets
    'SheetsServiceError',
    'SheetsConnectionError',
    'SheetsAuthenticationError',
    'SheetsDataError',

    # Configuración
    'ConfigurationError',
    'MissingConfigurationError',
    'InvalidConfigurationError',

    # Reportes
    'ReportServiceError',
    'ReportGenerationError',
    'ReportTemplateError',
    'TemplateError',

    # Sistema
    'SystemResourceError',
    'FileSystemError',
    'NetworkError',

    # Utilidades
    'format_error_details',
    'create_error_response',
]
