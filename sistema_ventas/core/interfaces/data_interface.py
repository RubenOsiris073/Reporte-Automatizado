"""
Interface para servicios de análisis de datos.
Define el contrato que debe cumplir cualquier implementación de servicio de datos.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd


class DataServiceInterface(ABC):
    """
    Interface abstracta para servicios de análisis de datos.

    Esta interfaz define los métodos que debe implementar
    cualquier servicio de análisis de datos en el sistema.
    """

    @abstractmethod
    def generar_resumen(
        self,
        datos: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Genera un resumen completo de los datos de ventas.

        Args:
            datos: DataFrame con los datos de ventas

        Returns:
            Dict[str, Any]: Diccionario con el resumen de métricas

        Raises:
            DataAnalysisError: Si hay un error en el análisis
            ValidationError: Si los datos no son válidos
        """
        pass

    @abstractmethod
    def analizar_tendencias(
        self,
        datos: pd.DataFrame,
        periodo: str = "mensual"
    ) -> Dict[str, Any]:
        """
        Analiza las tendencias de ventas en un período específico.

        Args:
            datos: DataFrame con los datos de ventas
            periodo: Período de análisis ('diario', 'semanal', 'mensual')

        Returns:
            Dict[str, Any]: Análisis de tendencias

        Raises:
            DataAnalysisError: Si hay un error en el análisis
        """
        pass

    @abstractmethod
    def calcular_metricas_kpi(
        self,
        datos: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Calcula los KPIs principales del negocio.

        Args:
            datos: DataFrame con los datos de ventas

        Returns:
            Dict[str, float]: Diccionario con los KPIs calculados

        Raises:
            DataAnalysisError: Si hay un error en el cálculo
        """
        pass

    @abstractmethod
    def identificar_anomalias(
        self,
        datos: pd.DataFrame,
        umbral: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Identifica anomalías en los datos de ventas.

        Args:
            datos: DataFrame con los datos de ventas
            umbral: Umbral de desviación estándar para detectar anomalías

        Returns:
            List[Dict[str, Any]]: Lista de anomalías detectadas

        Raises:
            DataAnalysisError: Si hay un error en la detección
        """
        pass

    @abstractmethod
    def generar_predicciones(
        self,
        datos: pd.DataFrame,
        periodos_futuros: int = 3
    ) -> Dict[str, Any]:
        """
        Genera predicciones de ventas futuras.

        Args:
            datos: DataFrame con los datos históricos
            periodos_futuros: Número de períodos a predecir

        Returns:
            Dict[str, Any]: Predicciones y métricas de confianza

        Raises:
            DataAnalysisError: Si hay un error en la predicción
        """
        pass

    @abstractmethod
    def validar_datos(
        self,
        datos: pd.DataFrame
    ) -> Tuple[bool, List[str]]:
        """
        Valida la integridad y calidad de los datos.

        Args:
            datos: DataFrame a validar

        Returns:
            Tuple[bool, List[str]]: (Es válido, Lista de errores)

        Raises:
            ValidationError: Si hay errores críticos de validación
        """
        pass

    @abstractmethod
    def limpiar_datos(
        self,
        datos: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Limpia y prepara los datos para el análisis.

        Args:
            datos: DataFrame con datos crudos

        Returns:
            pd.DataFrame: DataFrame limpio y preparado

        Raises:
            DataProcessingError: Si hay un error en el procesamiento
        """
        pass

    @abstractmethod
    def exportar_resultados(
        self,
        resultados: Dict[str, Any],
        formato: str = "json",
        ruta: Optional[str] = None
    ) -> str:
        """
        Exporta los resultados del análisis.

        Args:
            resultados: Diccionario con los resultados
            formato: Formato de exportación ('json', 'csv', 'excel')
            ruta: Ruta opcional donde guardar el archivo

        Returns:
            str: Ruta del archivo generado

        Raises:
            ExportError: Si hay un error en la exportación
        """
        pass
