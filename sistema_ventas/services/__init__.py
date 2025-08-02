"""
Servicios del Sistema de Análisis de Ventas
===========================================

Módulo que contiene todos los servicios de negocio del sistema.
Implementa la capa de servicios siguiendo el patrón Clean Architecture.

Servicios disponibles:
- EmailService: Servicio para envío de emails y reportes
- SheetsService: Servicio para conexión con Google Sheets
- DataAnalysisService: Servicio para análisis de datos de ventas

Cada servicio implementa su respectiva interfaz del módulo core.interfaces
y maneja su propia lógica de negocio específica.
"""

import smtplib
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from ..core.interfaces.email_interface import EmailServiceInterface
from ..core.exceptions import (
    EmailServiceError,
    EmailConfigurationError,
    EmailConnectionError,
    EmailSendError
)
from ..config import settings


class EmailService(EmailServiceInterface):
    """
    Servicio de email implementando la interfaz EmailServiceInterface.
    Migración mejorada de EmailManager original.
    """

    def __init__(self, config=None):
        """
        Inicializa el servicio de email.

        Args:
            config: Configuración opcional, usa settings.email por defecto
        """
        self.config = config or settings.email
        self._template_service = None
        self._validate_configuration_on_init()

    def _validate_configuration_on_init(self):
        """Valida la configuración al inicializar."""
        if not self.validar_configuracion():
            raise EmailConfigurationError(
                "Configuración de email inválida",
                error_code="EMAIL_CONFIG_INVALID",
                details={"required_fields": ["SMTP_SERVER", "SMTP_USER", "SMTP_PASSWORD", "FROM_EMAIL"]}
            )

    def validar_configuracion(self) -> bool:
        """
        Valida que la configuración del servicio de email sea correcta.

        Returns:
            bool: True si la configuración es válida

        Raises:
            ConfigurationError: Si la configuración es inválida
        """
        try:
            required_fields = [
                self.config.SMTP_SERVER,
                self.config.SMTP_USER,
                self.config.SMTP_PASSWORD,
                self.config.FROM_EMAIL,
                self.config.DEFAULT_TO_EMAIL
            ]
            return all(field for field in required_fields)
        except AttributeError as e:
            raise EmailConfigurationError(
                f"Configuración faltante: {str(e)}",
                error_code="EMAIL_CONFIG_MISSING"
            )

    def probar_conexion(self) -> bool:
        """
        Prueba la conexión con el servidor de email.

        Returns:
            bool: True si la conexión es exitosa

        Raises:
            ConnectionError: Si no se puede establecer conexión
        """
        try:
            server = smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT)
            server.starttls()
            server.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)
            server.quit()
            return True
        except smtplib.SMTPAuthenticationError as e:
            raise EmailConnectionError(
                "Error de autenticación SMTP",
                error_code="SMTP_AUTH_ERROR",
                details={"smtp_response": str(e)}
            )
        except smtplib.SMTPConnectError as e:
            raise EmailConnectionError(
                "Error de conexión SMTP",
                error_code="SMTP_CONNECT_ERROR",
                details={"server": self.config.SMTP_SERVER, "port": self.config.SMTP_PORT}
            )
        except Exception as e:
            raise EmailConnectionError(
                f"Error desconocido al conectar: {str(e)}",
                error_code="SMTP_UNKNOWN_ERROR"
            )

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
        try:
            print(f"Enviando reporte a: {self.config.DEFAULT_TO_EMAIL}")

            # Crear conexión SMTP
            server = self._crear_conexion_smtp()

            # Crear mensaje
            msg = self._crear_mensaje_reporte(
                destinatario=self.config.DEFAULT_TO_EMAIL,
                datos_resumen=datos_resumen,
                archivo_reporte=archivo_reporte
            )

            # Enviar mensaje
            server.send_message(msg)
            server.quit()

            print("Email enviado exitosamente!")
            return True

        except EmailServiceError:
            # Re-raise errores ya manejados
            raise
        except Exception as e:
            raise EmailSendError(
                f"Error inesperado enviando email: {str(e)}",
                error_code="EMAIL_SEND_UNEXPECTED",
                details={"recipient": self.config.DEFAULT_TO_EMAIL}
            )

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
        if not destinatarios:
            raise EmailServiceError(
                "Lista de destinatarios vacía",
                error_code="EMPTY_RECIPIENTS_LIST"
            )

        resultados = {}
        errores = []

        try:
            print(f"Enviando reporte a: {', '.join(destinatarios)}")

            # Crear conexión SMTP una sola vez
            server = self._crear_conexion_smtp()

            for destinatario in destinatarios:
                try:
                    # Crear mensaje para cada destinatario
                    msg = self._crear_mensaje_reporte(
                        destinatario=destinatario,
                        datos_resumen=datos_resumen,
                        archivo_reporte=archivo_reporte
                    )

                    # Enviar mensaje
                    server.send_message(msg)
                    resultados[destinatario] = True
                    print(f"Email enviado a: {destinatario}")

                except Exception as e:
                    resultados[destinatario] = False
                    errores.append(f"{destinatario}: {str(e)}")
                    print(f"Error enviando a {destinatario}: {str(e)}")

            server.quit()

            if errores:
                print(f"Se completó el envío con {len(errores)} errores")
            else:
                print("Todos los emails enviados exitosamente!")

            return resultados

        except EmailServiceError:
            # Re-raise errores ya manejados
            raise
        except Exception as e:
            raise EmailSendError(
                f"Error crítico en envío múltiple: {str(e)}",
                error_code="MULTIPLE_EMAIL_SEND_ERROR",
                details={"recipients": destinatarios, "partial_results": resultados}
            )

    def _crear_conexion_smtp(self) -> smtplib.SMTP:
        """
        Crea y autentica una conexión SMTP.

        Returns:
            smtplib.SMTP: Conexión SMTP autenticada

        Raises:
            EmailConnectionError: Si no se puede establecer la conexión
        """
        try:
            server = smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT)
            server.starttls()
            server.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)
            return server
        except smtplib.SMTPAuthenticationError as e:
            raise EmailConnectionError(
                "Error de autenticación SMTP",
                error_code="SMTP_AUTH_ERROR",
                details={"smtp_response": str(e)}
            )
        except smtplib.SMTPConnectError as e:
            raise EmailConnectionError(
                "Error de conexión SMTP",
                error_code="SMTP_CONNECT_ERROR",
                details={"server": self.config.SMTP_SERVER, "port": self.config.SMTP_PORT}
            )
        except Exception as e:
            raise EmailConnectionError(
                f"Error estableciendo conexión SMTP: {str(e)}",
                error_code="SMTP_CONNECTION_FAILED"
            )

    def _crear_mensaje_reporte(
        self,
        destinatario: str,
        datos_resumen: Dict[str, Any],
        archivo_reporte: Optional[str] = None
    ) -> MIMEMultipart:
        """
        Crea un mensaje de email con el reporte.

        Args:
            destinatario: Email del destinatario
            datos_resumen: Datos del resumen
            archivo_reporte: Archivo adjunto opcional

        Returns:
            MIMEMultipart: Mensaje de email construido
        """
        msg = MIMEMultipart()
        msg['From'] = f"{self.config.FROM_NAME} <{self.config.FROM_EMAIL}>"
        msg['To'] = destinatario

        # Crear subject usando template
        fecha_actual = datetime.now().strftime('%d/%m/%Y')
        msg['Subject'] = self.config.SUBJECT_TEMPLATE.format(fecha=fecha_actual)

        # Crear contenido HTML únicamente
        try:
            # Generar template HTML
            html_content = self._generar_contenido_html(datos_resumen)
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        except Exception as e:
            print(f"Advertencia: Error generando HTML, usando template básico: {str(e)}")
            # Fallback a HTML básico
            contenido_html_basico = self._generar_html_basico(datos_resumen)
            msg.attach(MIMEText(contenido_html_basico, 'html', 'utf-8'))

        # Adjuntar archivo si existe
        if archivo_reporte and os.path.exists(archivo_reporte):
            self._adjuntar_archivo(msg, archivo_reporte)

        return msg

    def _get_template_service(self):
        """Obtiene el servicio de templates HTML de manera lazy."""
        if self._template_service is None:
            try:
                from .html_template_service import HTMLTemplateService
                self._template_service = HTMLTemplateService()
            except ImportError as e:
                print(f"Advertencia: No se pudo cargar HTMLTemplateService: {str(e)}")
                self._template_service = False
        return self._template_service

    def _generar_contenido_html(self, datos_resumen: Dict[str, Any]) -> str:
        """
        Genera el contenido del reporte en formato HTML.

        Args:
            datos_resumen: Datos del resumen

        Returns:
            str: Contenido HTML del reporte

        Raises:
            Exception: Si no se puede generar el HTML
        """
        template_service = self._get_template_service()

        if not template_service:
            raise Exception("Servicio de templates HTML no disponible")

        return template_service.render_email_report(datos_resumen)

    def _generar_contenido_texto_plano(self, datos_resumen: Dict[str, Any]) -> str:
        """
        Genera el contenido del reporte en formato texto plano.

        Args:
            datos_resumen: Datos del resumen

        Returns:
            str: Contenido formateado del reporte
        """
        # Intentar usar el servicio de templates para el fallback
        template_service = self._get_template_service()

        if template_service:
            try:
                return template_service.generate_plain_text_fallback(datos_resumen)
            except Exception:
                pass  # Continuar con el método original

        # Método original como fallback final
        fecha_actual = datetime.now().strftime('%d/%m/%Y %H:%M')

        # Extraer métricas con manejo mejorado
        metricas = datos_resumen.get('metricas_ventas', {})
        ventas_totales = metricas.get('ventas_totales', 0)
        ticket_promedio = metricas.get('ticket_promedio', 0)
        transacciones = metricas.get('transacciones', 0)

        contenido = f"""
REPORTE EMPRESARIAL AUTOMÁTICO
=============================
Fecha: {fecha_actual}

MÉTRICAS PRINCIPALES:
• Ventas Totales: ${ventas_totales:,.2f} MXN
• Ticket Promedio: ${ticket_promedio:,.2f} MXN
• Total Transacciones: {transacciones:,}

TOP PRODUCTOS:"""

        # Agregar top productos
        top_productos = datos_resumen.get('top_productos', {})
        if top_productos:
            for i, (producto, venta) in enumerate(list(top_productos.items())[:5], 1):
                contenido += f"\n{i}. {producto}: ${venta:,.2f} MXN"
        else:
            contenido += "\n• No hay datos de productos disponibles"

        contenido += f"""

INSIGHTS:
• Análisis automatizado de tendencias de ventas
• Identificación de productos de alto rendimiento
• Métricas de performance empresarial

---
Generado automáticamente por {settings.base.PROJECT_NAME}
Este reporte es confidencial y de uso interno exclusivo.
        """

        return contenido.strip()

    def _generar_html_basico(self, datos_resumen: Dict[str, Any]) -> str:
        """
        Genera contenido HTML básico como fallback cuando fallan los templates.

        Args:
            datos_resumen: Datos del resumen

        Returns:
            str: Contenido HTML básico
        """
        fecha_actual = datetime.now().strftime('%d/%m/%Y %H:%M')

        # Extraer métricas con manejo mejorado
        metricas = datos_resumen.get('metricas_ventas', {})
        ventas_totales = metricas.get('ventas_totales', 0)
        ticket_promedio = metricas.get('ticket_promedio', 0)
        transacciones = metricas.get('transacciones', 0)

        # Top productos
        top_productos = datos_resumen.get('top_productos', {})
        productos_html = ""
        if top_productos:
            for i, (producto, venta) in enumerate(list(top_productos.items())[:5], 1):
                productos_html += f"<tr><td>{i}</td><td>{producto}</td><td style='text-align: right'>${venta:,.2f} MXN</td></tr>"
        else:
            productos_html = "<tr><td colspan='3' style='text-align: center'>No hay datos disponibles</td></tr>"

        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reporte de Ventas</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">REPORTE EMPRESARIAL DE VENTAS</h1>
                <p style="margin: 10px 0 0; opacity: 0.9;">Fecha: {fecha_actual}</p>
            </div>
            <div style="background: #ffffff; padding: 30px; border: 1px solid #ddd; border-radius: 0 0 8px 8px;">
                <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">MÉTRICAS PRINCIPALES</h2>
                <table style="width: 100%; margin-bottom: 20px; border-collapse: collapse;">
                    <tr style="background: #f8f9fa;">
                        <td style="padding: 15px; border: 1px solid #dee2e6; font-weight: bold;">VENTAS TOTALES</td>
                        <td style="padding: 15px; border: 1px solid #dee2e6; text-align: right; color: #28a745; font-weight: bold;">${ventas_totales:,.2f} MXN</td>
                    </tr>
                    <tr>
                        <td style="padding: 15px; border: 1px solid #dee2e6; font-weight: bold;">TICKET PROMEDIO</td>
                        <td style="padding: 15px; border: 1px solid #dee2e6; text-align: right; color: #17a2b8; font-weight: bold;">${ticket_promedio:,.2f} MXN</td>
                    </tr>
                    <tr style="background: #f8f9fa;">
                        <td style="padding: 15px; border: 1px solid #dee2e6; font-weight: bold;">TRANSACCIONES</td>
                        <td style="padding: 15px; border: 1px solid #dee2e6; text-align: right; color: #fd7e14; font-weight: bold;">{transacciones:,}</td>
                    </tr>
                </table>

                <h2 style="color: #2c3e50; border-bottom: 2px solid #28a745; padding-bottom: 10px;">TOP PRODUCTOS</h2>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    <tr style="background: #343a40; color: white;">
                        <th style="padding: 10px; border: 1px solid #dee2e6;">RANK</th>
                        <th style="padding: 10px; border: 1px solid #dee2e6;">PRODUCTO</th>
                        <th style="padding: 10px; border: 1px solid #dee2e6;">VENTAS</th>
                    </tr>
                    {productos_html}
                </table>
            </div>
            <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
                <p>Generado automáticamente por <strong>{settings.base.PROJECT_NAME}</strong></p>
                <p>Información Confidencial - Uso Interno Exclusivo</p>
            </div>
        </body>
        </html>
        """

        return html_content.strip()

    def _adjuntar_archivo(self, msg: MIMEMultipart, archivo_reporte: str):
        """
        Adjunta un archivo al mensaje de email.

        Args:
            msg: Mensaje al que adjuntar el archivo
            archivo_reporte: Ruta del archivo a adjuntar
        """
        try:
            with open(archivo_reporte, 'rb') as f:
                adjunto = MIMEApplication(f.read())
                adjunto.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{os.path.basename(archivo_reporte)}"'
                )
                msg.attach(adjunto)
        except FileNotFoundError:
            print(f"Advertencia: Archivo no encontrado: {archivo_reporte}")
        except Exception as e:
            print(f"Advertencia: Error adjuntando archivo {archivo_reporte}: {str(e)}")


# =============================================================================
# IMPORTAR OTROS SERVICIOS
# =============================================================================

# Importar servicios desde sus módulos específicos
from .sheets_service import SheetsService
from .data_analysis_service import DataAnalysisService

# =============================================================================
# FUNCIONES DE UTILIDAD PARA SERVICIOS
# =============================================================================

def get_available_services():
    """
    Obtiene lista de servicios disponibles.

    Returns:
        dict: Diccionario con servicios disponibles
    """
    return {
        'email': EmailService,
        'sheets': SheetsService,
        'data_analysis': DataAnalysisService
    }


def validate_service_health(service_instance):
    """
    Valida el estado de salud de un servicio.

    Args:
        service_instance: Instancia del servicio

    Returns:
        dict: Estado de salud del servicio
    """
    health_status = {
        'service_name': type(service_instance).__name__,
        'is_healthy': True,
        'checks': {},
        'errors': []
    }

    try:
        # Verificar configuración
        if hasattr(service_instance, 'validar_configuracion'):
            health_status['checks']['configuration'] = service_instance.validar_configuracion()
        elif hasattr(service_instance, 'validate_configuration'):
            health_status['checks']['configuration'] = service_instance.validate_configuration()

        # Verificar conectividad
        if hasattr(service_instance, 'probar_conexion'):
            health_status['checks']['connectivity'] = service_instance.probar_conexion()
        elif hasattr(service_instance, 'probar_conectividad'):
            health_status['checks']['connectivity'] = service_instance.probar_conectividad()

        # Determinar salud general
        health_status['is_healthy'] = all(health_status['checks'].values())

    except Exception as e:
        health_status['is_healthy'] = False
        health_status['errors'].append(str(e))

    return health_status


# =============================================================================
# EXPORTACIONES DEL MÓDULO
# =============================================================================

__all__ = [
    # Servicios principales
    'EmailService',
    'SheetsService',
    'DataAnalysisService',

    # Funciones de utilidad
    'get_available_services',
    'validate_service_health'
]

# Información del módulo
__version__ = "2.0.0"
__description__ = "Servicios del Sistema de Análisis de Ventas"
