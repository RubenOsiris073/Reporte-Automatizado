#!/usr/bin/env python3
"""
Servicio de IA adaptativo para Railway
Funciona con Ollama local/remoto o APIs externas como fallback
"""

import requests
import json
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

class AdaptiveAIService:
    """Servicio de IA que se adapta al entorno de deployment"""
    
    def __init__(self):
        # Configuración flexible
        self.ollama_url = os.getenv('OLLAMA_URL', '')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'qwen2.5:latest')
        
        # API de respaldo - solo Gemini
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', '')
        
        # Configuración
        self.environment = os.getenv('ENVIRONMENT', 'local')
        self.timeout = 30
        self.logger = logging.getLogger(__name__)
        
        # Determinar método de IA disponible
        self.ai_method = self._detectar_metodo_ia()
        
    def _detectar_metodo_ia(self) -> str:
        """Detecta qué método de IA está disponible: Ollama o Gemini"""
        
        # 1. Verificar Ollama (local o remoto) - PRIORIDAD
        if self.ollama_url and self._verificar_ollama():
            self.logger.info(f"Usando Ollama: {self.ollama_url}")
            return 'ollama'
        
        # 2. Si Ollama no está disponible, usar Gemini
        if self.gemini_api_key:
            self.logger.info("Ollama no disponible, usando Google Gemini API")
            return 'gemini'
        
        # 3. Fallback a análisis tradicional
        self.logger.warning("Ni Ollama ni Gemini disponibles, usando análisis tradicional")
        return 'traditional'
    
    def _verificar_ollama(self) -> bool:
        """Verifica si Ollama está disponible"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def generar_analisis_ia(self, datos_ventas: Dict[str, Any]) -> Dict[str, Any]:
        """Genera análisis usando Ollama o Gemini como respaldo"""
        
        resultado_base = {
            'timestamp': datetime.now().isoformat(),
            'ai_method': self.ai_method,
            'environment': self.environment,
            'status': 'processing'
        }
        
        if self.ai_method == 'ollama':
            return self._analisis_ollama(datos_ventas, resultado_base)
        elif self.ai_method == 'gemini':
            return self._analisis_gemini(datos_ventas, resultado_base)
        else:
            return self._analisis_tradicional(datos_ventas, resultado_base)
    
    def _analisis_ollama(self, datos: Dict, base: Dict) -> Dict:
        """Análisis con Ollama"""
        try:
            prompt = self._generar_prompt(datos)
            
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 800}
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                resultado = response.json()
                base.update({
                    'status': 'success',
                    'ai_available': True,
                    'analysis': resultado.get('response', ''),
                    'model_used': self.ollama_model
                })
            else:
                raise Exception(f"Error HTTP {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error Ollama: {e}")
            base.update({
                'status': 'error',
                'ai_available': False,
                'analysis': self._generar_insights_basicos(datos),
                'error': str(e)
            })
        
        return base
    
    def _analisis_gemini(self, datos: Dict, base: Dict) -> Dict:
        """Análisis con Google Gemini (GRATIS y generoso)"""
        try:
            prompt = self._generar_prompt(datos)
            
            # URL de la API de Gemini - MODELO ACTUALIZADO
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"Eres un analista empresarial experto. {prompt}"
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 800
                }
            }
            
            response = requests.post(
                url,
                json=payload,
                timeout=20  # Reducir timeout para fallar más rápido
            )
            
            if response.status_code == 200:
                resultado = response.json()
                
                if 'candidates' in resultado and len(resultado['candidates']) > 0:
                    content = resultado['candidates'][0]['content']['parts'][0]['text']
                    
                    base.update({
                        'status': 'success',
                        'ai_available': True,
                        'analysis': content,
                        'model_used': 'gemini-1.5-flash'
                    })
                else:
                    raise Exception("No se recibió respuesta válida de Gemini")
            else:
                raise Exception(f"Error Gemini HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            self.logger.error("Timeout conectando con Gemini API")
            base.update({
                'status': 'error',
                'ai_available': False,
                'analysis': self._generar_insights_basicos(datos),
                'error': 'Gemini API timeout - usando análisis tradicional'
            })
        except requests.exceptions.ConnectionError:
            self.logger.error("Error de conexión con Gemini API")
            base.update({
                'status': 'error',
                'ai_available': False,
                'analysis': self._generar_insights_basicos(datos),
                'error': 'Gemini API unavailable - usando análisis tradicional'
            })
        except Exception as e:
            self.logger.error(f"Error Gemini: {e}")
            base.update({
                'status': 'error',
                'ai_available': False,
                'analysis': self._generar_insights_basicos(datos),
                'error': f'Gemini error: {str(e)} - usando análisis tradicional'
            })
        
        return base
    
    def _analisis_tradicional(self, datos: Dict, base: Dict) -> Dict:
        """Análisis tradicional sin IA"""
        base.update({
            'status': 'success',
            'ai_available': False,
            'analysis': self._generar_insights_basicos(datos),
            'model_used': 'traditional_analysis'
        })
        return base
    
    def _generar_prompt(self, data: Dict[str, Any]) -> str:
        """Genera prompt optimizado para análisis empresarial"""
        
        return f"""
Analiza estos datos de ventas empresariales y genera insights profesionales:

MÉTRICAS CLAVE:
- Ventas Totales: ${data.get('ventas_totales', 0):,.2f}
- Transacciones: {data.get('total_transacciones', 0)}
- Ticket Promedio: ${data.get('ticket_promedio', 0):,.2f}
- Período: {data.get('periodo', 'Último período')}

TOP PRODUCTOS:
{self._formatear_productos_prompt(data.get('top_productos', []))}

Proporciona:
1. 🔍 INSIGHTS CLAVE (3-4 puntos)
2. 💡 OPORTUNIDADES detectadas
3. 📈 RECOMENDACIONES específicas
4. 🎯 PRÓXIMOS PASOS sugeridos

Máximo 600 palabras, tono profesional, en español.
"""
    
    def _formatear_productos_prompt(self, productos: List[Dict]) -> str:
        """Formatea productos para el prompt"""
        if not productos:
            return "No hay datos de productos"
        
        resultado = []
        for i, producto in enumerate(productos[:5], 1):
            nombre = producto.get('nombre', f'Producto {i}')
            ventas = producto.get('ventas', 0)
            resultado.append(f"{i}. {nombre}: ${ventas:,.2f}")
        
        return "\n".join(resultado)
    
    def _generar_insights_basicos(self, datos: Dict[str, Any]) -> str:
        """Insights tradicionales como fallback"""
        
        ventas = datos.get('ventas_totales', 0)
        transacciones = datos.get('total_transacciones', 0)
        ticket = datos.get('ticket_promedio', 0)
        
        insights = [
            "🔍 ANÁLISIS TRADICIONAL\n"
        ]
        
        # Análisis de rendimiento
        if ventas > 50000:
            insights.append("✅ Excelente rendimiento en ventas totales")
        elif ventas > 10000:
            insights.append("📈 Rendimiento sólido con potencial de crecimiento")
        else:
            insights.append("⚠️ Rendimiento por debajo del objetivo - revisar estrategia")
        
        # Análisis de ticket
        if ticket > 500:
            insights.append("💰 Ticket promedio alto - clientes premium")
        elif ticket > 200:
            insights.append("💵 Ticket promedio saludable")
        else:
            insights.append("💡 Oportunidad de aumentar ticket promedio")
        
        # Recomendaciones
        insights.extend([
            "\n📈 RECOMENDACIONES:",
            "• Implementar análisis de cohortes de clientes",
            "• Optimizar mix de productos de alto margen",
            "• Desarrollar programas de retención",
            "• Monitorear competencia y ajustar precios"
        ])
        
        return "\n".join(insights)
    
    def get_status_info(self) -> Dict[str, Any]:
        """Información del estado del servicio"""
        return {
            'ai_method': self.ai_method,
            'environment': self.environment,
            'ollama_configured': bool(self.ollama_url),
            'gemini_configured': bool(self.gemini_api_key),
            'ollama_available': self._verificar_ollama() if self.ollama_url else False
        }

# Función de inicialización
def inicializar_servicio_ia() -> AdaptiveAIService:
    """Inicializa el servicio adaptativo de IA"""
    return AdaptiveAIService()
