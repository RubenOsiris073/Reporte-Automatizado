"""
Servicio de análisis de datos.
Migración mejorada de DataAnalyzer original con nueva arquitectura.
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal

from ..core.interfaces.data_interface import DataServiceInterface
from ..core.exceptions import (
    DataServiceError,
    DataAnalysisError,
    DataValidationError,
    DataProcessingError,
    DataExportError
)
from ..config import settings
from ..models import KPIMetrics, TrendAnalysis, PeriodoAnalisis


class DataAnalysisService(DataServiceInterface):
    """
    Servicio de análisis de datos implementando DataServiceInterface.
    Migración mejorada de DataAnalyzer original.
    """

    def __init__(self, config=None):
        """
        Inicializa el servicio de análisis de datos.

        Args:
            config: Configuración opcional, usa settings.data_analysis por defecto
        """
        self.config = config or settings.data_analysis
        self.resumen = {}
        self.df_actual = None

    def generar_resumen(self, datos: pd.DataFrame) -> Dict[str, Any]:
        """
        Genera un resumen completo de los datos de ventas.
        Migración de la funcionalidad original generar_resumen().

        Args:
            datos: DataFrame con los datos de ventas

        Returns:
            Dict[str, Any]: Diccionario con el resumen de métricas

        Raises:
            DataAnalysisError: Si hay un error en el análisis
            ValidationError: Si los datos no son válidos
        """
        try:
            # Validar datos primero
            es_valido, errores = self.validar_datos(datos)
            if not es_valido:
                raise DataValidationError(
                    f"Datos inválidos para análisis: {'; '.join(errores)}",
                    error_code="INVALID_DATA_FOR_ANALYSIS",
                    details={"validation_errors": errores}
                )

            self.df_actual = datos
            print("Generando análisis estadístico empresarial...")

            # Inicializar resumen
            self.resumen = {}

            # Generar cada sección del análisis
            self._generar_info_basica(datos)
            self._generar_metricas_ventas(datos)
            self._generar_top_productos(datos)
            self._generar_analisis_categoria(datos)
            self._generar_alertas_inventario(datos)
            self._generar_analisis_temporal(datos)

            print("Análisis estadístico completado exitosamente")
            return self.resumen

        except DataValidationError:
            # Re-raise errores de validación
            raise
        except Exception as e:
            raise DataAnalysisError(
                f"Error generando resumen de análisis: {str(e)}",
                error_code="ANALYSIS_GENERATION_ERROR",
                details={"error": str(e)}
            )

    def _generar_info_basica(self, datos: pd.DataFrame):
        """Genera información básica del dataset."""
        self.resumen['info_basica'] = {
            'total_filas': len(datos),
            'columnas': list(datos.columns),
            'fecha_analisis': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Período de datos si existe columna de fecha
        if 'venta_timestamp' in datos.columns:
            fecha_min = datos['venta_timestamp'].min()
            fecha_max = datos['venta_timestamp'].max()
            self.resumen['info_basica']['periodo'] = f"Del {fecha_min} al {fecha_max}"

    def _generar_metricas_ventas(self, datos: pd.DataFrame):
        """Genera métricas de rendimiento de ventas."""
        if 'venta_total' in datos.columns:
            venta_total = datos['venta_total'].sum()
            ticket_promedio = datos['venta_total'].mean()
            num_transacciones = len(datos[datos['venta_total'] > 0])

            self.resumen['metricas_ventas'] = {
                'ventas_totales': float(venta_total),
                'ticket_promedio': float(ticket_promedio),
                'num_transacciones': int(num_transacciones)
            }

    def _generar_top_productos(self, datos: pd.DataFrame):
        """Genera análisis de top productos."""
        if 'nombre' in datos.columns and 'venta_total' in datos.columns:
            top_productos = datos.groupby('nombre')['venta_total'].sum().nlargest(10)
            self.resumen['top_productos'] = top_productos.to_dict()

    def _generar_analisis_categoria(self, datos: pd.DataFrame):
        """Genera análisis por categoría."""
        if 'categoria' in datos.columns:
            if 'venta_total' in datos.columns:
                cat_ventas = datos.groupby('categoria')['venta_total'].sum()
            else:
                cat_ventas = datos['categoria'].value_counts()
            self.resumen['por_categoria'] = cat_ventas.to_dict()

    def _generar_alertas_inventario(self, datos: pd.DataFrame):
        """Genera alertas de inventario."""
        if 'diasParaCaducar' in datos.columns:
            criticos = datos[datos['diasParaCaducar'] <= 7]
            self.resumen['alertas_inventario'] = {
                'cantidad': len(criticos),
                'productos': criticos['nombre'].tolist()[:10] if 'nombre' in criticos.columns else []
            }

    def _generar_analisis_temporal(self, datos: pd.DataFrame):
        """Genera análisis temporal y tendencias."""
        if 'mes_venta' in datos.columns and 'venta_total' in datos.columns:
            ventas_mensuales = datos.groupby('mes_venta')['venta_total'].sum().tail(6)
            self.resumen['tendencias'] = {
                'ventas_mensuales': ventas_mensuales.to_dict(),
                'mejor_mes': str(ventas_mensuales.idxmax()),
                'peor_mes': str(ventas_mensuales.idxmin())
            }

    def mostrar_resumen(self) -> None:
        """
        Muestra el resumen estadístico en consola.
        Migración de la funcionalidad original mostrar_resumen().
        """
        if not self.resumen:
            print("No hay resumen disponible. Ejecute generar_resumen() primero.")
            return

        print("\n" + "="*60)
        print("ANÁLISIS ESTADÍSTICO EMPRESARIAL")
        print("="*60)

        # Información básica
        self._mostrar_info_basica()

        # Métricas de rendimiento
        self._mostrar_metricas_ventas()

        # Top productos
        self._mostrar_top_productos()

        # Análisis por categoría
        self._mostrar_analisis_categoria()

        # Alertas de inventario
        self._mostrar_alertas_inventario()

        # Tendencias
        self._mostrar_tendencias()

    def _mostrar_info_basica(self):
        """Muestra información básica."""
        info = self.resumen.get('info_basica', {})
        print(f"Registros procesados: {info.get('total_filas', 0):,}")
        print(f"Fecha de análisis: {info.get('fecha_analisis', 'N/A')}")
        if 'periodo' in info:
            print(f"Período analizado: {info['periodo']}")

    def _mostrar_metricas_ventas(self):
        """Muestra métricas de ventas."""
        if 'metricas_ventas' in self.resumen:
            mv = self.resumen['metricas_ventas']
            print(f"\nMÉTRICAS DE RENDIMIENTO:")
            print(f"   Volumen total de ventas: ${mv['ventas_totales']:,.2f}")
            print(f"   Ticket promedio: ${mv['ticket_promedio']:,.2f}")
            print(f"   Número de transacciones: {mv['num_transacciones']:,}")

    def _mostrar_top_productos(self):
        """Muestra top productos."""
        if 'top_productos' in self.resumen:
            print(f"\nTOP 5 PRODUCTOS POR VOLUMEN:")
            for i, (producto, venta) in enumerate(list(self.resumen['top_productos'].items())[:5], 1):
                print(f"   {i}. {producto}: ${venta:,.2f}")

    def _mostrar_analisis_categoria(self):
        """Muestra análisis por categoría."""
        if 'por_categoria' in self.resumen:
            print(f"\nRENDIMIENTO POR CATEGORÍA:")
            for i, (categoria, valor) in enumerate(list(self.resumen['por_categoria'].items())[:5], 1):
                print(f"   {i}. {categoria}: ${valor:,.2f}")

    def _mostrar_alertas_inventario(self):
        """Muestra alertas de inventario."""
        if 'alertas_inventario' in self.resumen:
            ai = self.resumen['alertas_inventario']
            print(f"\nALERTAS DE INVENTARIO: {ai['cantidad']} productos")
            if ai['productos']:
                print("   Productos con fechas de vencimiento próximas:")
                for producto in ai['productos'][:3]:
                    print(f"   - {producto}")

    def _mostrar_tendencias(self):
        """Muestra análisis de tendencias."""
        if 'tendencias' in self.resumen:
            t = self.resumen['tendencias']
            print(f"\nANÁLISIS TEMPORAL:")
            print(f"   Mejor período: {t.get('mejor_mes', 'N/A')}")
            print(f"   Menor rendimiento: {t.get('peor_mes', 'N/A')}")

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
        """
        try:
            if 'venta_timestamp' not in datos.columns or 'venta_total' not in datos.columns:
                raise DataAnalysisError(
                    "Datos insuficientes para análisis de tendencias",
                    error_code="INSUFFICIENT_DATA_FOR_TRENDS",
                    details={"required_columns": ["venta_timestamp", "venta_total"]}
                )

            # Agrupar por período
            if periodo == "diario":
                agrupacion = datos.groupby(datos['venta_timestamp'].dt.date)['venta_total'].sum()
            elif periodo == "semanal":
                agrupacion = datos.groupby(datos['venta_timestamp'].dt.to_period('W'))['venta_total'].sum()
            else:  # mensual por defecto
                agrupacion = datos.groupby(datos['venta_timestamp'].dt.to_period('M'))['venta_total'].sum()

            # Calcular tendencia básica
            valores = agrupacion.values
            if len(valores) < 2:
                tendencia = "estable"
                crecimiento = 0.0
            else:
                crecimiento = ((valores[-1] - valores[0]) / valores[0] * 100) if valores[0] != 0 else 0.0
                if crecimiento > 5:
                    tendencia = "creciente"
                elif crecimiento < -5:
                    tendencia = "decreciente"
                else:
                    tendencia = "estable"

            return {
                'periodo': periodo,
                'tendencia': tendencia,
                'crecimiento_porcentual': crecimiento,
                'valores_por_periodo': agrupacion.to_dict(),
                'periodo_mejor': str(agrupacion.idxmax()),
                'periodo_peor': str(agrupacion.idxmin()),
                'promedio_periodo': float(agrupacion.mean()),
                'total_periodos': len(agrupacion)
            }

        except Exception as e:
            raise DataAnalysisError(
                f"Error analizando tendencias: {str(e)}",
                error_code="TREND_ANALYSIS_ERROR",
                details={"periodo": periodo}
            )

    def calcular_metricas_kpi(self, datos: pd.DataFrame) -> Dict[str, float]:
        """
        Calcula los KPIs principales del negocio.

        Args:
            datos: DataFrame con los datos de ventas

        Returns:
            Dict[str, float]: Diccionario con los KPIs calculados
        """
        try:
            kpis = {}

            # KPIs básicos de ventas
            if 'venta_total' in datos.columns:
                kpis['total_ventas'] = float(datos['venta_total'].sum())
                kpis['ticket_promedio'] = float(datos['venta_total'].mean())
                kpis['mediana_venta'] = float(datos['venta_total'].median())

            # KPIs de transacciones
            kpis['total_transacciones'] = len(datos)
            kpis['transacciones_exitosas'] = len(datos[datos['venta_total'] > 0]) if 'venta_total' in datos.columns else 0

            # KPIs de productos
            if 'nombre' in datos.columns:
                kpis['productos_unicos'] = datos['nombre'].nunique()

            # KPIs de clientes
            if 'cliente_id' in datos.columns:
                kpis['clientes_unicos'] = datos['cliente_id'].nunique()
                kpis['transacciones_por_cliente'] = len(datos) / datos['cliente_id'].nunique()

            # Tasa de conversión (asumiendo que hay productos con venta 0)
            if 'venta_total' in datos.columns:
                kpis['tasa_conversion'] = (len(datos[datos['venta_total'] > 0]) / len(datos) * 100) if len(datos) > 0 else 0.0

            return kpis

        except Exception as e:
            raise DataAnalysisError(
                f"Error calculando KPIs: {str(e)}",
                error_code="KPI_CALCULATION_ERROR"
            )

    def identificar_anomalias(
        self,
        datos: pd.DataFrame,
        umbral: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Identifica anomalías en los datos de ventas usando desviación estándar.

        Args:
            datos: DataFrame con los datos de ventas
            umbral: Umbral de desviación estándar para detectar anomalías

        Returns:
            List[Dict[str, Any]]: Lista de anomalías detectadas
        """
        try:
            anomalias = []

            if 'venta_total' in datos.columns:
                media = datos['venta_total'].mean()
                desv_std = datos['venta_total'].std()

                # Calcular límites
                limite_superior = media + (umbral * desv_std)
                limite_inferior = media - (umbral * desv_std)

                # Encontrar anomalías
                anomalias_sup = datos[datos['venta_total'] > limite_superior]
                anomalias_inf = datos[datos['venta_total'] < limite_inferior]

                # Formatear anomalías superiores
                for _, row in anomalias_sup.iterrows():
                    anomalias.append({
                        'tipo': 'venta_alta',
                        'valor': float(row['venta_total']),
                        'limite': float(limite_superior),
                        'desviacion': float((row['venta_total'] - media) / desv_std),
                        'producto': row.get('nombre', 'N/A'),
                        'fecha': row.get('venta_timestamp', 'N/A')
                    })

                # Formatear anomalías inferiores (solo si son ventas válidas)
                for _, row in anomalias_inf.iterrows():
                    if row['venta_total'] > 0:  # Excluir ventas de $0
                        anomalias.append({
                            'tipo': 'venta_baja',
                            'valor': float(row['venta_total']),
                            'limite': float(limite_inferior),
                            'desviacion': float((row['venta_total'] - media) / desv_std),
                            'producto': row.get('nombre', 'N/A'),
                            'fecha': row.get('venta_timestamp', 'N/A')
                        })

            return anomalias

        except Exception as e:
            raise DataAnalysisError(
                f"Error identificando anomalías: {str(e)}",
                error_code="ANOMALY_DETECTION_ERROR",
                details={"umbral": umbral}
            )

    def generar_predicciones(
        self,
        datos: pd.DataFrame,
        periodos_futuros: int = 3
    ) -> Dict[str, Any]:
        """
        Genera predicciones de ventas futuras usando tendencia lineal simple.

        Args:
            datos: DataFrame con los datos históricos
            periodos_futuros: Número de períodos a predecir

        Returns:
            Dict[str, Any]: Predicciones y métricas de confianza
        """
        try:
            if 'venta_timestamp' not in datos.columns or 'venta_total' not in datos.columns:
                raise DataAnalysisError(
                    "Datos insuficientes para predicciones",
                    error_code="INSUFFICIENT_DATA_FOR_PREDICTION",
                    details={"required_columns": ["venta_timestamp", "venta_total"]}
                )

            # Agrupar por mes para la predicción
            ventas_mensuales = datos.groupby(datos['venta_timestamp'].dt.to_period('M'))['venta_total'].sum()

            if len(ventas_mensuales) < 3:
                return {
                    'predicciones': [],
                    'confianza': 0.0,
                    'metodo': 'insuficientes_datos',
                    'mensaje': 'Se necesitan al menos 3 períodos históricos para generar predicciones'
                }

            # Calcular tendencia lineal simple
            valores = ventas_mensuales.values
            x = np.arange(len(valores))

            # Regresión lineal básica
            pendiente = np.corrcoef(x, valores)[0, 1] * (np.std(valores) / np.std(x))
            intercepto = np.mean(valores) - pendiente * np.mean(x)

            # Generar predicciones
            predicciones = []
            for i in range(1, periodos_futuros + 1):
                prediccion = intercepto + pendiente * (len(valores) + i - 1)
                predicciones.append(max(0, prediccion))  # No permitir predicciones negativas

            # Calcular métricas de confianza básicas
            residuos = valores - (intercepto + pendiente * x)
            error_std = np.std(residuos)
            r_cuadrado = 1 - (np.sum(residuos**2) / np.sum((valores - np.mean(valores))**2))
            confianza = max(0, min(100, r_cuadrado * 100))  # Convertir a porcentaje

            return {
                'predicciones': [float(p) for p in predicciones],
                'confianza': float(confianza),
                'error_estandar': float(error_std),
                'tendencia': 'creciente' if pendiente > 0 else 'decreciente' if pendiente < 0 else 'estable',
                'metodo': 'regresion_lineal_simple',
                'periodos_historicos': len(valores),
                'periodos_predichos': periodos_futuros
            }

        except Exception as e:
            raise DataAnalysisError(
                f"Error generando predicciones: {str(e)}",
                error_code="PREDICTION_ERROR",
                details={"periodos_futuros": periodos_futuros}
            )

    def validar_datos(self, datos: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Valida la integridad y calidad de los datos.

        Args:
            datos: DataFrame a validar

        Returns:
            Tuple[bool, List[str]]: (Es válido, Lista de errores)
        """
        errores = []

        # Validaciones básicas
        if datos is None:
            errores.append("DataFrame es None")
            return False, errores

        if datos.empty:
            errores.append("DataFrame está vacío")
            return False, errores

        # Validar que tenga al menos una columna básica
        columnas_basicas = ['nombre', 'categoria', 'venta_total']
        tiene_columna_basica = any(col in datos.columns for col in columnas_basicas)

        if not tiene_columna_basica:
            errores.append(f"Debe tener al menos una de estas columnas: {', '.join(columnas_basicas)}")

        # Validar tipos de datos
        if 'venta_total' in datos.columns:
            if not pd.api.types.is_numeric_dtype(datos['venta_total']):
                errores.append("Columna 'venta_total' debe ser numérica")
            elif datos['venta_total'].isnull().all():
                errores.append("Columna 'venta_total' no puede estar completamente vacía")

        if 'venta_timestamp' in datos.columns:
            if not pd.api.types.is_datetime64_any_dtype(datos['venta_timestamp']):
                errores.append("Columna 'venta_timestamp' debe ser fecha/hora")

        # Validar porcentaje de valores nulos
        for col in ['nombre', 'categoria']:
            if col in datos.columns:
                porcentaje_nulos = datos[col].isnull().sum() / len(datos) * 100
                if porcentaje_nulos > 80:
                    errores.append(f"Demasiados valores nulos en '{col}': {porcentaje_nulos:.1f}%")

        es_valido = len(errores) == 0
        return es_valido, errores

    def limpiar_datos(self, datos: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia y prepara los datos para el análisis.

        Args:
            datos: DataFrame con datos crudos

        Returns:
            pd.DataFrame: DataFrame limpio y preparado
        """
        try:
            df_limpio = datos.copy()

            # Eliminar filas completamente vacías
            df_limpio = df_limpio.dropna(how='all')

            # Limpiar columnas numéricas
            if 'venta_total' in df_limpio.columns:
                # Convertir a numérico, valores inválidos se vuelven NaN
                df_limpio['venta_total'] = pd.to_numeric(df_limpio['venta_total'], errors='coerce')
                # Llenar NaN con 0 en ventas
                df_limpio['venta_total'] = df_limpio['venta_total'].fillna(0)
                # Eliminar valores negativos
                df_limpio = df_limpio[df_limpio['venta_total'] >= 0]

            # Limpiar columnas de texto
            for col in ['nombre', 'categoria']:
                if col in df_limpio.columns:
                    # Eliminar espacios en blanco extra
                    df_limpio[col] = df_limpio[col].astype(str).str.strip()
                    # Reemplazar strings vacíos con 'Sin especificar'
                    df_limpio[col] = df_limpio[col].replace(['', 'nan', 'None'], 'Sin especificar')

            # Limpiar fechas
            if 'venta_timestamp' in df_limpio.columns:
                df_limpio['venta_timestamp'] = pd.to_datetime(df_limpio['venta_timestamp'], errors='coerce')
                # Eliminar filas con fechas inválidas
                df_limpio = df_limpio.dropna(subset=['venta_timestamp'])

            print(f"Datos limpiados: {len(datos)} -> {len(df_limpio)} registros")
            return df_limpio

        except Exception as e:
            raise DataProcessingError(
                f"Error limpiando datos: {str(e)}",
                error_code="DATA_CLEANING_ERROR"
            )

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
        """
        try:
            if formato not in self.config.EXPORT_FORMATS:
                raise DataExportError(
                    f"Formato no soportado: {formato}",
                    error_code="UNSUPPORTED_FORMAT",
                    details={"supported_formats": self.config.EXPORT_FORMATS}
                )

            # Generar nombre de archivo si no se proporciona ruta
            if not ruta:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                ruta = f"analisis_resultados_{timestamp}.{formato}"

            # Exportar según formato
            if formato == "json":
                with open(ruta, 'w', encoding='utf-8') as f:
                    json.dump(resultados, f, ensure_ascii=False, indent=2, default=str)

            elif formato == "csv" and self.df_actual is not None:
                self.df_actual.to_csv(ruta, index=False, encoding='utf-8')

            elif formato == "excel" and self.df_actual is not None:
                with pd.ExcelWriter(ruta, engine='openpyxl') as writer:
                    self.df_actual.to_excel(writer, sheet_name='Datos', index=False)
                    # Agregar hoja con resumen si existe
                    if self.resumen:
                        resumen_df = pd.DataFrame(list(self.resumen.items()), columns=['Metrica', 'Valor'])
                        resumen_df.to_excel(writer, sheet_name='Resumen', index=False)

            print(f"Resultados exportados exitosamente: {ruta}")
            return ruta

        except Exception as e:
            raise DataExportError(
                f"Error exportando resultados: {str(e)}",
                error_code="EXPORT_ERROR",
                details={"formato": formato, "ruta": ruta}
            )

    def get_resumen(self) -> Dict[str, Any]:
        """
        Obtiene el resumen actual del análisis.
        Método de conveniencia para mantener compatibilidad.

        Returns:
            Dict[str, Any]: Resumen actual
        """
        return self.resumen.copy()

    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Obtiene el DataFrame actual.
        Método de conveniencia.

        Returns:
            Optional[pd.DataFrame]: DataFrame actual o None
        """
        return self.df_actual
