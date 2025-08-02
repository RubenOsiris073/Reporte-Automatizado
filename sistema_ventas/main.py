#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA EMPRESARIAL DE ANÁLISIS DE VENTAS - MAIN
Punto de entrada principal usando arquitectura modular refactorizada.
"""

import json
import requests
from datetime import datetime
from typing import Optional, Dict, Any
import sys
import os

# Agregar el directorio padre al path para importar OllamaService
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ollama_service import OllamaService

from .factories import ServiceFactory, get_complete_services
from .core.exceptions import (
    SistemaVentasError,
    SheetsConnectionError,
    DataAnalysisError,
    EmailServiceError
)
from .utils import logger, log_execution_time, handle_exceptions, FormatUtils
from .config import settings


class SistemaVentasMain:
    """
    Clase principal del sistema de ventas refactorizada.
    Coordina todos los servicios usando la nueva arquitectura.
    """

    def __init__(self):
        """Inicializa el sistema principal."""
        self.services = None
        self.resumen_datos = {}
        self.analyzer_results = None
        # Inicializar servicio de IA con Ollama
        self.ai_service = OllamaService()

    @log_execution_time
    @handle_exceptions(SistemaVentasError)
    def inicializar_servicios(self) -> bool:
        """
        Inicializa todos los servicios necesarios.

        Returns:
            bool: True si la inicialización fue exitosa
        """
        try:
            logger.info("Inicializando servicios del sistema...")
            self.services = get_complete_services()

            # Verificar estado de servicios
            factory_status = ServiceFactory.get_service_status()
            logger.info(f"Estado de servicios: {factory_status}")

            return True

        except Exception as e:
            logger.error(f"Error inicializando servicios: {str(e)}")
            raise SistemaVentasError(
                f"Fallo en inicialización de servicios: {str(e)}",
                error_code="SERVICE_INIT_FAILED"
            )

    @log_execution_time
    @handle_exceptions(SheetsConnectionError)
    def cargar_datos_sheets(self, nombre_hoja: str = "DB_sales") -> bool:
        """
        Carga y procesa datos desde Google Sheets.

        Args:
            nombre_hoja: Nombre de la hoja de Google Sheets

        Returns:
            bool: True si la carga fue exitosa
        """
        try:
            logger.info(f"Cargando datos desde Google Sheets: {nombre_hoja}")
            sheets_service = self.services['sheets']

            # Conectar a Google Sheets
            if not sheets_service.conectar_sheets(nombre_hoja):
                raise SheetsConnectionError(
                    f"No se pudo establecer conexión con {nombre_hoja}",
                    error_code="SHEETS_CONNECTION_FAILED"
                )

            # Cargar datos
            df_raw = sheets_service.cargar_datos()
            if df_raw.empty:
                logger.warning("No se encontraron datos en la hoja")
                return False

            # Procesar datos
            df_processed = sheets_service.procesar_datos(df_raw)
            logger.info(f"Datos procesados exitosamente: {len(df_processed)} registros")

            return True

        except SheetsConnectionError:
            raise
        except Exception as e:
            logger.error(f"Error cargando datos: {str(e)}")
            raise SheetsConnectionError(
                f"Error inesperado cargando datos: {str(e)}",
                error_code="SHEETS_LOAD_ERROR"
            )

    @log_execution_time
    @handle_exceptions(DataAnalysisError)
    def ejecutar_analisis_estadistico(self) -> Dict[str, Any]:
        """
        Ejecuta el análisis estadístico de los datos.

        Returns:
            Dict[str, Any]: Resultados del análisis
        """
        try:
            logger.info("Ejecutando análisis estadístico...")

            data_service = self.services['data_analysis']
            sheets_service = self.services['sheets']

            # Obtener DataFrame procesado
            df = sheets_service.get_dataframe()
            if df is None or df.empty:
                raise DataAnalysisError(
                    "No hay datos disponibles para análisis",
                    error_code="NO_DATA_FOR_ANALYSIS"
                )

            # Generar análisis completo
            resumen = data_service.generar_resumen(df)

            # Mostrar resumen en consola
            data_service.mostrar_resumen()

            # Calcular KPIs adicionales
            kpis = data_service.calcular_metricas_kpi(df)

            # Análisis de tendencias
            tendencias = data_service.analizar_tendencias(df, periodo="mensual")

            # Combinar todos los resultados
            self.analyzer_results = {
                'resumen_principal': resumen,
                'kpis_adicionales': kpis,
                'analisis_tendencias': tendencias,
                'timestamp_analisis': datetime.now().isoformat()
            }

            # Preparar datos para IA y email
            self.resumen_datos = self._preparar_datos_para_ia(resumen)

            logger.info("Análisis estadístico completado exitosamente")
            return self.analyzer_results

        except DataAnalysisError:
            raise
        except Exception as e:
            logger.error(f"Error en análisis estadístico: {str(e)}")
            raise DataAnalysisError(
                f"Fallo inesperado en análisis: {str(e)}",
                error_code="ANALYSIS_UNEXPECTED_ERROR"
            )

    def _preparar_datos_para_ia(self, resumen: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepara datos del resumen para análisis con IA.

        Args:
            resumen: Resumen del análisis

        Returns:
            Dict[str, Any]: Datos preparados para IA
        """
        metricas = resumen.get('metricas_ventas', {})
        return {
            'ventas_totales': metricas.get('ventas_totales', 0),
            'ticket_promedio': metricas.get('ticket_promedio', 0),
            'transacciones': metricas.get('num_transacciones', 0),
            'top_productos': dict(list(resumen.get('top_productos', {}).items())[:3])
        }

    @log_execution_time
    def ejecutar_analisis_ia(self) -> Optional[str]:
        """
        Ejecuta análisis estratégico con IA usando Ollama.

        Returns:
            Optional[str]: Análisis de IA o None si hay error
        """
        try:
            logger.info("Iniciando análisis estratégico con Ollama...")

            if not self.resumen_datos:
                logger.warning("No hay datos de resumen para análisis con IA")
                return None

            # Usar el servicio de Ollama
            resultado_ia = self.ai_service.generar_analisis_ia(self.resumen_datos)
            
            if resultado_ia.get('status') == 'success':
                analisis_ia = resultado_ia.get('analysis', '')
                modelo_usado = resultado_ia.get('model_used', 'unknown')
                
                logger.info(f"Análisis con IA completado exitosamente usando {modelo_usado}")

                # Mostrar resultados
                print("\nRESULTADOS DEL ANÁLISIS ESTRATÉGICO:")
                print("=" * 50)
                print(f"Modelo usado: {modelo_usado}")
                print("-" * 30)
                print(analisis_ia)
                print("=" * 50)

                return analisis_ia
            else:
                # Si hay error, usar el análisis básico incluido
                analisis_basico = resultado_ia.get('analysis', '')
                error = resultado_ia.get('error', 'Error desconocido')
                
                logger.warning(f"Ollama no disponible ({error}), usando análisis básico")
                
                # Mostrar análisis básico
                print("\nRESULTADOS DEL ANÁLISIS (BÁSICO):")
                print("=" * 50)
                print("Nota: Ollama no disponible, análisis básico generado")
                print("-" * 30)
                print(analisis_basico)
                print("=" * 50)
                
                return analisis_basico

        except Exception as e:
            logger.error(f"Error inesperado en análisis con IA: {str(e)}")
            return None

    @log_execution_time
    def generar_reporte(self, analisis_ia: Optional[str] = None) -> str:
        """
        Genera reporte en archivo de texto.

        Args:
            analisis_ia: Análisis opcional de IA

        Returns:
            str: Ruta del archivo de reporte generado
        """
        try:
            logger.info("Generando reporte empresarial...")

            archivo_reporte = settings.base.REPORTS_DIR / 'reporte_empresarial.txt'

            with open(archivo_reporte, 'w', encoding='utf-8') as f:
                # Encabezado
                f.write(f"REPORTE EMPRESARIAL DE ANÁLISIS DE VENTAS\n")
                f.write(f"Generado por: {settings.base.PROJECT_NAME} v{settings.base.VERSION}\n")
                f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")

                # Resumen ejecutivo
                f.write("RESUMEN EJECUTIVO\n")
                f.write("-" * 20 + "\n")
                sheets_service = self.services['sheets']
                df = sheets_service.get_dataframe()
                if df is not None:
                    f.write(f"Registros analizados: {len(df):,}\n")

                f.write(f"Volumen de ventas: {FormatUtils.format_currency(self.resumen_datos.get('ventas_totales', 0))}\n")
                f.write(f"Ticket promedio: {FormatUtils.format_currency(self.resumen_datos.get('ticket_promedio', 0))}\n")
                f.write(f"Transacciones: {self.resumen_datos.get('transacciones', 0):,}\n\n")

                # Análisis estratégico con IA
                if analisis_ia:
                    f.write("ANÁLISIS ESTRATÉGICO CON IA\n")
                    f.write("-" * 30 + "\n")
                    f.write(analisis_ia)
                    f.write("\n\n")

                # Top productos
                f.write("PRODUCTOS DE MAYOR RENDIMIENTO\n")
                f.write("-" * 35 + "\n")
                if self.analyzer_results and 'resumen_principal' in self.analyzer_results:
                    top_productos = self.analyzer_results['resumen_principal'].get('top_productos', {})
                    for i, (prod, venta) in enumerate(top_productos.items(), 1):
                        f.write(f"{i:2d}. {prod}: {FormatUtils.format_currency(venta)}\n")

                # KPIs adicionales
                if self.analyzer_results and 'kpis_adicionales' in self.analyzer_results:
                    f.write("\nKPIs ADICIONALES\n")
                    f.write("-" * 20 + "\n")
                    kpis = self.analyzer_results['kpis_adicionales']
                    for kpi, valor in kpis.items():
                        if isinstance(valor, (int, float)):
                            f.write(f"{kpi.replace('_', ' ').title()}: {valor:,.2f}\n")

            logger.info(f"Reporte generado: {archivo_reporte}")
            return str(archivo_reporte)

        except Exception as e:
            logger.error(f"Error generando reporte: {str(e)}")
            raise SistemaVentasError(
                f"Error generando reporte: {str(e)}",
                error_code="REPORT_GENERATION_ERROR"
            )

    @log_execution_time
    @handle_exceptions(EmailServiceError)
    def enviar_reporte_automatico(self, archivo_reporte: str) -> bool:
        """
        Envía el reporte automáticamente por email.

        Args:
            archivo_reporte: Ruta del archivo de reporte

        Returns:
            bool: True si el envío fue exitoso
        """
        try:
            logger.info("Enviando reporte automáticamente por email...")

            email_service = self.services['email']

            # Enviar reporte
            exito = email_service.enviar_reporte_automatico(
                datos_resumen=self.resumen_datos,
                archivo_reporte=archivo_reporte
            )

            if exito:
                logger.info("Reporte enviado exitosamente por email")
            else:
                logger.warning("El envío de email no fue completamente exitoso")

            return exito

        except EmailServiceError:
            raise
        except Exception as e:
            logger.error(f"Error enviando reporte: {str(e)}")
            raise EmailServiceError(
                f"Error inesperado enviando reporte: {str(e)}",
                error_code="EMAIL_SEND_UNEXPECTED"
            )

    @log_execution_time
    def ejecutar_analisis_completo(self, nombre_hoja: str = "DB_sales") -> Optional[Dict[str, Any]]:
        """
        Ejecuta el análisis completo del sistema.
        Método principal que coordina todo el flujo.

        Args:
            nombre_hoja: Nombre de la hoja de Google Sheets

        Returns:
            Optional[Dict[str, Any]]: Resultados del análisis o None si hay error
        """
        try:
            print("SISTEMA EMPRESARIAL DE ANÁLISIS DE VENTAS")
            print("=" * 50)
            print(f"Versión: {settings.base.VERSION}")
            print(f"Configuración de email desde: {settings.email.FROM_EMAIL}")
            print()

            # 1. Inicializar servicios
            if not self.inicializar_servicios():
                logger.error("Error en inicialización de servicios")
                return None

            # 2. Cargar datos desde Google Sheets
            if not self.cargar_datos_sheets(nombre_hoja):
                logger.error("Error cargando datos desde Google Sheets")
                return None

            # 3. Ejecutar análisis estadístico
            resultados_analisis = self.ejecutar_analisis_estadistico()
            if not resultados_analisis:
                logger.error("Error en análisis estadístico")
                return None

            # 4. Ejecutar análisis con IA (Ollama)
            analisis_ia = self.ejecutar_analisis_ia()
            if analisis_ia:
                resultados_analisis['analisis_ia'] = analisis_ia
                # Incluir análisis de IA en datos para email
                self.resumen_datos['analisis_ia'] = {
                    'disponible': True,
                    'contenido': analisis_ia
                }
            else:
                # Marcar como no disponible si no hay análisis de IA
                self.resumen_datos['analisis_ia'] = {
                    'disponible': False,
                    'contenido': 'Análisis con IA no disponible. Verifique que Ollama esté ejecutándose.'
                }

            # 5. Generar reporte
            archivo_reporte = self.generar_reporte(analisis_ia)

            # 6. Enviar reporte por email
            envio_exitoso = self.enviar_reporte_automatico(archivo_reporte)

            # 7. Resultado final
            resultado_final = {
                'analisis_completado': True,
                'archivo_reporte': archivo_reporte,
                'email_enviado': envio_exitoso,
                'resultados': resultados_analisis,
                'timestamp': datetime.now().isoformat()
            }

            print("\n" + "=" * 50)
            print("ANÁLISIS EMPRESARIAL COMPLETADO")
            print("=" * 50)
            print(f"[OK] Análisis estadístico: Completado")
            print(f"{'[OK]' if analisis_ia else '[WARN]'} Análisis con IA: {'Completado' if analisis_ia else 'No disponible'}")
            print(f"[OK] Reporte generado: {archivo_reporte}")
            print(f"{'[OK]' if envio_exitoso else '[ERROR]'} Email enviado: {'Exitoso' if envio_exitoso else 'Falló'}")
            print("=" * 50)

            return resultado_final

        except SistemaVentasError as e:
            logger.error(f"Error del sistema: {str(e)}")
            print(f"\nERROR EN PROCESAMIENTO: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado en análisis completo: {str(e)}")
            print(f"\nERROR INESPERADO: {str(e)}")
            return None

    def mostrar_estado_ia(self) -> None:
        """Muestra el estado del servicio de Ollama"""
        try:
            print("\n" + "="*50)
            print("ESTADO DEL SERVICIO DE OLLAMA")
            print("="*50)
            print(f"Ollama URL: {self.ai_service.ollama_url}")
            print(f"Modelo: {self.ai_service.ollama_model}")
            print("="*50)
            
        except Exception as e:
            logger.error(f"Error al mostrar estado de Ollama: {e}")
            print(f"Error al obtener estado de Ollama: {e}")


# =============================================================================
# FUNCIÓN PRINCIPAL PARA COMPATIBILIDAD
# =============================================================================

@log_execution_time
def analisis_empresarial(nombre_hoja: str = "DB_sales") -> Optional[Dict[str, Any]]:
    """
    Función principal para análisis empresarial.
    Mantiene compatibilidad con el código original.

    Args:
        nombre_hoja: Nombre de la hoja de Google Sheets

    Returns:
        Optional[Dict[str, Any]]: Resultados del análisis
    """
    sistema = SistemaVentasMain()
    return sistema.ejecutar_analisis_completo(nombre_hoja)


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    """Punto de entrada principal del sistema."""
    try:
        logger.info("Iniciando Sistema Empresarial de Análisis de Ventas")

        resultado = analisis_empresarial("DB_sales")

        if resultado and resultado.get('analisis_completado'):
            logger.info("Sistema ejecutado exitosamente")
            return 0
        else:
            logger.error("El sistema no completó exitosamente")
            return 1

    except KeyboardInterrupt:
        logger.info("Ejecución interrumpida por el usuario")
        print("\nEjecución cancelada por el usuario")
        return 130
    except Exception as e:
        logger.error(f"Error crítico en main: {str(e)}")
        print(f"\nERROR CRÍTICO: {str(e)}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
