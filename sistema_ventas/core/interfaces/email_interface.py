"""
Interface para servicios de email.
Define el contrato que debe cumplir cualquier implementación de servicio de email.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class EmailServiceInterface(ABC):
    """
    Interface abstracta para servicios de email.

    Esta interfaz define los métodos que debe implementar
    cualquier servicio de email en el sistema.
    """

    @abstractmethod
    def enviar_reporte_automatico(
        self,
        datos_resumen: Dict[str, Any],
        archivo_reporte: Optional[str] = None
    ) -> bool:
        """
        Envía un reporte automático por email.

        Args:
            datos_resumen: Diccionario con los datos del resumen
            archivo_reporte: Ruta opcional del archivo adjunto

        Returns:
            bool: True si el envío fue exitoso, False en caso contrario

        Raises:
            EmailServiceError: Si hay un error en el envío
        """
        pass

    @abstractmethod
    def enviar_reporte_multiple(
        self,
        destinatarios: List[str],
        datos_resumen: Dict[str, Any],
        archivo_reporte: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        Envía un reporte a múltiples destinatarios.

        Args:
            destinatarios: Lista de emails destinatarios
            datos_resumen: Diccionario con los datos del resumen
            archivo_reporte: Ruta opcional del archivo adjunto

        Returns:
            Dict[str, bool]: Diccionario con el resultado por destinatario

        Raises:
            EmailServiceError: Si hay un error en el envío
        """
        pass

    @abstractmethod
    def validar_configuracion(self) -> bool:
        """
        Valida que la configuración del servicio de email sea correcta.

        Returns:
            bool: True si la configuración es válida

        Raises:
            ConfigurationError: Si la configuración es inválida
        """
        pass

    @abstractmethod
    def probar_conexion(self) -> bool:
        """
        Prueba la conexión con el servidor de email.

        Returns:
            bool: True si la conexión es exitosa

        Raises:
            ConnectionError: Si no se puede establecer conexión
        """
        pass
