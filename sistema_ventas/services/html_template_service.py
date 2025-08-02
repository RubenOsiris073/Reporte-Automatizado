"""
HTML Template Service para Sistema de Análisis de Ventas
======================================================

Servicio especializado en el manejo de templates HTML para correos electrónicos.
Proporciona funcionalidades para cargar, renderizar y personalizar plantillas HTML
de manera profesional y compatible con diferentes clientes de email.

Author: Sistema Empresarial de Ventas
Version: 2.0.0
"""

import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from ..core.exceptions import (
    SistemaVentasError,
    ConfigurationError,
    TemplateError
)
from ..config import settings


class TemplateError(SistemaVentasError):
    """Excepción específica para errores de templates."""
    pass


class HTMLTemplateService:
    """
    Servicio para manejo de templates HTML profesionales.

    Características:
    - Carga de templates desde archivos
    - Renderizado con datos dinámicos
    - Compatibilidad con múltiples clientes de email
    - Generación de contenido responsivo
    - Manejo de fallbacks para texto plano
    """

    def __init__(self, templates_dir: Optional[str] = None):
        """
        Inicializa el servicio de templates HTML.

        Args:
            templates_dir: Directorio de templates (opcional)
        """
        self.templates_dir = Path(templates_dir) if templates_dir else self._get_default_templates_dir()
        self._templates_cache = {}
        self._validate_templates_directory()

    def _get_default_templates_dir(self) -> Path:
        """Obtiene el directorio por defecto de templates."""
        current_dir = Path(__file__).parent.parent
        templates_dir = current_dir / "templates"
        return templates_dir

    def _validate_templates_directory(self):
        """Valida que el directorio de templates exista."""
        if not self.templates_dir.exists():
            raise ConfigurationError(
                f"Directorio de templates no encontrado: {self.templates_dir}",
                error_code="TEMPLATES_DIR_NOT_FOUND"
            )

    def load_template(self, template_name: str, use_cache: bool = True) -> str:
        """
        Carga un template HTML desde archivo.

        Args:
            template_name: Nombre del template (con o sin extensión .html)
            use_cache: Si usar caché de templates

        Returns:
            str: Contenido HTML del template

        Raises:
            TemplateError: Si el template no se puede cargar
        """
        # Normalizar nombre del template
        if not template_name.endswith('.html'):
            template_name += '.html'

        # Verificar caché
        if use_cache and template_name in self._templates_cache:
            return self._templates_cache[template_name]

        # Buscar archivo de template
        template_path = self.templates_dir / template_name

        if not template_path.exists():
            raise TemplateError(
                f"Template no encontrado: {template_name}",
                error_code="TEMPLATE_NOT_FOUND",
                details={"template_path": str(template_path)}
            )

        try:
            # Cargar contenido del template
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            # Guardar en caché
            if use_cache:
                self._templates_cache[template_name] = template_content

            return template_content

        except UnicodeDecodeError as e:
            raise TemplateError(
                f"Error de codificación en template {template_name}: {str(e)}",
                error_code="TEMPLATE_ENCODING_ERROR"
            )
        except Exception as e:
            raise TemplateError(
                f"Error cargando template {template_name}: {str(e)}",
                error_code="TEMPLATE_LOAD_ERROR"
            )

    def render_email_report(
        self,
        datos_resumen: Dict[str, Any],
        template_name: str = "email_report.html",
        use_simple_fallback: bool = True
    ) -> str:
        """
        Renderiza un reporte de email usando template HTML.

        Args:
            datos_resumen: Datos del resumen de ventas
            template_name: Nombre del template a usar
            use_simple_fallback: Si usar template simple en caso de error

        Returns:
            str: HTML renderizado del reporte

        Raises:
            TemplateError: Si no se puede renderizar el template
        """
        try:
            # Cargar template
            template_html = self.load_template(template_name)

            # Preparar datos para renderizado
            template_data = self._prepare_template_data(datos_resumen, template_name)

            # Renderizar template
            rendered_html = self._render_template(template_html, template_data)

            return rendered_html

        except TemplateError as e:
            if use_simple_fallback and template_name != "email_report_simple.html":
                print(f"Advertencia: Error con template principal, usando fallback: {str(e)}")
                return self.render_email_report(
                    datos_resumen,
                    "email_report_simple.html",
                    use_simple_fallback=False
                )
            raise

    def _prepare_template_data(self, datos_resumen: Dict[str, Any], template_name: str = "") -> Dict[str, Any]:
        """
        Prepara los datos para ser usados en el template.

        Args:
            datos_resumen: Datos originales del resumen

        Returns:
            Dict[str, Any]: Datos preparados para el template
        """
        # Fecha actual formateada
        fecha_actual = datetime.now()
        fecha_formateada = fecha_actual.strftime('%d de %B de %Y')
        timestamp_completo = fecha_actual.strftime('%d/%m/%Y %H:%M:%S')

        # Extraer métricas principales
        metricas = datos_resumen.get('metricas_ventas', {})

        # Formatear números - verificar múltiples fuentes de datos
        ventas_totales = self._format_currency(
            metricas.get('ventas_totales', 0) or
            datos_resumen.get('ventas_totales', 0)
        )
        ticket_promedio = self._format_currency(
            metricas.get('ticket_promedio', 0) or
            datos_resumen.get('ticket_promedio', 0)
        )
        total_transacciones = self._format_number(
            metricas.get('transacciones', 0) or
            metricas.get('num_transacciones', 0) or
            datos_resumen.get('transacciones', 0) or
            datos_resumen.get('num_transacciones', 0)
        )

        # Preparar top productos
        top_productos = datos_resumen.get('top_productos', {})
        top_productos_rows = self._generate_top_products_rows(top_productos, template_name)

        # Generar insights
        insights_principales = self._generate_insights_list(datos_resumen)

        # Estadísticas adicionales
        productos_activos = len(top_productos) if top_productos else 0
        crecimiento_porcentaje = self._calculate_growth_percentage(datos_resumen)

        # Análisis IA (si está disponible)
        analisis_ia = datos_resumen.get('analisis_ia', {})
        analisis_ia_contenido = self._format_ia_analysis(analisis_ia)

        # Periodo de análisis
        periodo_analisis = self._get_analysis_period(datos_resumen)

        template_data = {
            # Información básica
            'fecha': fecha_formateada,
            'timestamp': timestamp_completo,
            'project_name': settings.base.PROJECT_NAME,
            'periodo_analisis': periodo_analisis,

            # Métricas principales
            'ventas_totales': ventas_totales,
            'ticket_promedio': ticket_promedio,
            'total_transacciones': total_transacciones,

            # Top productos
            'top_productos_rows': top_productos_rows,

            # Análisis
            'insights_principales': insights_principales,
            'crecimiento_porcentaje': crecimiento_porcentaje,
            'productos_activos': productos_activos,

            # IA
            'analisis_ia_contenido': analisis_ia_contenido,
        }

        return template_data

    def _render_template(self, template_html: str, data: Dict[str, Any]) -> str:
        """
        Renderiza el template HTML con los datos proporcionados.

        Args:
            template_html: HTML del template
            data: Datos para reemplazar

        Returns:
            str: HTML renderizado
        """
        rendered_html = template_html

        # Reemplazar variables simples usando format
        try:
            rendered_html = rendered_html.format(**data)
        except KeyError as e:
            # Si falta alguna variable, usar valor por defecto
            missing_var = str(e).strip("'")
            print(f"Advertencia: Variable faltante en template: {missing_var}")
            data[missing_var] = f"[{missing_var}]"
            rendered_html = rendered_html.format(**data)

        return rendered_html

    def _format_currency(self, amount: Union[int, float]) -> str:
        """Formatea un número como moneda."""
        try:
            return f"${float(amount):,.2f}"
        except (ValueError, TypeError):
            return "$0.00"

    def _format_number(self, number: Union[int, float]) -> str:
        """Formatea un número con separadores de miles."""
        try:
            return f"{int(number):,}"
        except (ValueError, TypeError):
            return "0"

    def _generate_top_products_rows(self, top_productos: Dict[str, Any], template_name: str = "") -> str:
        """
        Genera las filas HTML para la tabla de top productos.

        Args:
            top_productos: Diccionario con productos y ventas
            template_name: Nombre del template para determinar el formato

        Returns:
            str: HTML de las filas de productos
        """
        if not top_productos:
            # Mensaje de no datos dependiendo del template
            if "compact" in template_name.lower():
                return '<tr><td colspan="2" style="text-align: center; padding: 15px; color: #6c757d; font-size: 12px;">Sin datos</td></tr>'
            else:
                return '<tr><td colspan="4" style="text-align: center; padding: 20px; color: #6c757d;">No hay datos de productos disponibles</td></tr>'

        # Determinar si es template compacto
        is_compact = "compact" in template_name.lower()
        max_products = 3 if is_compact else 5

        rows_html = []
        total_ventas = sum(top_productos.values()) if top_productos else 1

        for i, (producto, venta) in enumerate(list(top_productos.items())[:max_products], 1):
            porcentaje = (venta / total_ventas * 100) if total_ventas > 0 else 0

            if is_compact:
                # Formato compacto para template compact
                bg_color = "#f8f9fa" if i % 2 == 0 else "#ffffff"
                row_html = f'''
                                <tr style="background-color: {bg_color};">
                                    <td style="border-bottom: 1px solid #dee2e6; font-weight: 500; color: #495057;">
                                        {i}. {producto}
                                    </td>
                                    <td style="border-bottom: 1px solid #dee2e6; text-align: right; font-weight: bold; color: #28a745;">
                                        {self._format_currency(venta)}
                                    </td>
                                </tr>'''
            else:
                # Formato completo para templates regulares
                bg_color = "#f8f9fa" if i % 2 == 0 else "#ffffff"
                row_html = f'''
                    <tr style="background-color: {bg_color};">
                        <td style="padding: 12px 15px; text-align: center; font-weight: bold; color: #495057; border-bottom: 1px solid #dee2e6;">{i}</td>
                        <td style="padding: 12px 15px; color: #212529; border-bottom: 1px solid #dee2e6;">{producto}</td>
                        <td style="padding: 12px 15px; text-align: right; font-weight: bold; color: #28a745; border-bottom: 1px solid #dee2e6;">{self._format_currency(venta)}</td>
                        <td style="padding: 12px 15px; text-align: center; color: #6c757d; border-bottom: 1px solid #dee2e6;">{porcentaje:.1f}%</td>
                    </tr>'''

            rows_html.append(row_html)

        return ''.join(rows_html)

    def _generate_insights_list(self, datos_resumen: Dict[str, Any]) -> str:
        """
        Genera una lista HTML de insights principales.

        Args:
            datos_resumen: Datos del resumen

        Returns:
            str: HTML con la lista de insights
        """
        insights = []

        # Insight sobre ventas totales
        metricas = datos_resumen.get('metricas_ventas', {})
        ventas_totales = metricas.get('ventas_totales', 0)
        if ventas_totales > 0:
            insights.append(f"<li>Se registraron ventas por ${self._format_currency(ventas_totales)} MXN en el período analizado</li>")

        # Insight sobre productos
        top_productos = datos_resumen.get('top_productos', {})
        if top_productos:
            mejor_producto = list(top_productos.keys())[0]
            insights.append(f"<li>El producto estrella fue <strong>{mejor_producto}</strong> con mayor volumen de ventas</li>")

        # Insight sobre transacciones
        transacciones = metricas.get('transacciones', 0)
        if transacciones > 0:
            insights.append(f"<li>Se procesaron un total de <strong>{self._format_number(transacciones)}</strong> transacciones</li>")

        # Insight sobre ticket promedio
        ticket_promedio = metricas.get('ticket_promedio', 0)
        if ticket_promedio > 0:
            insights.append(f"<li>El ticket promedio por transacción fue de <strong>${self._format_currency(ticket_promedio)} MXN</strong></li>")

        # Si no hay insights, agregar mensaje por defecto
        if not insights:
            insights.append("<li>Los datos están siendo procesados para generar insights detallados</li>")

        return ''.join(insights)

    def _calculate_growth_percentage(self, datos_resumen: Dict[str, Any]) -> str:
        """
        Calcula el porcentaje de crecimiento (simulado por ahora).

        Args:
            datos_resumen: Datos del resumen

        Returns:
            str: Porcentaje de crecimiento formateado
        """
        # Por ahora devolvemos un valor simulado
        # En futuras versiones se calculará con datos históricos
        return "+12.5"

    def _format_ia_analysis(self, analisis_ia: Dict[str, Any]) -> str:
        """
        Formatea el análisis de IA de Ollama para mostrar en HTML.

        Args:
            analisis_ia: Datos del análisis de IA

        Returns:
            str: HTML formateado del análisis
        """
        if not analisis_ia or not analisis_ia.get('disponible', False):
            return '''
                <div style="text-align: center; color: #6c757d; font-style: italic; padding: 20px;">
                    <p><strong>ANÁLISIS ESTRATÉGICO CON IA</strong></p>
                    <p>Servicio de análisis no disponible</p>
                    <p>Para habilitar: Ejecute Ollama en su sistema</p>
                </div>
            '''

        # Si hay análisis de IA disponible de Ollama
        contenido_ia = analisis_ia.get('contenido', 'Análisis en proceso...')

        # Procesar el contenido de Ollama para mejor formato HTML
        contenido_procesado = self._procesar_contenido_ollama(contenido_ia)

        return f'''
            <div style="background-color: rgba(255, 255, 255, 0.95); border-radius: 8px; padding: 20px;">
                <div style="color: #2c3e50; line-height: 1.7; font-size: 14px;">
                    {contenido_procesado}
                </div>
            </div>
        '''

    def _procesar_contenido_ollama(self, contenido: str) -> str:
        """
        Procesa el contenido de análisis de Ollama para mejor presentación en HTML.

        Args:
            contenido: Contenido raw de Ollama

        Returns:
            str: Contenido procesado para HTML
        """
        if not contenido:
            return "<p>Análisis no disponible</p>"

        # Dividir por líneas y procesar cada sección
        lineas = contenido.split('\n')
        html_procesado = []

        for linea in lineas:
            linea = linea.strip()
            if not linea:
                continue

            # Detectar secciones principales (que empiecen con mayúsculas seguidas de ':')
            if ':' in linea and linea.split(':')[0].isupper():
                seccion, contenido_seccion = linea.split(':', 1)
                html_procesado.append(f'''
                    <div style="margin: 15px 0 8px 0;">
                        <strong style="color: #1976d2; font-size: 15px; text-transform: uppercase;">
                            {seccion.strip()}:
                        </strong>
                    </div>
                    <div style="margin-left: 15px; color: #2c3e50;">
                        {contenido_seccion.strip()}
                    </div>
                ''')
            # Detectar puntos de lista (que empiecen con •, -, *, etc.)
            elif linea.startswith(('•', '-', '*', '+')):
                punto = linea[1:].strip()
                html_procesado.append(f'''
                    <div style="margin: 5px 0; padding-left: 20px; position: relative;">
                        <span style="position: absolute; left: 0; color: #1976d2; font-weight: bold;">•</span>
                        {punto}
                    </div>
                ''')
            # Líneas normales
            else:
                html_procesado.append(f'<p style="margin: 8px 0;">{linea}</p>')

        return ''.join(html_procesado) if html_procesado else f'<p>{contenido}</p>'

    def _get_analysis_period(self, datos_resumen: Dict[str, Any]) -> str:
        """
        Obtiene el período de análisis de los datos.

        Args:
            datos_resumen: Datos del resumen

        Returns:
            str: Descripción del período de análisis
        """
        # Por ahora devolvemos un período por defecto
        # En futuras versiones se extraerá de los datos reales
        return "Último período disponible"

    def generate_plain_text_fallback(self, datos_resumen: Dict[str, Any]) -> str:
        """
        Genera una versión en texto plano como fallback.

        Args:
            datos_resumen: Datos del resumen

        Returns:
            str: Reporte en texto plano
        """
        fecha_actual = datetime.now().strftime('%d/%m/%Y %H:%M')

        # Extraer métricas
        metricas = datos_resumen.get('metricas_ventas', {})
        ventas_totales = self._format_currency(metricas.get('ventas_totales', 0))
        ticket_promedio = self._format_currency(metricas.get('ticket_promedio', 0))
        transacciones = self._format_number(metricas.get('transacciones', 0))

        # Top productos
        top_productos = datos_resumen.get('top_productos', {})
        productos_text = []
        for i, (producto, venta) in enumerate(list(top_productos.items())[:5], 1):
            productos_text.append(f"{i}. {producto}: ${self._format_currency(venta)} MXN")

        contenido = f"""
REPORTE EMPRESARIAL AUTOMÁTICO
=============================
Fecha: {fecha_actual}

MÉTRICAS PRINCIPALES:
• Ventas Totales: ${ventas_totales} MXN
• Ticket Promedio: ${ticket_promedio} MXN
• Total Transacciones: {transacciones}

TOP 5 PRODUCTOS:
{chr(10).join(productos_text) if productos_text else '• No hay datos de productos disponibles'}

INSIGHTS:
• Análisis automatizado de tendencias de ventas
• Identificación de productos de alto rendimiento
• Métricas de performance empresarial

---
Generado automáticamente por {settings.base.PROJECT_NAME}
Este reporte es confidencial y de uso interno exclusivo.
        """

        return contenido.strip()

    def list_available_templates(self) -> List[str]:
        """
        Lista todos los templates disponibles.

        Returns:
            List[str]: Lista de nombres de templates
        """
        try:
            template_files = []
            for file_path in self.templates_dir.glob("*.html"):
                template_files.append(file_path.name)
            return sorted(template_files)
        except Exception as e:
            print(f"Error listando templates: {str(e)}")
            return []

    def clear_cache(self):
        """Limpia el caché de templates."""
        self._templates_cache.clear()
        print("Caché de templates limpiado")

    def validate_template(self, template_name: str) -> Dict[str, Any]:
        """
        Valida un template específico.

        Args:
            template_name: Nombre del template

        Returns:
            Dict[str, Any]: Resultado de la validación
        """
        validation_result = {
            'template_name': template_name,
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'size_kb': 0
        }

        try:
            # Cargar template
            template_content = self.load_template(template_name, use_cache=False)

            # Verificar tamaño
            template_size = len(template_content.encode('utf-8')) / 1024
            validation_result['size_kb'] = round(template_size, 2)

            # Advertir si es muy grande
            if template_size > 100:  # 100KB
                validation_result['warnings'].append("Template muy grande, puede causar problemas en algunos clientes de email")

            # Verificar variables requeridas
            required_vars = [
                'fecha', 'timestamp', 'project_name', 'ventas_totales',
                'ticket_promedio', 'total_transacciones', 'top_productos_rows'
            ]

            missing_vars = []
            for var in required_vars:
                if f'{{{var}}}' not in template_content:
                    missing_vars.append(var)

            if missing_vars:
                validation_result['warnings'].append(f"Variables faltantes: {', '.join(missing_vars)}")

        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(str(e))

        return validation_result


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def get_html_template_service() -> HTMLTemplateService:
    """
    Factory function para obtener una instancia del servicio de templates.

    Returns:
        HTMLTemplateService: Instancia del servicio
    """
    return HTMLTemplateService()


def render_sales_report_html(datos_resumen: Dict[str, Any], template_name: str = "email_report.html") -> str:
    """
    Función de utilidad para renderizar un reporte de ventas en HTML.

    Args:
        datos_resumen: Datos del resumen de ventas
        template_name: Nombre del template a usar

    Returns:
        str: HTML renderizado del reporte
    """
    template_service = get_html_template_service()
    return template_service.render_email_report(datos_resumen, template_name)


def get_available_templates() -> List[str]:
    """
    Obtiene lista de templates disponibles.

    Returns:
        List[str]: Lista de nombres de templates disponibles
    """
    template_service = get_html_template_service()
    return template_service.list_available_templates()


def validate_template(template_name: str) -> Dict[str, Any]:
    """
    Valida un template específico.

    Args:
        template_name: Nombre del template

    Returns:
        Dict[str, Any]: Resultado de la validación
    """
    template_service = get_html_template_service()
    return template_service.validate_template(template_name)


# =============================================================================
# EXPORTACIONES
# =============================================================================

__all__ = [
    'HTMLTemplateService',
    'TemplateError',
    'get_html_template_service',
    'render_sales_report_html',
    'get_available_templates',
    'validate_template'
]
