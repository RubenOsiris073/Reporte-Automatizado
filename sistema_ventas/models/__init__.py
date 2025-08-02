"""
Modelos de datos del sistema de ventas.
Define las estructuras de datos principales que usa el sistema.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from enum import Enum
import json
from pathlib import Path


# =============================================================================
# ENUMERACIONES
# =============================================================================

class TipoReporte(Enum):
    """Tipos de reportes disponibles."""
    EJECUTIVO = "ejecutivo"
    DETALLADO = "detallado"
    KPIS = "kpis"
    TENDENCIAS = "tendencias"


class EstadoVenta(Enum):
    """Estados posibles de una venta."""
    PENDIENTE = "pendiente"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"
    REEMBOLSADA = "reembolsada"


class PeriodoAnalisis(Enum):
    """Períodos de análisis disponibles."""
    DIARIO = "diario"
    SEMANAL = "semanal"
    MENSUAL = "mensual"
    TRIMESTRAL = "trimestral"
    ANUAL = "anual"


# =============================================================================
# MODELOS BASE
# =============================================================================

class BaseModel:
    """Modelo base con funcionalidades comunes."""

    def __init__(self):
        """Inicialización base."""
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, date):
                result[key] = value.isoformat()
            elif isinstance(value, Decimal):
                result[key] = float(value)
            elif isinstance(value, Enum):
                result[key] = value.value
            elif hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [
                    item.to_dict() if hasattr(item, 'to_dict') else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    def to_json(self) -> str:
        """Convierte el modelo a JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def save_to_file(self, filepath: Union[str, Path]):
        """Guarda el modelo en un archivo JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())


# =============================================================================
# MODELOS DE PRODUCTOS Y CLIENTES
# =============================================================================

@dataclass
class Product:
    """Modelo para productos."""

    id: str
    nombre: str
    categoria: str
    precio: Decimal
    descripcion: Optional[str] = None
    activo: bool = True
    stock: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validaciones post-inicialización."""
        if self.precio < 0:
            raise ValueError("El precio no puede ser negativo")
        if self.stock is not None and self.stock < 0:
            raise ValueError("El stock no puede ser negativo")

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, date):
                result[key] = value.isoformat()
            elif isinstance(value, Decimal):
                result[key] = float(value)
            elif isinstance(value, Enum):
                result[key] = value.value
            elif hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [
                    item.to_dict() if hasattr(item, 'to_dict') else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    def to_json(self) -> str:
        """Convierte el modelo a JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def save_to_file(self, filepath: Union[str, Path]):
        """Guarda el modelo en un archivo JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())


@dataclass
class Customer:
    """Modelo para clientes."""

    id: str
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    fecha_registro: Optional[date] = None
    activo: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validaciones post-inicialización."""
        if self.fecha_registro is None:
            self.fecha_registro = date.today()

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, date):
                result[key] = value.isoformat()
            elif isinstance(value, Decimal):
                result[key] = float(value)
            elif isinstance(value, Enum):
                result[key] = value.value
            elif hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [
                    item.to_dict() if hasattr(item, 'to_dict') else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    def to_json(self) -> str:
        """Convierte el modelo a JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def save_to_file(self, filepath: Union[str, Path]):
        """Guarda el modelo en un archivo JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())


# =============================================================================
# MODELO PRINCIPAL DE VENTAS
# =============================================================================

@dataclass
class SalesData:
    """Modelo para datos de ventas individuales."""

    id: str
    fecha: date
    cliente_id: str
    producto_id: str
    cantidad: int
    precio_unitario: Decimal
    descuento: Decimal = Decimal('0.00')
    impuestos: Decimal = Decimal('0.00')
    estado: EstadoVenta = EstadoVenta.COMPLETADA
    vendedor: Optional[str] = None
    notas: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Campos calculados
    subtotal: Decimal = field(init=False)
    total: Decimal = field(init=False)

    def __post_init__(self):
        """Cálculos y validaciones post-inicialización."""
        # Validaciones
        if self.cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        if self.precio_unitario < 0:
            raise ValueError("El precio unitario no puede ser negativo")
        if self.descuento < 0:
            raise ValueError("El descuento no puede ser negativo")
        if self.impuestos < 0:
            raise ValueError("Los impuestos no pueden ser negativos")

        # Cálculos
        self.subtotal = self.precio_unitario * self.cantidad
        self.total = self.subtotal - self.descuento + self.impuestos

    @property
    def margen_descuento(self) -> float:
        """Calcula el porcentaje de descuento."""
        if self.subtotal == 0:
            return 0.0
        return float(self.descuento / self.subtotal * 100)

    @property
    def es_venta_valida(self) -> bool:
        """Verifica si la venta es válida."""
        return (
            self.estado in [EstadoVenta.COMPLETADA, EstadoVenta.PENDIENTE] and
            self.total > 0
        )


# =============================================================================
# MODELOS DE MÉTRICAS Y KPIs
# =============================================================================

@dataclass
class KPIMetrics:
    """Modelo para métricas KPI."""

    # Métricas básicas
    total_ventas: Decimal
    numero_transacciones: int
    ticket_promedio: Decimal

    # Métricas de crecimiento
    crecimiento_ventas: Optional[float] = None
    crecimiento_transacciones: Optional[float] = None

    # Métricas de productos
    productos_vendidos: int = 0
    producto_top: Optional[str] = None
    categoria_top: Optional[str] = None

    # Métricas de clientes
    clientes_activos: int = 0
    cliente_top: Optional[str] = None
    clientes_nuevos: int = 0

    # Métricas de tiempo
    periodo_inicio: Optional[date] = None
    periodo_fin: Optional[date] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validaciones post-inicialización."""
        # Inicializar fechas si no se proporcionaron
        if self.periodo_inicio is None:
            self.periodo_inicio = date.today()
        if self.periodo_fin is None:
            self.periodo_fin = date.today()

        if self.numero_transacciones < 0:
            raise ValueError("El número de transacciones no puede ser negativo")
        if self.total_ventas < 0:
            raise ValueError("El total de ventas no puede ser negativo")
        if self.periodo_inicio > self.periodo_fin:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin")

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, date):
                result[key] = value.isoformat()
            elif isinstance(value, Decimal):
                result[key] = float(value)
            elif isinstance(value, Enum):
                result[key] = value.value
            elif hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [
                    item.to_dict() if hasattr(item, 'to_dict') else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    def to_json(self) -> str:
        """Convierte el modelo a JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def save_to_file(self, filepath: Union[str, Path]):
        """Guarda el modelo en un archivo JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    @property
    def conversion_rate(self) -> float:
        """Calcula la tasa de conversión."""
        if self.clientes_activos == 0:
            return 0.0
        return (self.numero_transacciones / self.clientes_activos) * 100


@dataclass
class TrendAnalysis:
    """Modelo para análisis de tendencias."""

    periodo: PeriodoAnalisis
    fecha_inicio: date
    fecha_fin: date

    # Datos de tendencia
    valores: List[Decimal] = field(default_factory=list)
    fechas: List[date] = field(default_factory=list)

    # Métricas de tendencia
    tendencia: str = ""  # "creciente", "decreciente", "estable"
    pendiente: Optional[float] = None
    r_cuadrado: Optional[float] = None

    # Predicciones
    predicciones_futuras: List[Decimal] = field(default_factory=list)
    fechas_prediccion: List[date] = field(default_factory=list)
    intervalo_confianza: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validaciones post-inicialización."""
        if len(self.valores) != len(self.fechas):
            raise ValueError("Los valores y fechas deben tener la misma longitud")
        if self.fecha_inicio > self.fecha_fin:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin")

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, date):
                result[key] = value.isoformat()
            elif isinstance(value, Decimal):
                result[key] = float(value)
            elif isinstance(value, Enum):
                result[key] = value.value
            elif hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [
                    item.to_dict() if hasattr(item, 'to_dict') else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    def to_json(self) -> str:
        """Convierte el modelo a JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def save_to_file(self, filepath: Union[str, Path]):
        """Guarda el modelo en un archivo JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    @property
    def tiene_datos_suficientes(self) -> bool:
        """Verifica si hay suficientes datos para el análisis."""
        return len(self.valores) >= 3

    @property
    def variacion_total(self) -> Optional[float]:
        """Calcula la variación total del período."""
        if len(self.valores) < 2:
            return None

        inicial = float(self.valores[0])
        final = float(self.valores[-1])

        if inicial == 0:
            return None

        return ((final - inicial) / inicial) * 100


# =============================================================================
# MODELO DE REPORTES
# =============================================================================

@dataclass
class SalesReport:
    """Modelo para reportes de ventas."""

    id: str
    titulo: str
    tipo: TipoReporte
    fecha_inicio: date
    fecha_fin: date
    fecha_generacion: Optional[datetime] = None

    # Datos del reporte
    kpis: Optional[KPIMetrics] = None
    tendencias: List[TrendAnalysis] = field(default_factory=list)
    datos_ventas: List[SalesData] = field(default_factory=list)

    # Metadatos
    generado_por: Optional[str] = None
    notas: Optional[str] = None
    version: str = "1.0"

    # Archivos generados
    archivos_generados: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validaciones post-inicialización."""
        # Inicializar fecha de generación si no se proporcionó
        if self.fecha_generacion is None:
            self.fecha_generacion = datetime.now()

        if self.fecha_inicio > self.fecha_fin:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin")

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, date):
                result[key] = value.isoformat()
            elif isinstance(value, Decimal):
                result[key] = float(value)
            elif isinstance(value, Enum):
                result[key] = value.value
            elif hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [
                    item.to_dict() if hasattr(item, 'to_dict') else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    def to_json(self) -> str:
        """Convierte el modelo a JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def save_to_file(self, filepath: Union[str, Path]):
        """Guarda el modelo en un archivo JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    @property
    def duracion_periodo(self) -> int:
        """Calcula la duración del período en días."""
        return (self.fecha_fin - self.fecha_inicio).days + 1

    @property
    def total_ventas_periodo(self) -> Decimal:
        """Calcula el total de ventas del período."""
        if self.kpis:
            return self.kpis.total_ventas
        return sum(venta.total for venta in self.datos_ventas)

    def agregar_archivo_generado(self, filepath: Union[str, Path]):
        """Agrega un archivo generado al reporte."""
        self.archivos_generados.append(str(filepath))

    def get_resumen_ejecutivo(self) -> Dict[str, Any]:
        """Genera un resumen ejecutivo del reporte."""
        return {
            'titulo': self.titulo,
            'periodo': f"{self.fecha_inicio} - {self.fecha_fin}",
            'duracion_dias': self.duracion_periodo,
            'total_ventas': float(self.total_ventas_periodo),
            'numero_transacciones': len(self.datos_ventas),
            'fecha_generacion': self.fecha_generacion.isoformat(),
            'tipo_reporte': self.tipo.value
        }


# =============================================================================
# MODELOS DE RESPUESTA API
# =============================================================================

@dataclass
class APIResponse:
    """Modelo estándar para respuestas de API."""

    success: bool
    message: str
    data: Optional[Any] = None
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def success_response(cls, message: str, data: Any = None, **metadata) -> 'APIResponse':
        """Crea una respuesta exitosa."""
        return cls(
            success=True,
            message=message,
            data=data,
            metadata=metadata
        )

    @classmethod
    def error_response(cls, message: str, errors: List[str] = None) -> 'APIResponse':
        """Crea una respuesta de error."""
        return cls(
            success=False,
            message=message,
            errors=errors or []
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, date):
                result[key] = value.isoformat()
            elif isinstance(value, Decimal):
                result[key] = float(value)
            elif isinstance(value, Enum):
                result[key] = value.value
            elif hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [
                    item.to_dict() if hasattr(item, 'to_dict') else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    def to_json(self) -> str:
        """Convierte el modelo a JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def save_to_file(self, filepath: Union[str, Path]):
        """Guarda el modelo en un archivo JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())


# =============================================================================
# EXPORTAR TODOS LOS MODELOS
# =============================================================================

__all__ = [
    # Enumeraciones
    'TipoReporte',
    'EstadoVenta',
    'PeriodoAnalisis',

    # Modelos base
    'BaseModel',

    # Modelos de entidades
    'Product',
    'Customer',
    'SalesData',

    # Modelos de análisis
    'KPIMetrics',
    'TrendAnalysis',

    # Modelos de reportes
    'SalesReport',

    # Modelos de API
    'APIResponse',
]
