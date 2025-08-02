#!/usr/bin/env python3
"""
Servicio de Ollama para análisis de ventas
Solo funciona con Ollama local
"""

import requests
import json
import logging
import os
from typing import Dict, Any
from datetime import datetime

class OllamaService:
    """Servicio simple para análisis con Ollama"""
    
    def __init__(self):
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'qwen2.5:latest')
        self.timeout = 30
        self.logger = logging.getLogger(__name__)
        
    def generar_analisis_ia(self, datos_ventas: Dict[str, Any]) -> Dict[str, Any]:
        """Genera análisis usando Ollama"""
        
        resultado_base = {
            'timestamp': datetime.now().isoformat(),
            'ai_method': 'ollama',
            'status': 'processing'
        }
        
        return self._analisis_ollama(datos_ventas, resultado_base)
    
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
    
    def _formatear_productos_prompt(self, productos) -> str:
        """Formatea productos para el prompt"""
        if not productos:
            return "No hay datos de productos"
        
        resultado = []
        for i, (nombre, ventas) in enumerate(productos.items() if isinstance(productos, dict) else enumerate(productos), 1):
            if isinstance(productos, dict):
                resultado.append(f"{i}. {nombre}: ${ventas:,.2f}")
            else:
                nombre = productos.get('nombre', f'Producto {i}')
                ventas = productos.get('ventas', 0)
                resultado.append(f"{i}. {nombre}: ${ventas:,.2f}")
        
        return "\n".join(resultado)
    
    def _generar_insights_basicos(self, datos: Dict[str, Any]) -> str:
        """Insights básicos cuando Ollama no está disponible"""
        
        ventas = datos.get('ventas_totales', 0)
        transacciones = datos.get('total_transacciones', 0)
        ticket = datos.get('ticket_promedio', 0)
        
        insights = [
            "🔍 ANÁLISIS BÁSICO (Ollama no disponible)\n"
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
            "• Verificar que Ollama esté ejecutándose",
            "• Optimizar mix de productos de alto margen",
            "• Desarrollar programas de retención",
            "• Monitorear competencia y ajustar precios"
        ])
        
        return "\n".join(insights)

# Función de inicialización
def inicializar_servicio_ia() -> OllamaService:
    """Inicializa el servicio de Ollama"""
    return OllamaService()
