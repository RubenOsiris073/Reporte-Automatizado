"""
Utilidades del sistema de ventas.
Contiene funciones de apoyo, loggers, validators y decoradores.
"""

import os
import logging
import functools
import time
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path
import pandas as pd
import json
from decimal import Decimal

from ..config import settings
from ..core.exceptions import (
    SistemaVentasError,
    DataValidationError,
    FileSystemError
)


# =============================================================================
# CONFIGURACIÓN DE LOGGING
# =============================================================================

class CustomFormatter(logging.Formatter):
    """Formatter personalizado con colores para diferentes niveles."""

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    green = "\x1b[32;20m"
    blue = "\x1b[34;20m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: grey + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.INFO: green + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.WARNING: yellow + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.ERROR: red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.CRITICAL: bold_red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


def setup_logger(name: str = "sistema_ventas") -> logging.Logger:
    """
    Configura y retorna un logger personalizado.

    Args:
        name: Nombre del logger

    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name)

    # Evitar duplicar handlers
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, settings.logging.LOG_LEVEL))

    # Handler para consola
    if settings.logging.CONSOLE_LOGGING:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(CustomFormatter())
        logger.addHandler(console_handler)

    # Handler para archivo principal
    file_handler = logging.FileHandler(
        settings.base.LOGS_DIR / settings.logging.MAIN_LOG_FILE,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        settings.logging.LOG_FORMAT,
        datefmt=settings.logging.DATE_FORMAT
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Handler para errores
    error_handler = logging.FileHandler(
        settings.base.LOGS_DIR / settings.logging.ERROR_LOG_FILE,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)

    return logger


# Logger global del sistema
logger = setup_logger()


# =============================================================================
# DECORADORES ÚTILES
# =============================================================================

def log_execution_time(func: Callable) -> Callable:
    """
    Decorador que registra el tiempo de ejecución de una función.

    Args:
        func: Función a decorar

    Returns:
        Callable: Función decorada
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Iniciando ejecución de {func.__name__}")

        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} completado en {execution_time:.2f} segundos")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} falló después de {execution_time:.2f} segundos: {str(e)}")
            raise

    return wrapper


def handle_exceptions(exception_type: type = SistemaVentasError):
    """
    Decorador que maneja excepciones de manera consistente.

    Args:
        exception_type: Tipo de excepción a usar para errores no esperados

    Returns:
        Callable: Decorador
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except SistemaVentasError:
                # Re-raise excepciones del sistema
                raise
            except Exception as e:
                logger.error(f"Error no esperado en {func.__name__}: {str(e)}")
                raise exception_type(
                    f"Error inesperado en {func.__name__}: {str(e)}",
                    error_code="UNEXPECTED_ERROR"
                )
        return wrapper
    return decorator


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorador para reintentar funciones que pueden fallar.

    Args:
        max_attempts: Número máximo de intentos
        delay: Delay inicial entre intentos
        backoff: Factor de incremento del delay

    Returns:
        Callable: Decorador
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"{func.__name__} falló después de {max_attempts} intentos")
                        raise

                    logger.warning(f"{func.__name__} falló en intento {attempt + 1}/{max_attempts}: {str(e)}")
                    time.sleep(current_delay)
                    current_delay *= backoff

        return wrapper
    return decorator


# =============================================================================
# VALIDADORES
# =============================================================================

class DataValidator:
    """Clase para validaciones de datos comunes."""

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Valida formato de email básico.

        Args:
            email: Email a validar

        Returns:
            bool: True si es válido
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_dataframe(df: pd.DataFrame, required_columns: List[str] = None) -> tuple:
        """
        Valida un DataFrame básico.

        Args:
            df: DataFrame a validar
            required_columns: Columnas requeridas

        Returns:
            tuple: (es_valido, lista_errores)
        """
        errors = []

        if df is None:
            errors.append("DataFrame es None")
            return False, errors

        if df.empty:
            errors.append("DataFrame está vacío")
            return False, errors

        if required_columns:
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                errors.append(f"Columnas faltantes: {', '.join(missing_cols)}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_numeric_range(value: Union[int, float], min_val: float = None, max_val: float = None) -> bool:
        """
        Valida que un valor numérico esté en un rango.

        Args:
            value: Valor a validar
            min_val: Valor mínimo
            max_val: Valor máximo

        Returns:
            bool: True si está en rango
        """
        if not isinstance(value, (int, float)):
            return False

        if min_val is not None and value < min_val:
            return False

        if max_val is not None and value > max_val:
            return False

        return True

    @staticmethod
    def validate_date_range(date_value: Union[str, date, datetime],
                          start_date: Union[str, date, datetime] = None,
                          end_date: Union[str, date, datetime] = None) -> bool:
        """
        Valida que una fecha esté en un rango.

        Args:
            date_value: Fecha a validar
            start_date: Fecha inicio
            end_date: Fecha fin

        Returns:
            bool: True si está en rango
        """
        try:
            if isinstance(date_value, str):
                date_value = pd.to_datetime(date_value).date()
            elif isinstance(date_value, datetime):
                date_value = date_value.date()

            if start_date:
                if isinstance(start_date, str):
                    start_date = pd.to_datetime(start_date).date()
                elif isinstance(start_date, datetime):
                    start_date = start_date.date()

                if date_value < start_date:
                    return False

            if end_date:
                if isinstance(end_date, str):
                    end_date = pd.to_datetime(end_date).date()
                elif isinstance(end_date, datetime):
                    end_date = end_date.date()

                if date_value > end_date:
                    return False

            return True
        except Exception:
            return False


# =============================================================================
# UTILIDADES DE ARCHIVOS
# =============================================================================

class FileUtils:
    """Utilidades para manejo de archivos."""

    @staticmethod
    def safe_create_directory(path: Union[str, Path]) -> bool:
        """
        Crea un directorio de manera segura.

        Args:
            path: Ruta del directorio

        Returns:
            bool: True si se creó exitosamente
        """
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Error creando directorio {path}: {str(e)}")
            return False

    @staticmethod
    def safe_delete_file(file_path: Union[str, Path]) -> bool:
        """
        Elimina un archivo de manera segura.

        Args:
            file_path: Ruta del archivo

        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            Path(file_path).unlink(missing_ok=True)
            return True
        except Exception as e:
            logger.error(f"Error eliminando archivo {file_path}: {str(e)}")
            return False

    @staticmethod
    def get_file_size(file_path: Union[str, Path]) -> int:
        """
        Obtiene el tamaño de un archivo.

        Args:
            file_path: Ruta del archivo

        Returns:
            int: Tamaño en bytes, -1 si hay error
        """
        try:
            return Path(file_path).stat().st_size
        except Exception:
            return -1

    @staticmethod
    def backup_file(file_path: Union[str, Path], backup_suffix: str = None) -> Optional[str]:
        """
        Crea una copia de seguridad de un archivo.

        Args:
            file_path: Ruta del archivo original
            backup_suffix: Sufijo para el backup

        Returns:
            Optional[str]: Ruta del backup o None si hay error
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return None

            if not backup_suffix:
                backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")

            backup_path = file_path.with_suffix(f".{backup_suffix}{file_path.suffix}")

            import shutil
            shutil.copy2(file_path, backup_path)

            logger.info(f"Backup creado: {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"Error creando backup de {file_path}: {str(e)}")
            return None


# =============================================================================
# UTILIDADES DE FORMATO
# =============================================================================

class FormatUtils:
    """Utilidades para formateo de datos."""

    @staticmethod
    def format_currency(amount: Union[int, float, Decimal], currency: str = "MXN") -> str:
        """
        Formatea un monto como moneda.

        Args:
            amount: Monto a formatear
            currency: Código de moneda

        Returns:
            str: Monto formateado
        """
        try:
            if currency == "MXN":
                return f"${amount:,.2f} MXN"
            else:
                return f"{amount:,.2f} {currency}"
        except Exception:
            return f"${amount} {currency}"

    @staticmethod
    def format_percentage(value: Union[int, float], decimals: int = 2) -> str:
        """
        Formatea un valor como porcentaje.

        Args:
            value: Valor a formatear
            decimals: Número de decimales

        Returns:
            str: Valor formateado como porcentaje
        """
        try:
            return f"{value:.{decimals}f}%"
        except Exception:
            return f"{value}%"

    @staticmethod
    def format_large_number(number: Union[int, float]) -> str:
        """
        Formatea números grandes con sufijos (K, M, B).

        Args:
            number: Número a formatear

        Returns:
            str: Número formateado
        """
        try:
            if abs(number) >= 1_000_000_000:
                return f"{number/1_000_000_000:.2f}B"
            elif abs(number) >= 1_000_000:
                return f"{number/1_000_000:.2f}M"
            elif abs(number) >= 1_000:
                return f"{number/1_000:.2f}K"
            else:
                return f"{number:,.2f}"
        except Exception:
            return str(number)

    @staticmethod
    def safe_json_serialize(obj: Any) -> str:
        """
        Serializa un objeto a JSON de forma segura.

        Args:
            obj: Objeto a serializar

        Returns:
            str: JSON string
        """
        def default_serializer(o):
            if isinstance(o, (date, datetime)):
                return o.isoformat()
            elif isinstance(o, Decimal):
                return float(o)
            elif hasattr(o, 'to_dict'):
                return o.to_dict()
            return str(o)

        try:
            return json.dumps(obj, default=default_serializer, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error serializando a JSON: {str(e)}")
            return "{}"


# =============================================================================
# UTILIDADES DE TIEMPO
# =============================================================================

class TimeUtils:
    """Utilidades para manejo de tiempo y fechas."""

    @staticmethod
    def get_current_timestamp() -> str:
        """
        Obtiene timestamp actual en formato ISO.

        Returns:
            str: Timestamp actual
        """
        return datetime.now().isoformat()

    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        Formatea una duración en segundos a formato legible.

        Args:
            seconds: Duración en segundos

        Returns:
            str: Duración formateada
        """
        if seconds < 60:
            return f"{seconds:.2f} segundos"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.2f} minutos"
        else:
            hours = seconds / 3600
            return f"{hours:.2f} horas"

    @staticmethod
    def get_business_days_between(start_date: date, end_date: date) -> int:
        """
        Calcula días laborables entre dos fechas.

        Args:
            start_date: Fecha inicio
            end_date: Fecha fin

        Returns:
            int: Número de días laborables
        """
        try:
            return pd.bdate_range(start_date, end_date).shape[0]
        except Exception:
            return 0


# =============================================================================
# UTILIDADES DE SISTEMA
# =============================================================================

class SystemUtils:
    """Utilidades del sistema."""

    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """
        Obtiene información del uso de memoria.

        Returns:
            Dict[str, float]: Información de memoria
        """
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                'total_gb': memory.total / (1024**3),
                'available_gb': memory.available / (1024**3),
                'used_gb': memory.used / (1024**3),
                'percentage': memory.percent
            }
        except ImportError:
            return {'error': 'psutil no disponible'}
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def check_disk_space(path: Union[str, Path] = '.') -> Dict[str, float]:
        """
        Verifica el espacio en disco.

        Args:
            path: Ruta a verificar

        Returns:
            Dict[str, float]: Información de disco
        """
        try:
            import shutil
            total, used, free = shutil.disk_usage(path)
            return {
                'total_gb': total / (1024**3),
                'used_gb': used / (1024**3),
                'free_gb': free / (1024**3),
                'percentage_used': (used / total) * 100
            }
        except Exception as e:
            return {'error': str(e)}


# =============================================================================
# EXPORTAR UTILIDADES
# =============================================================================

__all__ = [
    # Logger
    'setup_logger',
    'logger',

    # Decoradores
    'log_execution_time',
    'handle_exceptions',
    'retry',

    # Validadores
    'DataValidator',

    # Utilidades
    'FileUtils',
    'FormatUtils',
    'TimeUtils',
    'SystemUtils',
]
