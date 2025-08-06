"""
Servicio de Google Sheets.
Migración mejorada de SheetsManager original con nueva arquitectura.
"""

import gspread
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from google.oauth2.service_account import Credentials

from ..core.interfaces.sheets_interface import SheetsServiceInterface
from ..core.exceptions import (
    SheetsServiceError,
    SheetsConnectionError,
    SheetsAuthenticationError,
    SheetsDataError
)
from ..config import settings

# Importar el CredentialsManager para Railway
import sys
# Credentials manager integrado - no necesita importación externa


class SheetsService(SheetsServiceInterface):
    """
    Servicio de Google Sheets implementando SheetsServiceInterface.
    Migración mejorada de SheetsManager original.
    """

    def __init__(self, config=None):
        """
        Inicializa el servicio de Google Sheets.

        Args:
            config: Configuración opcional, usa settings.sheets por defecto
        """
        self.config = config or settings.sheets
        self.gc = None
        self.sheet = None
        self.current_worksheet = None
        self.df = None
        self._metadatos = {}

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
        try:
            print(f"Conectando con Google Sheets: {nombre_hoja}")

            # Usar el nuevo sistema de credenciales para Railway
            try:
                credentials_path = "credentials.json"
                scope = self.config.SCOPES
                creds = Credentials.from_service_account_file(
                    credentials_path,
                    scopes=scope
                )

                # Limpiar archivo temporal si existe
                if 'temp' in credentials_path:
                    self._temp_credentials_file = credentials_path

            except Exception as e:
                raise SheetsAuthenticationError(
                    f"Error de autenticación con Google Sheets: {str(e)}",
                    error_code="SHEETS_AUTH_ERROR",
                    details={"error": str(e)}
                )

            # Autorizar y conectar
            self.gc = gspread.authorize(creds)
            self.sheet = self.gc.open(nombre_hoja)
            self.current_worksheet = self.sheet.sheet1  # Hoja por defecto

            # Obtener metadatos básicos
            self._metadatos = {
                'nombre_hoja': nombre_hoja,
                'conectado_en': datetime.now().isoformat(),
                'worksheets_disponibles': len(self.sheet.worksheets())
            }

            print(f"Conexión exitosa. Worksheets disponibles: {self._metadatos['worksheets_disponibles']}")
            return True

        except gspread.SpreadsheetNotFound as e:
            raise SheetsConnectionError(
                f"Hoja de cálculo no encontrada: {nombre_hoja}",
                error_code="SPREADSHEET_NOT_FOUND",
                details={"spreadsheet_name": nombre_hoja}
            )
        except gspread.exceptions.APIError as e:
            raise SheetsConnectionError(
                f"Error de API de Google Sheets: {str(e)}",
                error_code="SHEETS_API_ERROR",
                details={"api_error": str(e)}
            )
        except Exception as e:
            raise SheetsAuthenticationError(
                f"Error de autenticación con Google Sheets: {str(e)}",
                error_code="SHEETS_AUTH_ERROR",
                details={"error": str(e)}
            )

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
        if not self.sheet:
            raise SheetsConnectionError(
                "No hay conexión establecida con Google Sheets",
                error_code="NO_SHEETS_CONNECTION"
            )

        try:
            # Seleccionar worksheet
            if worksheet_name:
                try:
                    worksheet = self.sheet.worksheet(worksheet_name)
                    self.current_worksheet = worksheet
                except gspread.WorksheetNotFound:
                    raise SheetsDataError(
                        f"Worksheet no encontrado: {worksheet_name}",
                        error_code="WORKSHEET_NOT_FOUND",
                        details={"worksheet_name": worksheet_name}
                    )
            else:
                worksheet = self.current_worksheet

            if not worksheet:
                raise SheetsDataError(
                    "No hay worksheet seleccionado",
                    error_code="NO_WORKSHEET_SELECTED"
                )

            # Cargar datos
            print("Cargando datos desde Google Sheets...")
            datos_raw = worksheet.get_all_records()

            if not datos_raw:
                print("Advertencia: No se encontraron datos en la hoja")
                self.df = pd.DataFrame()
                return self.df

            # Crear DataFrame
            self.df = pd.DataFrame(datos_raw)
            print(f"Datos cargados exitosamente: {len(self.df)} registros, {len(self.df.columns)} columnas")

            # Actualizar metadatos
            self._metadatos.update({
                'registros_cargados': len(self.df),
                'columnas': list(self.df.columns),
                'worksheet_actual': worksheet_name or 'sheet1',
                'ultima_carga': datetime.now().isoformat()
            })

            return self.df

        except gspread.exceptions.APIError as e:
            raise SheetsDataError(
                f"Error de API cargando datos: {str(e)}",
                error_code="SHEETS_API_LOAD_ERROR",
                details={"api_error": str(e)}
            )
        except Exception as e:
            raise SheetsDataError(
                f"Error inesperado cargando datos: {str(e)}",
                error_code="SHEETS_LOAD_UNEXPECTED_ERROR",
                details={"error": str(e)}
            )

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
        if df is None or df.empty:
            raise SheetsDataError(
                "DataFrame vacío o nulo para procesar",
                error_code="EMPTY_DATAFRAME"
            )

        try:
            print("Procesando y limpiando datos...")
            df_procesado = df.copy()

            # Procesar fechas
            df_procesado = self._procesar_fechas(df_procesado)

            # Procesar números
            df_procesado = self._procesar_numeros(df_procesado)

            # Calcular métricas derivadas
            df_procesado = self._calcular_metricas_derivadas(df_procesado)

            # Categorizar datos
            df_procesado = self._categorizar_datos(df_procesado)

            print(f"Datos procesados exitosamente: {len(df_procesado)} registros")

            # Actualizar el DataFrame interno
            self.df = df_procesado

            return df_procesado

        except Exception as e:
            raise SheetsDataError(
                f"Error procesando datos: {str(e)}",
                error_code="DATA_PROCESSING_ERROR",
                details={"error": str(e), "columns": list(df.columns)}
            )

    def _procesar_fechas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Procesa las columnas de fechas."""
        # Convertir fechas de venta
        if 'venta_timestamp' in df.columns:
            df['venta_timestamp'] = pd.to_datetime(df['venta_timestamp'], errors='coerce')
            df['mes_venta'] = df['venta_timestamp'].dt.to_period('M')
            df['semana_venta'] = df['venta_timestamp'].dt.to_period('W')
            df['fecha_venta'] = df['venta_timestamp'].dt.date

        # Convertir fechas de caducidad
        if 'fechaCaducidad' in df.columns:
            df['fechaCaducidad'] = pd.to_datetime(df['fechaCaducidad'], errors='coerce')

        return df

    def _procesar_numeros(self, df: pd.DataFrame) -> pd.DataFrame:
        """Procesa las columnas numéricas."""
        columnas_numericas = ['venta_total', 'precio', 'cantidad', 'diasParaCaducar']

        for col in columnas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df

    def _calcular_metricas_derivadas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula métricas derivadas."""
        # Calcular margen si tenemos las columnas necesarias
        if all(col in df.columns for col in ['venta_total', 'precio', 'cantidad']):
            df['margen'] = df['venta_total'] - (df['precio'] * df['cantidad'])
            df['margen_porcentaje'] = (df['margen'] / df['venta_total'] * 100).fillna(0)

        # Calcular ticket promedio por cliente si tenemos la info
        if 'cliente_id' in df.columns and 'venta_total' in df.columns:
            df['es_cliente_recurrente'] = df.groupby('cliente_id')['cliente_id'].transform('count') > 1

        return df

    def _categorizar_datos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Categoriza datos según criterios de negocio."""
        # Categorizar urgencia de inventario
        if 'diasParaCaducar' in df.columns:
            df['urgencia_inventario'] = pd.cut(
                df['diasParaCaducar'],
                bins=[-np.inf, 7, 30, 90, np.inf],
                labels=['Crítico', 'Urgente', 'Medio', 'Normal']
            )

        # Categorizar volumen de ventas
        if 'venta_total' in df.columns:
            df['categoria_venta'] = pd.cut(
                df['venta_total'],
                bins=[0, 100, 500, 1000, np.inf],
                labels=['Baja', 'Media', 'Alta', 'Premium']
            )

        return df

    def validar_estructura_datos(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Valida que la estructura de datos sea correcta.

        Args:
            df: DataFrame a validar

        Returns:
            Tuple[bool, List[str]]: (Es válido, Lista de errores)
        """
        errores = []

        # Validaciones básicas
        if df is None:
            errores.append("DataFrame es None")
            return False, errores

        if df.empty:
            errores.append("DataFrame está vacío")
            return False, errores

        # Validar columnas mínimas esperadas
        columnas_esperadas = ['nombre', 'categoria']  # Columnas mínimas básicas
        columnas_faltantes = [col for col in columnas_esperadas if col not in df.columns]

        if columnas_faltantes:
            errores.append(f"Columnas faltantes: {', '.join(columnas_faltantes)}")

        # Validar tipos de datos si existen columnas específicas
        if 'venta_total' in df.columns:
            if not pd.api.types.is_numeric_dtype(df['venta_total']):
                errores.append("Columna 'venta_total' debe ser numérica")

        if 'venta_timestamp' in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df['venta_timestamp']):
                errores.append("Columna 'venta_timestamp' debe ser fecha/hora")

        # Validar que no haya demasiados valores nulos en columnas críticas
        if 'nombre' in df.columns:
            porcentaje_nulos = df['nombre'].isnull().sum() / len(df) * 100
            if porcentaje_nulos > 50:
                errores.append(f"Demasiados valores nulos en 'nombre': {porcentaje_nulos:.1f}%")

        es_valido = len(errores) == 0
        return es_valido, errores

    def obtener_metadatos_sheet(self) -> Dict[str, Any]:
        """
        Obtiene metadatos de la hoja de cálculo.

        Returns:
            Dict[str, Any]: Metadatos de la hoja
        """
        if not self.sheet:
            raise SheetsConnectionError(
                "No hay conexión establecida con Google Sheets",
                error_code="NO_SHEETS_CONNECTION"
            )

        try:
            metadatos = self._metadatos.copy()
            metadatos.update({
                'titulo': self.sheet.title,
                'id': self.sheet.id,
                'url': self.sheet.url,
                'worksheets_count': len(self.sheet.worksheets())
            })
            return metadatos
        except Exception as e:
            raise SheetsServiceError(
                f"Error obteniendo metadatos: {str(e)}",
                error_code="METADATA_ERROR"
            )

    def obtener_info_worksheets(self) -> List[Dict[str, Any]]:
        """
        Obtiene información de todas las hojas de trabajo disponibles.

        Returns:
            List[Dict[str, Any]]: Lista con información de cada worksheet
        """
        if not self.sheet:
            raise SheetsConnectionError(
                "No hay conexión establecida con Google Sheets",
                error_code="NO_SHEETS_CONNECTION"
            )

        try:
            worksheets_info = []
            for ws in self.sheet.worksheets():
                info = {
                    'titulo': ws.title,
                    'id': ws.id,
                    'filas': ws.row_count,
                    'columnas': ws.col_count,
                    'url': ws.url
                }
                worksheets_info.append(info)
            return worksheets_info
        except Exception as e:
            raise SheetsServiceError(
                f"Error obteniendo información de worksheets: {str(e)}",
                error_code="WORKSHEETS_INFO_ERROR"
            )

    def actualizar_datos(
        self,
        datos: pd.DataFrame,
        worksheet_name: Optional[str] = None,
        rango: Optional[str] = None
    ) -> bool:
        """
        Actualiza datos en Google Sheets.

        Implementación básica - en el código original no había esta funcionalidad.
        """
        # Por ahora retornamos False ya que el código original no implementaba esta funcionalidad
        # Se puede implementar en el futuro si es necesario
        return False

    def crear_worksheet(self, nombre: str, filas: int = 1000, columnas: int = 26) -> bool:
        """
        Crea una nueva hoja de trabajo.

        Implementación básica - funcionalidad nueva.
        """
        return False

    def eliminar_worksheet(self, nombre: str) -> bool:
        """
        Elimina una hoja de trabajo.

        Implementación básica - funcionalidad nueva.
        """
        return False

    def validar_permisos(self) -> Dict[str, bool]:
        """
        Valida los permisos disponibles en la hoja.

        Returns:
            Dict[str, bool]: Permisos disponibles
        """
        return {
            'read': True,  # Asumimos que siempre tenemos permisos de lectura
            'write': False,  # Por defecto False, se puede verificar intentando escribir
            'admin': False
        }

    def obtener_ultima_actualizacion(self) -> Optional[str]:
        """
        Obtiene la fecha de última actualización de la hoja.

        Returns:
            Optional[str]: Fecha de última actualización
        """
        return self._metadatos.get('ultima_carga')

    def probar_conectividad(self) -> bool:
        """
        Prueba la conectividad con Google Sheets API.

        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            if self.gc and self.sheet:
                # Intentar una operación simple para verificar conectividad
                _ = self.sheet.title
                return True
            return False
        except Exception:
            return False

    def obtener_estadisticas_uso(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de uso de la API.

        Returns:
            Dict[str, Any]: Estadísticas de uso
        """
        return {
            'requests_realizados': 'N/A',  # Google Sheets API no expone esta info fácilmente
            'limite_diario': 'N/A',
            'requests_restantes': 'N/A',
            'ultima_verificacion': datetime.now().isoformat()
        }

    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Obtiene el DataFrame actual cargado.
        Método de conveniencia para mantener compatibilidad.

        Returns:
            Optional[pd.DataFrame]: DataFrame actual o None
        """
        return self.df

    def is_connected(self) -> bool:
        """
        Verifica si hay una conexión activa.
        Método de conveniencia.

        Returns:
            bool: True si hay conexión activa
        """
        return self.gc is not None and self.sheet is not None

    def __del__(self):
        """Limpieza automática del archivo temporal de credenciales"""
        if hasattr(self, '_temp_credentials_file'):
            if hasattr(self, '_temp_credentials_file') and self._temp_credentials_file:
                try:
                    import os
                    if os.path.exists(self._temp_credentials_file) and 'temp' in self._temp_credentials_file:
                        os.remove(self._temp_credentials_file)
                except Exception:
                    pass  # Ignorar errores de limpieza
