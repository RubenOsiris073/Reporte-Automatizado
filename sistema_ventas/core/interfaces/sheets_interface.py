"""
Interface para servicios de Google Sheets.
Define el contrato que debe cumplir cualquier implementación de servicio de Google Sheets.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd


class SheetsServiceInterface(ABC):
    """
    Interface abstracta para servicios de Google Sheets.

    Esta interfaz define los métodos que debe implementar
    cualquier servicio de Google Sheets en el sistema.
    """

    @abstractmethod
    def conectar_sheets(self, nombre_hoja: str) -> bool:
        """
        Establece conexión con Google Sheets.

        Args:
            nombre_hoja: Nombre de la hoja de cálculo

        Returns:
            bool: True si la conexión fue exitosa

        Raises:
            SheetsConnectionError: Si hay un error en la conexión
            SheetsAuthenticationError: Si hay un error de autenticación
        """
        pass

    @abstractmethod
    def cargar_datos(self, worksheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Carga datos desde Google Sheets.

        Args:
            worksheet_name: Nombre opcional de la hoja específica

        Returns:
            pd.DataFrame: DataFrame con los datos cargados

        Raises:
            SheetsDataError: Si hay un error cargando los datos
            SheetsConnectionError: Si no hay conexión establecida
        """
        pass

    @abstractmethod
    def procesar_datos(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Procesa y limpia los datos cargados desde Sheets.

        Args:
            df: DataFrame con datos crudos

        Returns:
            pd.DataFrame: DataFrame procesado y limpio

        Raises:
            SheetsDataError: Si hay un error procesando los datos
        """
        pass

    @abstractmethod
    def validar_estructura_datos(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Valida que la estructura de datos sea correcta.

        Args:
            df: DataFrame a validar

        Returns:
            Tuple[bool, List[str]]: (Es válido, Lista de errores)

        Raises:
            SheetsDataError: Si hay errores críticos de validación
        """
        pass

    @abstractmethod
    def obtener_metadatos_sheet(self) -> Dict[str, Any]:
        """
        Obtiene metadatos de la hoja de cálculo.

        Returns:
            Dict[str, Any]: Metadatos de la hoja (título, última modificación, etc.)

        Raises:
            SheetsConnectionError: Si no hay conexión establecida
        """
        pass

    @abstractmethod
    def obtener_info_worksheets(self) -> List[Dict[str, Any]]:
        """
        Obtiene información de todas las hojas de trabajo disponibles.

        Returns:
            List[Dict[str, Any]]: Lista con información de cada worksheet

        Raises:
            SheetsConnectionError: Si no hay conexión establecida
        """
        pass

    @abstractmethod
    def actualizar_datos(
        self,
        datos: pd.DataFrame,
        worksheet_name: Optional[str] = None,
        rango: Optional[str] = None
    ) -> bool:
        """
        Actualiza datos en Google Sheets.

        Args:
            datos: DataFrame con los datos a actualizar
            worksheet_name: Nombre de la hoja específica
            rango: Rango específico a actualizar (ej: 'A1:D10')

        Returns:
            bool: True si la actualización fue exitosa

        Raises:
            SheetsDataError: Si hay un error actualizando los datos
            SheetsConnectionError: Si no hay conexión establecida
        """
        pass

    @abstractmethod
    def crear_worksheet(
        self,
        nombre: str,
        filas: int = 1000,
        columnas: int = 26
    ) -> bool:
        """
        Crea una nueva hoja de trabajo.

        Args:
            nombre: Nombre de la nueva hoja
            filas: Número de filas (por defecto 1000)
            columnas: Número de columnas (por defecto 26)

        Returns:
            bool: True si la creación fue exitosa

        Raises:
            SheetsServiceError: Si hay un error creando la hoja
        """
        pass

    @abstractmethod
    def eliminar_worksheet(self, nombre: str) -> bool:
        """
        Elimina una hoja de trabajo.

        Args:
            nombre: Nombre de la hoja a eliminar

        Returns:
            bool: True si la eliminación fue exitosa

        Raises:
            SheetsServiceError: Si hay un error eliminando la hoja
        """
        pass

    @abstractmethod
    def validar_permisos(self) -> Dict[str, bool]:
        """
        Valida los permisos disponibles en la hoja.

        Returns:
            Dict[str, bool]: Permisos disponibles (read, write, etc.)

        Raises:
            SheetsAuthenticationError: Si hay un error de permisos
        """
        pass

    @abstractmethod
    def obtener_ultima_actualizacion(self) -> Optional[str]:
        """
        Obtiene la fecha de última actualización de la hoja.

        Returns:
            Optional[str]: Fecha de última actualización en formato ISO

        Raises:
            SheetsConnectionError: Si no hay conexión establecida
        """
        pass

    @abstractmethod
    def probar_conectividad(self) -> bool:
        """
        Prueba la conectividad con Google Sheets API.

        Returns:
            bool: True si la conexión es exitosa

        Raises:
            SheetsConnectionError: Si hay un error de conexión
        """
        pass

    @abstractmethod
    def obtener_estadisticas_uso(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de uso de la API.

        Returns:
            Dict[str, Any]: Estadísticas de uso (límites, requests restantes, etc.)

        Raises:
            SheetsServiceError: Si hay un error obteniendo estadísticas
        """
        pass
