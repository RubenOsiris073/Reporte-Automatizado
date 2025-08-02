#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA EMPRESARIAL DE ANÁLISIS DE VENTAS
Análisis profesional de rendimiento comercial con soporte para Railway
"""

import subprocess
import time
import os
import requests
import json
import pandas as pd
import numpy as np
import psutil
from dotenv import load_dotenv
import logging
import smtplib
import io
import gspread
from datetime import datetime, timedelta
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from google.oauth2.service_account import Credentials
from credentials_manager import CredentialsManager
from ollama_service import AdaptiveAIService

# Cargar variables de entorno
load_dotenv()

# Configuración única de SMTP
SMTP_CONFIG = {
    'server': os.getenv('SMTP_SERVER', 'smtp-relay.brevo.com'),
    'port': int(os.getenv('SMTP_PORT', '587')),
    'user': os.getenv('SMTP_USER', ''),
    'password': os.getenv('SMTP_PASSWORD', ''),
    'from_email': os.getenv('FROM_EMAIL', ''),
    'from_name': os.getenv('FROM_NAME', 'comunicacion'),
    'to_email': os.getenv('TO_EMAIL', '')
}

class EmailManager:
    """Gestor de emails con Brevo SMTP"""

    def __init__(self):
        self.config = SMTP_CONFIG

    def enviar_reporte_automatico(self, datos_resumen, archivo_reporte):
        try:
            print(f"Enviando reporte a: {self.config['to_email']}")

            server = smtplib.SMTP(self.config['server'], self.config['port'])
            server.starttls()
            server.login(self.config['user'], self.config['password'])

            msg = MIMEMultipart()
            msg['From'] = f"{self.config['from_name']} <{self.config['from_email']}>"
            msg['To'] = self.config['to_email']
            msg['Subject'] = f"Reporte Empresarial - {datetime.now().strftime('%d/%m/%Y')}"

            contenido = f"""
REPORTE EMPRESARIAL AUTOMÁTICO
=============================
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

MÉTRICAS:
• Ventas: ${datos_resumen.get('ventas_totales', 0):,.2f} MXN
• Ticket Promedio: ${datos_resumen.get('ticket_promedio', 0):,.2f} MXN
• Transacciones: {datos_resumen.get('transacciones', 0):,}

TOP PRODUCTOS:"""

            for i, (producto, venta) in enumerate(list(datos_resumen.get('top_productos', {}).items())[:5], 1):
                contenido += f"\n{i}. {producto}: ${venta:,.2f} MXN"

            msg.attach(MIMEText(contenido, 'plain', 'utf-8'))

            if archivo_reporte and os.path.exists(archivo_reporte):
                with open(archivo_reporte, 'rb') as f:
                    adjunto = MIMEApplication(f.read())
                    adjunto.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(archivo_reporte)}"')
                    msg.attach(adjunto)

            server.send_message(msg)
            server.quit()

            print("Email enviado exitosamente!")
            return True

        except Exception as e:
            print(f"Error enviando email: {e}")
            return False

    def enviar_reporte_multiple(self, datos_resumen, archivo_reporte, destinatarios):
        """Enviar reporte a múltiples destinatarios"""
        try:
            print(f"Enviando reporte a: {', '.join(destinatarios)}")

            server = smtplib.SMTP(self.config['server'], self.config['port'])
            server.starttls()
            server.login(self.config['user'], self.config['password'])

            for destinatario in destinatarios:
                msg = MIMEMultipart()
                msg['From'] = f"{self.config['from_name']} <{self.config['from_email']}>"
                msg['To'] = destinatario
                msg['Subject'] = f"Reporte Empresarial - {datetime.now().strftime('%d/%m/%Y')}"

                contenido = f"""
REPORTE EMPRESARIAL AUTOMÁTICO
=============================
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

MÉTRICAS:
• Ventas: ${datos_resumen.get('ventas_totales', 0):,.2f} MXN
• Ticket Promedio: ${datos_resumen.get('ticket_promedio', 0):,.2f} MXN
• Transacciones: {datos_resumen.get('transacciones', 0):,}

TOP PRODUCTOS:"""

                for i, (producto, venta) in enumerate(list(datos_resumen.get('top_productos', {}).items())[:5], 1):
                    contenido += f"\n{i}. {producto}: ${venta:,.2f} MXN"

                msg.attach(MIMEText(contenido, 'plain', 'utf-8'))

                if archivo_reporte and os.path.exists(archivo_reporte):
                    with open(archivo_reporte, 'rb') as f:
                        adjunto = MIMEApplication(f.read())
                        adjunto.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(archivo_reporte)}"')
                        msg.attach(adjunto)

                server.send_message(msg)
                print(f"Email enviado a: {destinatario}")

            server.quit()
            print("Todos los emails enviados exitosamente!")
            return True

        except Exception as e:
            print(f"Error enviando emails: {e}")
            return False


class SheetsManager:
    """Gestor para conexión con base de datos Google Sheets"""

    def __init__(self):
        self.gc = None
        self.sheet = None
        self.df = None
        self.temp_credentials_file = None

    def conectar_sheets(self, nombre_hoja):
        """Establecer conexión con la base de datos"""

        try:
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            # Usar el nuevo sistema de credenciales
            credentials_path = CredentialsManager.get_credentials_path()
            self.temp_credentials_file = credentials_path

            creds = Credentials.from_service_account_file(
                credentials_path,
                scopes=scope
            )

            self.gc = gspread.authorize(creds)
            self.sheet = self.gc.open(nombre_hoja).sheet1
            return True

        except Exception as e:
            logging.error(f"Error conectando a Google Sheets: {e}")
            return False
    
    def __del__(self):
        """Limpieza automática del archivo temporal"""
        if hasattr(self, 'temp_credentials_file'):
            CredentialsManager.cleanup_temp_file(self.temp_credentials_file)

    def cargar_datos(self):
        """Cargar datos desde la base de datos"""
        if not self.sheet:
            return False

        try:
            datos_raw = self.sheet.get_all_records()
            self.df = pd.DataFrame(datos_raw)
            return True

        except Exception:
            return False

    def procesar_datos(self):
        """Procesar y limpiar datos empresariales"""
        if self.df is None:
            return False

        try:
            # Convertir fechas
            if 'venta_timestamp' in self.df.columns:
                self.df['venta_timestamp'] = pd.to_datetime(self.df['venta_timestamp'], errors='coerce')
                self.df['mes_venta'] = self.df['venta_timestamp'].dt.to_period('M')
                self.df['semana_venta'] = self.df['venta_timestamp'].dt.to_period('W')

            if 'fechaCaducidad' in self.df.columns:
                self.df['fechaCaducidad'] = pd.to_datetime(self.df['fechaCaducidad'], errors='coerce')

            # Convertir números
            columnas_numericas = ['venta_total', 'precio', 'cantidad', 'diasParaCaducar']
            for col in columnas_numericas:
                if col in self.df.columns:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

            # Calcular métricas derivadas
            if all(col in self.df.columns for col in ['venta_total', 'precio', 'cantidad']):
                self.df['margen'] = self.df['venta_total'] - (self.df['precio'] * self.df['cantidad'])

            # Categorizar urgencia de inventario
            if 'diasParaCaducar' in self.df.columns:
                self.df['urgencia_inventario'] = pd.cut(
                    self.df['diasParaCaducar'],
                    bins=[-np.inf, 7, 30, 90, np.inf],
                    labels=['Crítico', 'Urgente', 'Medio', 'Normal']
                )

            return True

        except Exception:
            return False


class DataAnalyzer:
    """Analizador de datos empresariales"""

    def __init__(self, df):
        self.df = df
        self.resumen = {}

    def generar_resumen(self):
        """Generar análisis estadístico empresarial"""

        try:
            # Información básica
            self.resumen['info_basica'] = {
                'total_filas': len(self.df),
                'columnas': list(self.df.columns),
                'fecha_analisis': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Período de datos
            if 'venta_timestamp' in self.df.columns:
                fecha_min = self.df['venta_timestamp'].min()
                fecha_max = self.df['venta_timestamp'].max()
                self.resumen['info_basica']['periodo'] = f"Del {fecha_min} al {fecha_max}"

            # Métricas de rendimiento
            if 'venta_total' in self.df.columns:
                venta_total = self.df['venta_total'].sum()
                ticket_promedio = self.df['venta_total'].mean()
                num_transacciones = len(self.df[self.df['venta_total'] > 0])

                self.resumen['metricas_ventas'] = {
                    'ventas_totales': float(venta_total),
                    'ticket_promedio': float(ticket_promedio),
                    'num_transacciones': int(num_transacciones)
                }

            # Top productos
            if 'nombre' in self.df.columns and 'venta_total' in self.df.columns:
                top_productos = self.df.groupby('nombre')['venta_total'].sum().nlargest(10)
                self.resumen['top_productos'] = top_productos.to_dict()

            # Análisis por categoría
            if 'categoria' in self.df.columns:
                if 'venta_total' in self.df.columns:
                    cat_ventas = self.df.groupby('categoria')['venta_total'].sum()
                else:
                    cat_ventas = self.df['categoria'].value_counts()
                self.resumen['por_categoria'] = cat_ventas.to_dict()

            # Alertas de inventario
            if 'diasParaCaducar' in self.df.columns:
                criticos = self.df[self.df['diasParaCaducar'] <= 7]
                self.resumen['alertas_inventario'] = {
                    'cantidad': len(criticos),
                    'productos': criticos['nombre'].tolist()[:10] if 'nombre' in criticos.columns else []
                }

            # Análisis temporal
            if 'mes_venta' in self.df.columns and 'venta_total' in self.df.columns:
                ventas_mensuales = self.df.groupby('mes_venta')['venta_total'].sum().tail(6)
                self.resumen['tendencias'] = {
                    'ventas_mensuales': ventas_mensuales.to_dict(),
                    'mejor_mes': str(ventas_mensuales.idxmax()),
                    'peor_mes': str(ventas_mensuales.idxmin())
                }

            # NUEVO: Análisis con IA
            self._generar_analisis_ia()

            return True

        except Exception:
            return False

    def mostrar_resumen(self):
        """Mostrar resumen estadístico profesional"""
        print("\n" + "="*60)
        print("ANÁLISIS ESTADÍSTICO EMPRESARIAL")
        print("="*60)

        # Información básica
        info = self.resumen.get('info_basica', {})
        print(f"Registros procesados: {info.get('total_filas', 0):,}")
        print(f"Fecha de análisis: {info.get('fecha_analisis', 'N/A')}")
        if 'periodo' in info:
            print(f"Período analizado: {info['periodo']}")

        # Métricas de rendimiento
        if 'metricas_ventas' in self.resumen:
            mv = self.resumen['metricas_ventas']
            print(f"\nMÉTRICAS DE RENDIMIENTO:")
            print(f"   Volumen total de ventas: ${mv['ventas_totales']:,.2f}")
            print(f"   Ticket promedio: ${mv['ticket_promedio']:,.2f}")
            print(f"   Número de transacciones: {mv['num_transacciones']:,}")

        # Top productos
        if 'top_productos' in self.resumen:
            print(f"\nTOP 5 PRODUCTOS POR VOLUMEN:")
            for i, (producto, venta) in enumerate(list(self.resumen['top_productos'].items())[:5], 1):
                print(f"   {i}. {producto}: ${venta:,.2f}")

        # Análisis por categoría
        if 'por_categoria' in self.resumen:
            print(f"\nRENDIMIENTO POR CATEGORÍA:")
            for i, (categoria, valor) in enumerate(list(self.resumen['por_categoria'].items())[:5], 1):
                print(f"   {i}. {categoria}: ${valor:,.2f}")

        # Alertas de inventario
        if 'alertas_inventario' in self.resumen:
            ai = self.resumen['alertas_inventario']
            print(f"\nALERTAS DE INVENTARIO: {ai['cantidad']} productos")
            if ai['productos']:
                print("   Productos con fechas de vencimiento próximas:")
                for producto in ai['productos'][:3]:
                    print(f"   - {producto}")

        # Tendencias
        if 'tendencias' in self.resumen:
            t = self.resumen['tendencias']
            print(f"\nANÁLISIS TEMPORAL:")
            print(f"   Mejor período: {t.get('mejor_mes', 'N/A')}")
            print(f"   Menor rendimiento: {t.get('peor_mes', 'N/A')}")

        # Mostrar análisis IA si está disponible
        if 'analisis_ia' in self.resumen:
            ai_data = self.resumen['analisis_ia']
            print(f"\n🤖 ANÁLISIS CON IA:")
            print(f"   Método: {ai_data.get('ai_method', 'N/A')}")
            print(f"   Estado: {ai_data.get('status', 'N/A')}")
            if ai_data.get('ai_available', False):
                print(f"   Modelo: {ai_data.get('model_used', 'N/A')}")
                print("\n" + ai_data.get('analysis', ''))
            else:
                print("\n" + ai_data.get('analysis', ''))

    def _generar_analisis_ia(self):
        """Genera análisis con IA usando el servicio adaptativo"""
        try:
            # Preparar datos para IA
            datos_para_ia = {}
            
            if 'metricas_ventas' in self.resumen:
                mv = self.resumen['metricas_ventas']
                datos_para_ia.update({
                    'ventas_totales': mv.get('ventas_totales', 0),
                    'total_transacciones': mv.get('num_transacciones', 0),
                    'ticket_promedio': mv.get('ticket_promedio', 0)
                })
            
            if 'info_basica' in self.resumen:
                periodo = self.resumen['info_basica'].get('periodo', 'Período actual')
                datos_para_ia['periodo'] = periodo
            
            if 'top_productos' in self.resumen:
                # Convertir dict a lista de productos
                top_dict = self.resumen['top_productos']
                productos_lista = []
                for nombre, ventas in list(top_dict.items())[:5]:
                    productos_lista.append({
                        'nombre': nombre,
                        'ventas': ventas
                    })
                datos_para_ia['top_productos'] = productos_lista
            
            # Inicializar servicio IA
            ai_service = AdaptiveAIService()
            
            # Generar análisis
            resultado_ia = ai_service.generar_analisis_ia(datos_para_ia)
            
            # Guardar resultado en resumen
            self.resumen['analisis_ia'] = resultado_ia
            
            # Log del estado
            print(f"IA: {resultado_ia.get('ai_method', 'unknown')} - {resultado_ia.get('status', 'unknown')}")
            
        except Exception as e:
            # Fallback en caso de error
            self.resumen['analisis_ia'] = {
                'ai_method': 'error',
                'status': 'failed',
                'ai_available': False,
                'analysis': f"Error en análisis IA: {str(e)}",
                'error': str(e)
            }
            print(f"Error en análisis IA: {e}")


def analisis_empresarial(nombre_hoja="DB_sales"):
    """Función principal para análisis empresarial"""
    print("SISTEMA EMPRESARIAL DE ANÁLISIS DE VENTAS")
    print("=" * 50)

    # Conectar a base de datos
    print("Conectando a base de datos empresarial...")
    sheets = SheetsManager()

    if not sheets.conectar_sheets(nombre_hoja):
        print("ERROR: No se pudo establecer conexión")
        print("Verificar credenciales y permisos de acceso")
        return None

    # Cargar y procesar datos
    if not sheets.cargar_datos():
        print("ERROR: Fallo en carga de datos")
        return None

    if not sheets.procesar_datos():
        print("ERROR: Fallo en procesamiento")
        return None

    # Check if sheets.df is not None before using len()
    if sheets.df is not None:
        print(f"Datos cargados: {len(sheets.df):,} registros")
    else:
        print("ERROR: No hay datos cargados")
        return None

    # Análisis estadístico
    print("\nGenerando análisis estadístico...")
    analyzer = DataAnalyzer(sheets.df)

    if not analyzer.generar_resumen():
        print("ERROR: Fallo en generación de análisis")
        return None

    # Mostrar resumen
    analyzer.mostrar_resumen()

    # Análisis con IA
    print("\nANÁLISIS ESTRATÉGICO CON IA")
    print("=" * 40)

    try:
        # Preparar datos
        datos_ia = {
            'ventas_totales': analyzer.resumen['metricas_ventas']['ventas_totales'],
            'ticket_promedio': analyzer.resumen['metricas_ventas']['ticket_promedio'],
            'transacciones': analyzer.resumen['metricas_ventas']['num_transacciones'],
            'top_productos': dict(list(analyzer.resumen['top_productos'].items())[:3])
        }

        prompt = f"""Analiza estos datos empresariales de una empresa mexicana (moneda: pesos mexicanos MXN):

MÉTRICAS COMERCIALES:
{json.dumps(datos_ia, indent=2, ensure_ascii=False)}

Proporciona análisis estratégico en formato:
RESUMEN EJECUTIVO: [evaluación del rendimiento general]
FORTALEZAS: [ventajas competitivas identificadas]
OPORTUNIDADES: [áreas de crecimiento potencial]
RECOMENDACIONES: [estrategias específicas a implementar]
PROYECCIÓN: [estimación de rendimiento futuro]

Utiliza enfoque empresarial y terminología profesional."""

        print("Procesando análisis estratégico...")

        response = requests.post(
            'http://127.0.0.1:11434/api/generate',
            json={
                'model': 'qwen2.5:3b',
                'prompt': prompt,
                'stream': False,
                'options': {
                    'num_ctx': 2048,
                    'temperature': 0.1,
                    'num_predict': 500
                }
            },
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            analisis_ia = result.get('response', '').strip()

            print("\nRESULTADOS DEL ANÁLISIS ESTRATÉGICO:")
            print("=" * 50)
            print(analisis_ia)
            print("=" * 50)

            # Generar reporte
            archivo_reporte = 'reporte_empresarial.txt'
            with open(archivo_reporte, 'w', encoding='utf-8') as f:
                f.write(f"REPORTE EMPRESARIAL DE ANÁLISIS DE VENTAS\n")
                f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")

                f.write("RESUMEN EJECUTIVO\n")
                f.write("-" * 20 + "\n")
                if sheets.df is not None:
                    f.write(f"Registros: {len(sheets.df):,}\n")
                f.write(f"Volumen de ventas: ${datos_ia['ventas_totales']:,.2f}\n")
                f.write(f"Ticket promedio: ${datos_ia['ticket_promedio']:,.2f}\n")
                f.write(f"Transacciones: {datos_ia['transacciones']:,}\n\n")

                f.write("ANÁLISIS ESTRATÉGICO\n")
                f.write("-" * 25 + "\n")
                f.write(analisis_ia)
                f.write("\n\nPRODUCTOS DE MAYOR RENDIMIENTO\n")
                f.write("-" * 40 + "\n")
                for i, (prod, venta) in enumerate(analyzer.resumen['top_productos'].items(), 1):
                    f.write(f"{i:2d}. {prod}: ${venta:,.2f}\n")

            print(f"\nReporte generado: {archivo_reporte}")

            # ENVÍO AUTOMÁTICO POR EMAIL
            print("\nEnviando reporte por email...")
            email_manager = EmailManager()
            email_enviado = email_manager.enviar_reporte_automatico(datos_ia, archivo_reporte)

            # Resumen de envío
            print("\n" + "="*50)
            print("RESUMEN DE ENVÍO:")
            print(f"📧 Email: {'✅ Enviado exitosamente' if email_enviado else '❌ Error en envío'}")
            print("="*50)

            print("ANÁLISIS EMPRESARIAL COMPLETADO")
            return analyzer

        else:
            print(f"Error en sistema de IA: HTTP {response.status_code}")
            print("Análisis estadístico completado")
            return analyzer

    except Exception as e:
        print(f"Error en análisis estratégico: {e}")
        print("Análisis estadístico completado")
        return analyzer


if __name__ == "__main__":
    print("SISTEMA DE ANÁLISIS EMPRESARIAL v3.0")
    print("� Email automático integrado")
    print(f"📧 Reportes enviados desde: {SMTP_CONFIG['from_email']}")
    print()

    resultado = analisis_empresarial("DB_sales")

    if resultado:
        print("\nCOMPLETADO EXITOSAMENTE")
        print("Análisis realizado")
        print("Email enviado automáticamente")
    else:
        print("\nERROR EN PROCESAMIENTO")
