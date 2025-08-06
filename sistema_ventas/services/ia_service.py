#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servicio de IA Integrado para Sistema de Análisis de Ventas
==========================================================

Servicio especializado para análisis estratégico con IA usando Ollama.
Incluye fallbacks robustos y manejo de errores para evitar colgados del sistema.

Author: Sistema Empresarial de Ventas
Version: 2.0.0
"""

import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional, Union
import time

from ..core.exceptions import SistemaVentasError
from ..config import settings
from ..utils import logger


class IAServiceError(SistemaVentasError):
    """Excepción específica para errores del servicio de IA."""
    pass


class IAService:
    """
    Servicio de IA integrado para análisis estratégico de ventas.

    Características:
    - Integración con Ollama local
    - Fallback a análisis básico
    - Timeouts cortos para evitar colgados
    - Manejo robusto de errores
    - Análisis específico para datos de ventas mexicanas
    """

    def __init__(self, ollama_url: str = "http://127.0.0.1:11434",
                 modelo: str = "qwen2.5:3b", timeout: int = 120):
        """
        Inicializa el servicio de IA.

        Args:
            ollama_url: URL del servicio Ollama
            modelo: Modelo a usar para análisis
            timeout: Timeout en segundos para requests
        """
        self.ollama_url = ollama_url
        self.modelo = modelo
        self.timeout = timeout
        self.disponible = None  # Cache del estado de disponibilidad
        self._ultima_verificacion = 0
        self._cache_verificacion = 300  # 5 minutos

    def verificar_disponibilidad(self) -> bool:
        """
        Verifica si Ollama está disponible.

        Returns:
            bool: True si Ollama está disponible y respondiendo
        """
        # Usar cache por 5 minutos para evitar verificaciones constantes
        ahora = time.time()
        if (self.disponible is not None and
            (ahora - self._ultima_verificacion) < self._cache_verificacion):
            return self.disponible

        try:
            response = requests.get(
                f"{self.ollama_url}/api/tags",
                timeout=5  # Timeout muy corto para verificación
            )

            if response.status_code == 200:
                modelos = response.json()
                modelo_disponible = any(
                    modelo.get('name', '').startswith(self.modelo.split(':')[0])
                    for modelo in modelos.get('models', [])
                )

                self.disponible = modelo_disponible
                self._ultima_verificacion = ahora

                if modelo_disponible:
                    logger.info(f"Ollama disponible con modelo {self.modelo}")
                else:
                    logger.warning(f"Ollama disponible pero modelo {self.modelo} no encontrado")

                return self.disponible
            else:
                self.disponible = False
                self._ultima_verificacion = ahora
                return False

        except requests.exceptions.RequestException as e:
            logger.debug(f"Ollama no disponible: {str(e)}")
            self.disponible = False
            self._ultima_verificacion = ahora
            return False

    def generar_analisis_ia(self, datos_resumen: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera análisis estratégico con IA.

        Args:
            datos_resumen: Datos del resumen de ventas

        Returns:
            Dict[str, Any]: Resultado del análisis con status, analysis, etc.
        """
        # Verificar disponibilidad primero - OBLIGATORIO
        if not self.verificar_disponibilidad():
            raise IAServiceError(
                "Ollama no está disponible. El análisis con IA es obligatorio.",
                error_code="OLLAMA_NOT_AVAILABLE"
            )

        try:
            # Preparar prompt estructurado
            prompt = self._crear_prompt_analisis(datos_resumen)

            # Realizar solicitud a Ollama con timeout optimizado
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.modelo,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.8,
                        "num_predict": 800
                    }
                },
                timeout=self.timeout
            )

            if response.status_code == 200:
                resultado = response.json()
                analisis = resultado.get('response', '').strip()

                if analisis and len(analisis) > 100:  # Verificar que hay contenido útil
                    return {
                        'status': 'success',
                        'analysis': analisis,
                        'model_used': self.modelo,
                        'source': 'ollama',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    raise IAServiceError(
                        "Ollama devolvió respuesta vacía o muy corta",
                        error_code="OLLAMA_EMPTY_RESPONSE"
                    )
            else:
                raise IAServiceError(
                    f"Error HTTP {response.status_code} de Ollama",
                    error_code="OLLAMA_HTTP_ERROR"
                )

        except requests.exceptions.Timeout:
            logger.error("Timeout en solicitud a Ollama")
            raise IAServiceError(
                "Timeout en Ollama. Aumente el timeout o verifique el rendimiento del modelo.",
                error_code="OLLAMA_TIMEOUT"
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con Ollama: {str(e)}")
            raise IAServiceError(
                f"Error de conexión con Ollama: {str(e)}",
                error_code="OLLAMA_CONNECTION_ERROR"
            )

        except Exception as e:
            logger.error(f"Error inesperado en análisis IA: {str(e)}")
            raise IAServiceError(
                f"Error inesperado en análisis IA: {str(e)}",
                error_code="OLLAMA_UNEXPECTED_ERROR"
            )

    def _crear_prompt_analisis(self, datos_resumen: Dict[str, Any]) -> str:
        """
        Crea un prompt estructurado para el análisis de IA.

        Args:
            datos_resumen: Datos del resumen de ventas

        Returns:
            str: Prompt formateado para Ollama
        """
        # Extraer métricas principales
        metricas = datos_resumen.get('metricas_ventas', {})
        ventas_totales = metricas.get('ventas_totales', datos_resumen.get('ventas_totales', 0))
        ticket_promedio = metricas.get('ticket_promedio', datos_resumen.get('ticket_promedio', 0))
        transacciones = (metricas.get('transacciones', 0) or
                        metricas.get('num_transacciones', 0) or
                        datos_resumen.get('transacciones', 0) or
                        datos_resumen.get('num_transacciones', 0))

        # Top productos
        top_productos = datos_resumen.get('top_productos', {})

        prompt = f"""Analiza datos de ventas mexicanas (MXN):

VENTAS: ${ventas_totales:,.2f} MXN
TICKET: ${ticket_promedio:,.2f} MXN
TRANSACCIONES: {transacciones:,}

TOP PRODUCTOS:"""

        for i, (producto, venta) in enumerate(list(top_productos.items())[:3], 1):
            prompt += f"\n{i}. {producto}: ${venta:,.2f}"

        prompt += f"""

Formato requerido:

RESUMEN EJECUTIVO: [evaluación en 2 líneas]

FORTALEZAS:
• [punto clave 1]
• [punto clave 2]
• [punto clave 3]

OPORTUNIDADES:
• [área de crecimiento 1]
• [área de crecimiento 2]
• [área de crecimiento 3]

RECOMENDACIONES:
• [acción específica 1]
• [acción específica 2]
• [acción específica 3]

PROYECCIÓN: [estimación en 1 línea]

Respuesta concisa, profesional, enfocada en México."""

        return prompt

    def obtener_estado(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del servicio de IA.

        Returns:
            Dict[str, Any]: Estado detallado del servicio
        """
        disponible = self.verificar_disponibilidad()

        return {
            'servicio_disponible': disponible,
            'ollama_url': self.ollama_url,
            'modelo': self.modelo,
            'timeout': self.timeout,
            'ultima_verificacion': datetime.fromtimestamp(self._ultima_verificacion).isoformat() if self._ultima_verificacion > 0 else None,
            'cache_valido': (time.time() - self._ultima_verificacion) < self._cache_verificacion if self._ultima_verificacion > 0 else False
        }

    def limpiar_cache(self):
        """Limpia el cache de disponibilidad para forzar nueva verificación."""
        self.disponible = None
        self._ultima_verificacion = 0
        logger.info("Cache de disponibilidad de IA limpiado")


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def crear_servicio_ia(ollama_url: str = None, modelo: str = None, timeout: int = None) -> IAService:
    """
    Factory function para crear una instancia del servicio de IA.

    Args:
        ollama_url: URL opcional de Ollama
        modelo: Modelo opcional a usar
        timeout: Timeout opcional

    Returns:
        IAService: Instancia configurada del servicio
    """
    return IAService(
        ollama_url=ollama_url or "http://127.0.0.1:11434",
        modelo=modelo or "qwen2.5:3b",
        timeout=timeout or 120
    )


def verificar_ollama_disponible(url: str = "http://127.0.0.1:11434") -> bool:
    """
    Función de utilidad para verificar rápidamente si Ollama está disponible.

    Args:
        url: URL de Ollama

    Returns:
        bool: True si está disponible
    """
    try:
        response = requests.get(f"{url}/api/tags", timeout=3)
        return response.status_code == 200
    except:
        return False


# =============================================================================
# EXPORTACIONES
# =============================================================================

__all__ = [
    'IAService',
    'IAServiceError',
    'crear_servicio_ia',
    'verificar_ollama_disponible'
]
