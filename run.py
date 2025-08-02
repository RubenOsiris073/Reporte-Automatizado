#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA EMPRESARIAL DE ANÁLISIS DE VENTAS
Servidor web para Railway + CLI local con soporte Ollama/Gemini adaptativo
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from flask import Flask, jsonify, request
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agregar el directorio del sistema al path
sys.path.insert(0, str(Path(__file__).parent))

# Importar dotenv para cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv no disponible, usando variables de entorno del sistema")

try:
    from sistema_ventas.main import analisis_empresarial, SistemaVentasMain
    from sistema_ventas.config import settings
    from sistema_ventas.utils import logger as sistema_logger
    from sistema_ventas.core.exceptions import SistemaVentasError
    from ollama_service import AdaptiveAIService
except ImportError as e:
    logger.error(f"ERROR: Error importando módulos del sistema: {e}")
    logger.error("Asegúrese de que todos los módulos estén instalados correctamente.")
    sys.exit(1)

# =============================================================================
# SERVIDOR WEB PARA RAILWAY
# =============================================================================

# Crear la aplicación Flask
app = Flask(__name__)

# Variables globales para el estado del sistema
ultimo_analisis = None
sistema_status = {
    'iniciado': datetime.now().isoformat(),
    'ultimo_analisis': None,
    'total_analisis': 0,
    'ia_disponible': False,
    'ai_method': 'unknown'
}

def inicializar_sistema():
    """Inicializa el sistema y verifica que todo esté funcionando"""
    global sistema_status
    try:
        # Crear instancia del sistema
        sistema = SistemaVentasMain()
        
        # Verificar estado de IA
        ai_status = sistema.ai_service.get_status_info()
        sistema_status.update({
            'ia_disponible': ai_status.get('ai_method') != 'traditional',
            'ai_method': ai_status.get('ai_method', 'unknown')
        })
        
        logger.info(f"Sistema inicializado - IA: {sistema_status['ai_method']}")
        return True
    except Exception as e:
        logger.error(f"Error inicializando sistema: {e}")
        return False

@app.route('/health')
def health_check():
    """Endpoint de salud para Railway healthcheck"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Sistema Análisis Ventas',
        'version': '3.0.0',
        'ai_method': sistema_status.get('ai_method', 'unknown')
    }), 200

@app.route('/')
def home():
    """Página principal con información del sistema"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de Análisis de Ventas</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
            .status {{ padding: 15px; margin: 15px 0; border-radius: 5px; }}
            .status.success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }}
            .status.warning {{ background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }}
            .button {{ background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 5px; }}
            .button:hover {{ background: #2980b9; }}
            .info {{ background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏢 Sistema Empresarial de Análisis de Ventas</h1>
            
            <div class="status {'success' if sistema_status['ia_disponible'] else 'warning'}">
                <strong>Estado del Sistema:</strong> Operativo<br>
                <strong>IA Detectada:</strong> {'✅ ' + sistema_status['ai_method'].upper() if sistema_status['ia_disponible'] else '❌ Solo análisis tradicional'}<br>
                <strong>Iniciado:</strong> {sistema_status['iniciado']}<br>
                <strong>Total Análisis:</strong> {sistema_status['total_analisis']}
            </div>
            
            <div class="info">
                <h3>🤖 Sistema de IA Adaptativo:</h3>
                <p><strong>Prioridad 1:</strong> Ollama (local) - Mejor para desarrollo</p>
                <p><strong>Prioridad 2:</strong> Google Gemini (API) - Fallback confiable</p>
                <p><strong>Prioridad 3:</strong> Análisis tradicional - Siempre funciona</p>
            </div>
            
            <div class="info">
                <h3>📋 Funcionalidades:</h3>
                <ul>
                    <li>🔍 Análisis estadístico avanzado de datos de ventas</li>
                    <li>🤖 IA adaptativa (Ollama → Gemini → Tradicional)</li>
                    <li>📊 Generación de reportes profesionales</li>
                    <li>📧 Envío automático por email</li>
                    <li>🔗 Integración con Google Sheets</li>
                </ul>
            </div>
            
            <div>
                <a href="/status" class="button">📊 Ver Estado Detallado</a>
                <a href="/run-analysis" class="button">🚀 Ejecutar Análisis</a>
                <a href="/health" class="button">❤️ Health Check</a>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/status')
def system_status():
    """Endpoint con estado detallado del sistema"""
    try:
        # Obtener estado actualizado
        sistema = SistemaVentasMain()
        ai_status = sistema.ai_service.get_status_info()
        
        return jsonify({
            'sistema': sistema_status,
            'ia_detalle': ai_status,
            'configuracion': {
                'smtp_configurado': bool(os.getenv('SMTP_HOST')),
                'gemini_configurado': bool(os.getenv('GEMINI_API_KEY')),
                'ollama_url': os.getenv('OLLAMA_URL', 'No configurado'),
                'ollama_disponible': ai_status.get('ollama_available', False),
                'google_sheets_configurado': bool(os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON'))
            },
            'entorno': {
                'railway': bool(os.getenv('RAILWAY_STATIC_URL')),
                'puerto': os.getenv('PORT', '8080'),
                'debug_mode': os.getenv('DEBUG_MODE', 'false')
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/run-analysis', methods=['GET', 'POST'])
def run_analysis():
    """Endpoint para ejecutar análisis"""
    if request.method == 'GET':
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Ejecutar Análisis</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
                .button { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
                .button:hover { background: #2980b9; }
                input[type="text"] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Ejecutar Análisis de Ventas</h1>
                <form method="POST">
                    <label>Nombre de la hoja de Google Sheets:</label>
                    <input type="text" name="sheet_name" value="DB_sales" placeholder="DB_sales">
                    <br><br>
                    <button type="submit" class="button">Ejecutar Análisis Completo</button>
                </form>
                <br>
                <a href="/">← Volver al inicio</a>
            </div>
        </body>
        </html>
        """
        return html
    
    # POST - Ejecutar análisis
    try:
        global ultimo_analisis, sistema_status
        
        sheet_name = request.form.get('sheet_name', 'DB_sales')
        logger.info(f"Iniciando análisis para hoja: {sheet_name}")
        
        # Ejecutar análisis
        resultado = analisis_empresarial(sheet_name)
        
        if resultado:
            ultimo_analisis = resultado
            sistema_status['ultimo_analisis'] = datetime.now().isoformat()
            sistema_status['total_analisis'] += 1
            
            return jsonify({
                'success': True,
                'message': 'Análisis completado exitosamente',
                'resultado': {
                    'analisis_completado': resultado.get('analisis_completado'),
                    'email_enviado': resultado.get('email_enviado'),
                    'archivo_reporte': str(resultado.get('archivo_reporte', '')),
                    'timestamp': resultado.get('timestamp')
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error en el análisis',
                'error': 'El sistema no pudo completar el análisis'
            }), 500
            
    except Exception as e:
        logger.error(f"Error ejecutando análisis: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

# =============================================================================
# INTERFAZ DE LÍNEA DE COMANDOS (CLI)
# =============================================================================

def mostrar_banner():
    """Muestra el banner del sistema."""
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                 SISTEMA EMPRESARIAL DE VENTAS                ║
║                    Análisis Profesional                      ║
╠══════════════════════════════════════════════════════════════╣
║ Versión: 3.0.0              IA Adaptativa: Ollama → Gemini ║
║ Desarrollado con arquitectura modular y Clean Code          ║
╚══════════════════════════════════════════════════════════════╝

🤖 IA ADAPTATIVA - FUNCIONAMIENTO:
   1. 🔍 Detecta Ollama local (http://localhost:11434)
   2. 🌐 Si no está disponible, usa Google Gemini
   3. 📊 Si no hay IA, genera análisis tradicional

📋 FUNCIONALIDADES:
   • Conexión automatizada con Google Sheets
   • Análisis estadístico avanzado de ventas  
   • Generación de reportes profesionales
   • Envío automático por email
   • Análisis estratégico con IA adaptativa
"""
    print(banner)

def mostrar_estado_ia():
    """Muestra el estado actual del sistema de IA"""
    try:
        sistema = SistemaVentasMain()
        ai_status = sistema.ai_service.get_status_info()
        
        print("\n" + "="*60)
        print("ESTADO DEL SISTEMA DE IA ADAPTATIVO")
        print("="*60)
        print(f"Método detectado: {ai_status.get('ai_method', 'unknown').upper()}")
        print(f"Entorno: {ai_status.get('environment', 'unknown')}")
        print()
        print("CONFIGURACIÓN:")
        print(f"  Ollama URL: {os.getenv('OLLAMA_URL', 'No configurado')}")
        print(f"  Ollama disponible: {'✅' if ai_status.get('ollama_available') else '❌'}")
        print(f"  Gemini configurado: {'✅' if ai_status.get('gemini_configured') else '❌'}")
        print()
        print("PRIORIDADES:")
        print("  1. Ollama (local) - Mejor rendimiento")
        print("  2. Gemini (API) - Fallback confiable") 
        print("  3. Tradicional - Siempre funciona")
        print("="*60)
        
    except Exception as e:
        print(f"Error obteniendo estado de IA: {e}")

def main_cli():
    """Función principal para CLI (línea de comandos)"""
    
    parser = argparse.ArgumentParser(
        description="Sistema Empresarial de Análisis de Ventas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run.py                     # Usar hoja por defecto (DB_sales)
  python run.py "MiHojaVentas"      # Usar hoja personalizada
  python run.py --status            # Ver estado del sistema de IA
  python run.py --web               # Iniciar servidor web (Railway)
        """
    )

    parser.add_argument(
        'nombre_hoja',
        nargs='?',
        default='DB_sales',
        help='Nombre de la hoja de Google Sheets (por defecto: DB_sales)'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='Mostrar estado del sistema de IA y salir'
    )

    parser.add_argument(
        '--web',
        action='store_true',
        help='Iniciar servidor web para Railway'
    )

    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='No mostrar banner inicial'
    )

    args = parser.parse_args()

    # Iniciar servidor web si se solicita
    if args.web:
        port = int(os.environ.get('PORT', 8080))
        logger.info("Iniciando servidor web...")
        if inicializar_sistema():
            logger.info("✅ Sistema inicializado correctamente")
        else:
            logger.warning("⚠️ Sistema inicializado con advertencias")
        
        logger.info(f"🚀 Servidor web iniciado en puerto {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
        return

    # Mostrar banner a menos que se solicite lo contrario
    if not args.no_banner:
        mostrar_banner()

    # Solo mostrar estado si se solicita
    if args.status:
        mostrar_estado_ia()
        return 0

    try:
        # Mostrar información de inicio
        print(f"\n🚀 INICIANDO ANÁLISIS DE VENTAS")
        print(f"Hoja de Google Sheets: {args.nombre_hoja}")
        print("-" * 60)

        # Mostrar estado de IA
        mostrar_estado_ia()

        # Ejecutar análisis completo
        logger.info(f"Iniciando análisis desde CLI con hoja: {args.nombre_hoja}")

        resultado = analisis_empresarial(args.nombre_hoja)

        if resultado and resultado.get('analisis_completado'):
            print("\n✅ ¡ANÁLISIS COMPLETADO EXITOSAMENTE!")
            print(f"📄 Reporte: {resultado.get('archivo_reporte', 'N/A')}")
            print(f"📧 Email: {'Enviado' if resultado.get('email_enviado') else 'No enviado'}")

            # Mostrar resumen si hay IA disponible
            if 'resultados' in resultado:
                resumen = resultado['resultados'].get('resumen_principal', {})
                if 'metricas_ventas' in resumen:
                    mv = resumen['metricas_ventas']
                    print(f"💰 Ventas totales: ${mv.get('ventas_totales', 0):,.2f}")
                    print(f"🛒 Transacciones: {mv.get('num_transacciones', 0):,}")

            logger.info("Análisis completado exitosamente desde CLI")
            return 0
        else:
            print("\n❌ El análisis no se completó correctamente")
            logger.error("Análisis no completado desde CLI")
            return 1

    except KeyboardInterrupt:
        print("\n\nEjecución interrumpida por el usuario")
        logger.info("Ejecución interrumpida por el usuario desde CLI")
        return 130

    except SistemaVentasError as e:
        print(f"\n❌ ERROR DEL SISTEMA: {e}")
        logger.error(f"Error del sistema desde CLI: {e}")
        return 1

    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        logger.error(f"Error inesperado desde CLI: {e}", exc_info=True)
        return 1

# =============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    # Detectar si se está ejecutando en Railway
    if os.getenv('RAILWAY_STATIC_URL') or os.getenv('PORT'):
        # Modo Railway - servidor web
        port = int(os.environ.get('PORT', 8080))
        logger.info("🚂 Modo Railway detectado - iniciando servidor web...")
        
        if inicializar_sistema():
            logger.info("✅ Sistema inicializado correctamente")
        else:
            logger.warning("⚠️ Sistema inicializado con advertencias")
        
        logger.info(f"🚀 Servidor web iniciado en puerto {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # Modo CLI local
        try:
            exit_code = main_cli()
            sys.exit(exit_code)
        except Exception as e:
            print(f"\n❌ ERROR CRÍTICO EN EL SISTEMA: {e}")
            sys.exit(1)
