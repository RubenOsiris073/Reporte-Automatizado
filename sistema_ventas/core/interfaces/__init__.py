"""
Interfaces del sistema de ventas.
=================================

Define los contratos que deben cumplir las implementaciones de servicios.
Todas las interfaces siguen el principio de Inversión de Dependencias (DIP)
del patrón SOLID, permitiendo que el código dependa de abstracciones
en lugar de implementaciones concretas.

Interfaces disponibles:
- EmailServiceInterface: Contrato para servicios de email
- DataServiceInterface: Contrato para servicios de análisis de datos
- SheetsServiceInterface: Contrato para servicios de Google Sheets
"""

from abc import ABC, abstractmethod

# Importar todas las interfaces
from .email_interface import EmailServiceInterface
from .data_interface import DataServiceInterface
from .sheets_interface import SheetsServiceInterface

# =============================================================================
# FUNCIONES DE UTILIDAD PARA INTERFACES
# =============================================================================

def get_interface_info(interface_class):
    """
    Obtiene información sobre una interfaz.

    Args:
        interface_class: Clase de interfaz

    Returns:
        dict: Información de la interfaz
    """
    return {
        'name': interface_class.__name__,
        'description': interface_class.__doc__.split('\n')[1].strip() if interface_class.__doc__ else 'Sin descripción',
        'abstract_methods': list(getattr(interface_class, '__abstractmethods__', set())),
        'method_count': len(getattr(interface_class, '__abstractmethods__', set()))
    }


def list_all_interfaces():
    """
    Lista todas las interfaces disponibles con su información.

    Returns:
        dict: Diccionario con información de todas las interfaces
    """
    interfaces = {
        'EmailServiceInterface': EmailServiceInterface,
        'DataServiceInterface': DataServiceInterface,
        'SheetsServiceInterface': SheetsServiceInterface
    }

    return {name: get_interface_info(interface) for name, interface in interfaces.items()}


def validate_interface_contract(implementation, interface_class):
    """
    Valida que una implementación cumpla el contrato de una interfaz.

    Args:
        implementation: Instancia de la implementación
        interface_class: Clase de interfaz a validar

    Returns:
        tuple: (es_valido, lista_errores)
    """
    errors = []

    # Verificar que sea una instancia de la interfaz
    if not isinstance(implementation, interface_class):
        errors.append(f"La implementación no hereda de {interface_class.__name__}")
        return False, errors

    # Verificar métodos abstractos
    abstract_methods = getattr(interface_class, '__abstractmethods__', set())
    for method_name in abstract_methods:
        if not hasattr(implementation, method_name):
            errors.append(f"Método faltante: {method_name}")
        else:
            method = getattr(implementation, method_name)
            if not callable(method):
                errors.append(f"El atributo {method_name} no es callable")

    is_valid = len(errors) == 0
    return is_valid, errors


# =============================================================================
# CLASE BASE PARA INTERFACES
# =============================================================================

class BaseServiceInterface(ABC):
    """
    Interfaz base para todos los servicios del sistema.

    Define métodos comunes que deberían implementar todos los servicios.
    """

    @abstractmethod
    def validate_configuration(self) -> bool:
        """
        Valida la configuración del servicio.

        Returns:
            bool: True si la configuración es válida
        """
        pass

    @abstractmethod
    def get_service_status(self) -> dict:
        """
        Obtiene el estado actual del servicio.

        Returns:
            dict: Estado del servicio
        """
        pass

    @abstractmethod
    def cleanup_resources(self) -> bool:
        """
        Limpia recursos utilizados por el servicio.

        Returns:
            bool: True si la limpieza fue exitosa
        """
        pass


# =============================================================================
# DECORADOR PARA VALIDACIÓN DE INTERFACES
# =============================================================================

def implements_interface(interface_class):
    """
    Decorador que valida que una clase implemente correctamente una interfaz.

    Args:
        interface_class: Clase de interfaz que debe implementar

    Returns:
        function: Decorador
    """
    def decorator(cls):
        # Validar en tiempo de definición de clase
        abstract_methods = getattr(interface_class, '__abstractmethods__', set())

        for method_name in abstract_methods:
            if not hasattr(cls, method_name):
                raise TypeError(
                    f"La clase {cls.__name__} no implementa el método requerido: {method_name} "
                    f"de la interfaz {interface_class.__name__}"
                )

        # Agregar metadata
        cls._implemented_interface = interface_class
        cls._interface_validated = True

        return cls

    return decorator


# =============================================================================
# CONSTANTES DE INTERFACES
# =============================================================================

AVAILABLE_INTERFACES = {
    'email': EmailServiceInterface,
    'data': DataServiceInterface,
    'sheets': SheetsServiceInterface,
    'base': BaseServiceInterface
}

INTERFACE_DESCRIPTIONS = {
    'EmailServiceInterface': 'Contrato para servicios de envío de emails',
    'DataServiceInterface': 'Contrato para servicios de análisis de datos',
    'SheetsServiceInterface': 'Contrato para servicios de Google Sheets',
    'BaseServiceInterface': 'Interfaz base para todos los servicios'
}

# =============================================================================
# EXPORTACIONES
# =============================================================================

__all__ = [
    # Interfaces principales
    'EmailServiceInterface',
    'DataServiceInterface',
    'SheetsServiceInterface',
    'BaseServiceInterface',

    # Funciones de utilidad
    'get_interface_info',
    'list_all_interfaces',
    'validate_interface_contract',

    # Decoradores
    'implements_interface',

    # Constantes
    'AVAILABLE_INTERFACES',
    'INTERFACE_DESCRIPTIONS'
]

# Información del módulo
__version__ = "2.0.0"
__description__ = "Interfaces del Sistema de Análisis de Ventas"
