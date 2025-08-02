#!/usr/bin/env python3
"""
Script de Demostración y Testing para Templates HTML de Email
===========================================================

Este script permite probar y validar los templates HTML del sistema de ventas,
generar ejemplos de correos y verificar que todo funciona correctamente.

Usage:
    python test_templates.py                    # Ejecutar todas las pruebas
    python test_templates.py --template compact # Probar template específico
    python test_templates.py --generate         # Solo generar ejemplos
    python test_templates.py --validate         # Solo validar templates

Author: Sistema Empresarial de Ventas
Version: 2.0.0
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Agregar el directorio del sistema al path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from sistema_ventas.services.html_template_service import (
        HTMLTemplateService,
        get_html_template_service,
        render_sales_report_html,
        get_available_templates,
        validate_template
    )
    from sistema_ventas.config import settings
except ImportError as e:
    print(f"❌ Error importando módulos del sistema: {e}")
    print("Asegúrate de ejecutar desde el directorio raíz del proyecto")
    sys.exit(1)


class TemplatesTester:
    """Clase para testing y demostración de templates HTML."""

    def __init__(self):
        """Inicializa el tester."""
        self.template_service = get_html_template_service()
        self.output_dir = Path("ejemplos_templates")
        self.output_dir.mkdir(exist_ok=True)

    def generate_sample_data(self) -> Dict[str, Any]:
        """
        Genera datos de muestra para testing.

        Returns:
            Dict[str, Any]: Datos de muestra completos
        """
        return {
            'metricas_ventas': {
                'ventas_totales': 2847593.50,
                'ticket_promedio': 1247.80,
                'transacciones': 2283,
                'productos_vendidos': 15679,
                'clientes_activos': 892
            },
            'top_productos': {
                'iPhone 15 Pro Max': 523847.20,
                'MacBook Air M3': 445692.15,
                'iPad Pro 12.9': 298475.80,
                'AirPods Pro 2': 187429.35,
                'Apple Watch Ultra 2': 156238.90,
                'Mac Studio M2': 134567.40,
                'HomePod mini': 98765.30
            },
            'analisis_temporal': {
                'mes_actual': 'Enero 2025',
                'crecimiento_mensual': 12.5,
                'tendencia': 'positiva'
            },
            'analisis_ia': {
                'disponible': True,
                'contenido': '''
                📈 ANÁLISIS ESTRATÉGICO AUTOMATIZADO:

                • Las ventas muestran una tendencia positiva del +12.5% respecto al mes anterior
                • Los productos Apple dominan el mercado con un 78% de participación
                • El segmento premium (iPhone Pro, MacBook) genera el 65% de los ingresos
                • Se recomienda aumentar inventario de AirPods Pro por alta demanda
                • Oportunidad: Promocionar accesorios complementarios para incrementar ticket promedio

                🎯 RECOMENDACIONES CLAVE:
                • Enfocar marketing en productos de alto ticket promedio
                • Implementar estrategia de bundling para aumentar venta cruzada
                • Monitorear disponibilidad de productos estrella
                '''
            },
            'kpis_adicionales': {
                'margen_promedio': 23.8,
                'conversion_rate': 4.2,
                'customer_lifetime_value': 3247.50,
                'productos_por_transaccion': 2.4
            },
            'alertas': [
                'Stock bajo en iPhone 15 Pro Max',
                'Incremento del 15% en devoluciones de accesorios',
                'Nueva campaña publicitaria muestra ROI del 340%'
            ]
        }

    def test_all_templates(self) -> Dict[str, Any]:
        """
        Prueba todos los templates disponibles.

        Returns:
            Dict[str, Any]: Resultados de las pruebas
        """
        print("🧪 Iniciando pruebas de templates HTML...")
        print("=" * 60)

        results = {
            'templates_tested': 0,
            'successful': 0,
            'failed': 0,
            'results': {},
            'errors': []
        }

        # Obtener datos de muestra
        sample_data = self.generate_sample_data()

        # Obtener templates disponibles
        available_templates = get_available_templates()

        if not available_templates:
            print("❌ No se encontraron templates disponibles")
            return results

        print(f"📁 Templates encontrados: {len(available_templates)}")
        for template in available_templates:
            print(f"   • {template}")
        print()

        # Probar cada template
        for template_name in available_templates:
            print(f"🔍 Probando template: {template_name}")
            results['templates_tested'] += 1

            try:
                # Renderizar template
                html_content = render_sales_report_html(sample_data, template_name)

                # Guardar ejemplo
                output_file = self.output_dir / f"ejemplo_{template_name}"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)

                # Estadísticas del archivo generado
                file_size = len(html_content.encode('utf-8')) / 1024  # KB

                results['successful'] += 1
                results['results'][template_name] = {
                    'status': 'success',
                    'file_size_kb': round(file_size, 2),
                    'output_file': str(output_file),
                    'character_count': len(html_content)
                }

                print(f"   ✅ Éxito - {file_size:.1f} KB - {len(html_content):,} caracteres")

            except Exception as e:
                results['failed'] += 1
                results['results'][template_name] = {
                    'status': 'failed',
                    'error': str(e)
                }
                results['errors'].append(f"{template_name}: {str(e)}")
                print(f"   ❌ Error: {str(e)}")

        print("\n" + "=" * 60)
        print(f"📊 Resumen de pruebas:")
        print(f"   • Templates probados: {results['templates_tested']}")
        print(f"   • Exitosos: {results['successful']}")
        print(f"   • Fallidos: {results['failed']}")
        print(f"   • Ejemplos generados en: {self.output_dir}")

        return results

    def validate_all_templates(self) -> Dict[str, Any]:
        """
        Valida todos los templates disponibles.

        Returns:
            Dict[str, Any]: Resultados de validación
        """
        print("🔍 Validando templates HTML...")
        print("=" * 40)

        validation_results = {
            'total_templates': 0,
            'valid_templates': 0,
            'templates_with_warnings': 0,
            'invalid_templates': 0,
            'details': {}
        }

        available_templates = get_available_templates()
        validation_results['total_templates'] = len(available_templates)

        for template_name in available_templates:
            print(f"\n📄 Validando: {template_name}")

            try:
                validation = validate_template(template_name)
                validation_results['details'][template_name] = validation

                if validation['is_valid']:
                    if validation['warnings']:
                        validation_results['templates_with_warnings'] += 1
                        print(f"   ⚠️  Válido con advertencias ({validation['size_kb']} KB)")
                        for warning in validation['warnings']:
                            print(f"      • {warning}")
                    else:
                        validation_results['valid_templates'] += 1
                        print(f"   ✅ Válido ({validation['size_kb']} KB)")
                else:
                    validation_results['invalid_templates'] += 1
                    print(f"   ❌ Inválido")
                    for error in validation['errors']:
                        print(f"      • {error}")

            except Exception as e:
                validation_results['invalid_templates'] += 1
                validation_results['details'][template_name] = {
                    'is_valid': False,
                    'errors': [str(e)]
                }
                print(f"   ❌ Error de validación: {str(e)}")

        print("\n" + "=" * 40)
        print("📋 Resumen de validación:")
        print(f"   • Total templates: {validation_results['total_templates']}")
        print(f"   • Válidos: {validation_results['valid_templates']}")
        print(f"   • Con advertencias: {validation_results['templates_with_warnings']}")
        print(f"   • Inválidos: {validation_results['invalid_templates']}")

        return validation_results

    def test_specific_template(self, template_name: str) -> bool:
        """
        Prueba un template específico.

        Args:
            template_name: Nombre del template

        Returns:
            bool: True si la prueba fue exitosa
        """
        print(f"🎯 Probando template específico: {template_name}")
        print("=" * 50)

        try:
            # Generar datos de muestra
            sample_data = self.generate_sample_data()

            # Renderizar template
            html_content = render_sales_report_html(sample_data, template_name)

            # Guardar ejemplo
            output_file = self.output_dir / f"test_{template_name}"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            # Estadísticas
            file_size = len(html_content.encode('utf-8')) / 1024

            print(f"✅ Template renderizado exitosamente")
            print(f"📁 Archivo: {output_file}")
            print(f"📏 Tamaño: {file_size:.2f} KB")
            print(f"📝 Caracteres: {len(html_content):,}")

            # Validar template
            print(f"\n🔍 Validando template...")
            validation = validate_template(template_name)

            if validation['is_valid']:
                print(f"✅ Template válido")
                if validation['warnings']:
                    print(f"⚠️  Advertencias:")
                    for warning in validation['warnings']:
                        print(f"   • {warning}")
            else:
                print(f"❌ Template inválido:")
                for error in validation['errors']:
                    print(f"   • {error}")

            return True

        except Exception as e:
            print(f"❌ Error probando template: {str(e)}")
            return False

    def generate_demo_email(self, template_name: str = "email_report.html") -> str:
        """
        Genera un email de demostración completo.

        Args:
            template_name: Template a usar

        Returns:
            str: Ruta del archivo generado
        """
        print(f"📧 Generando email de demostración con template: {template_name}")

        # Datos de demostración más realistas
        demo_data = {
            'metricas_ventas': {
                'ventas_totales': 1847293.75,
                'ticket_promedio': 892.50,
                'transacciones': 2069,
                'productos_vendidos': 8847,
                'clientes_activos': 567
            },
            'top_productos': {
                'Laptop Gaming ASUS ROG': 384729.20,
                'Monitor 4K Samsung 32"': 267849.85,
                'Teclado Mecánico Corsair': 189456.30,
                'Mouse Logitech MX Master': 154782.40,
                'Webcam HD Logitech C920': 98567.15
            },
            'analisis_temporal': {
                'periodo': 'Diciembre 2024',
                'crecimiento_mensual': 8.7,
                'tendencia': 'estable'
            },
            'analisis_ia': {
                'disponible': True,
                'contenido': '''
                🤖 ANÁLISIS INTELIGENTE DE VENTAS:

                • Temporada navideña impulsó ventas un +23% sobre el promedio anual
                • Productos gaming lideran con 42% de participación en ingresos
                • Incremento notable en accesorios premium (+31% vs mes anterior)
                • Patrón de compra: Los clientes prefieren bundles completos

                📊 MÉTRICAS CLAVE:
                • ROI de marketing digital: +187%
                • Satisfacción del cliente: 94.2%
                • Tiempo promedio de entrega: 2.1 días
                • Tasa de recompra: 68%

                🚀 RECOMENDACIONES ESTRATÉGICAS:
                • Ampliar línea de productos gaming profesionales
                • Desarrollar programa de fidelización para clientes recurrentes
                • Optimizar inventario para Q1 2025 basado en tendencias actuales
                '''
            }
        }

        try:
            # Renderizar template
            html_content = render_sales_report_html(demo_data, template_name)

            # Crear nombre de archivo único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            demo_file = self.output_dir / f"demo_email_{timestamp}.html"

            # Guardar archivo
            with open(demo_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f"✅ Email de demostración generado: {demo_file}")
            print(f"📁 Abre el archivo en tu navegador para visualizar el resultado")

            return str(demo_file)

        except Exception as e:
            print(f"❌ Error generando email de demostración: {str(e)}")
            raise

    def show_templates_info(self):
        """Muestra información detallada sobre los templates."""
        print("📋 Información de Templates HTML")
        print("=" * 50)

        available_templates = get_available_templates()

        if not available_templates:
            print("❌ No se encontraron templates")
            return

        print(f"📁 Directorio de templates: {self.template_service.templates_dir}")
        print(f"🔢 Total de templates: {len(available_templates)}")
        print()

        for i, template in enumerate(available_templates, 1):
            print(f"{i}. {template}")

            # Información adicional del template
            try:
                template_path = self.template_service.templates_dir / template
                if template_path.exists():
                    stat = template_path.stat()
                    size_kb = stat.st_size / 1024
                    modified_time = datetime.fromtimestamp(stat.st_mtime)

                    print(f"   📏 Tamaño: {size_kb:.1f} KB")
                    print(f"   📅 Modificado: {modified_time.strftime('%Y-%m-%d %H:%M')}")

                    # Descripción basada en el nombre
                    descriptions = {
                        'email_report.html': 'Template principal completo con diseño profesional',
                        'email_report_simple.html': 'Template simplificado, compatible con más clientes',
                        'email_report_compact.html': 'Template compacto para reportes rápidos'
                    }

                    if template in descriptions:
                        print(f"   📝 Descripción: {descriptions[template]}")

            except Exception:
                pass

            print()


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Script de testing y demostración para templates HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python test_templates.py                     # Ejecutar todas las pruebas
  python test_templates.py --info              # Mostrar información de templates
  python test_templates.py --validate          # Solo validar templates
  python test_templates.py --generate          # Generar ejemplos de todos los templates
  python test_templates.py --template compact  # Probar template específico
  python test_templates.py --demo             # Generar email de demostración
        """
    )

    parser.add_argument('--template', '-t',
                       help='Probar template específico')
    parser.add_argument('--validate', '-v', action='store_true',
                       help='Solo validar templates')
    parser.add_argument('--generate', '-g', action='store_true',
                       help='Solo generar ejemplos')
    parser.add_argument('--demo', '-d', action='store_true',
                       help='Generar email de demostración')
    parser.add_argument('--info', '-i', action='store_true',
                       help='Mostrar información de templates')

    args = parser.parse_args()

    # Crear instancia del tester
    tester = TemplatesTester()

    print("🎨 Sistema de Testing de Templates HTML")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        if args.info:
            tester.show_templates_info()

        elif args.validate:
            tester.validate_all_templates()

        elif args.generate:
            tester.test_all_templates()

        elif args.demo:
            template_name = args.template if args.template else "email_report.html"
            if not template_name.endswith('.html'):
                template_name += '.html'
            tester.generate_demo_email(template_name)

        elif args.template:
            template_name = args.template
            if not template_name.endswith('.html'):
                template_name += '.html'
            tester.test_specific_template(template_name)

        else:
            # Ejecutar suite completa
            print("🚀 Ejecutando suite completa de pruebas...\n")

            # Mostrar información
            tester.show_templates_info()
            print()

            # Validar templates
            tester.validate_all_templates()
            print()

            # Probar todos los templates
            tester.test_all_templates()
            print()

            # Generar demo
            print("📧 Generando email de demostración...")
            tester.generate_demo_email()

        print(f"\n✅ Proceso completado exitosamente")
        print(f"📁 Revisa los archivos generados en: {tester.output_dir}")

    except KeyboardInterrupt:
        print(f"\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
