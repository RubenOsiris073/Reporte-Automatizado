"""
Configuración centralizada del sistema de ventas.
Maneja todas las configuraciones del sistema de forma segura y centralizada.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


# =============================================================================
# CONFIGURACIÓN BASE
# =============================================================================

@dataclass
class BaseConfig:
    """Configuración base del sistema."""

    # Información del proyecto
    PROJECT_NAME: str = os.getenv('PROJECT_NAME', 'Sistema Empresarial de Análisis de Ventas')
    VERSION: str = os.getenv('VERSION', '1.0.0')
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'

    # Paths del sistema
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    REPORTS_DIR: Path = BASE_DIR / "reports"
    TEMP_DIR: Path = BASE_DIR / "temp"

    def __post_init__(self):
        """Crear directorios si no existen."""
        for directory in [self.DATA_DIR, self.LOGS_DIR, self.REPORTS_DIR, self.TEMP_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


# =============================================================================
# CONFIGURACIÓN DE EMAIL
# =============================================================================

@dataclass
class EmailConfig:
    """Configuración para servicios de email."""

    # Configuración SMTP
    SMTP_SERVER: str = os.getenv('SMTP_SERVER', '')
    SMTP_PORT: int = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER: str = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD: str = os.getenv('SMTP_PASSWORD', '')

    # Configuración de emails
    FROM_EMAIL: str = os.getenv('FROM_EMAIL', '')
    FROM_NAME: str = os.getenv('FROM_NAME', '')
    DEFAULT_TO_EMAIL: str = os.getenv('TO_EMAIL', '')

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path


# =============================================================================
# CONFIGURACIÓN BASE
# =============================================================================

@dataclass
class BaseConfig:
    """Configuración base del sistema."""

    # Información del proyecto
    PROJECT_NAME: str = "Sistema Empresarial de Análisis de Ventas"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Paths del sistema
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    REPORTS_DIR: Path = BASE_DIR / "reports"
    TEMP_DIR: Path = BASE_DIR / "temp"

    def __post_init__(self):
        """Crear directorios si no existen."""
        for directory in [self.DATA_DIR, self.LOGS_DIR, self.REPORTS_DIR, self.TEMP_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


# =============================================================================
# CONFIGURACIÓN DE EMAIL
# =============================================================================

@dataclass
class EmailConfig:
    """Configuración para servicios de email."""

    # Configuración SMTP
    SMTP_SERVER: str = os.getenv('SMTP_SERVER', '')
    SMTP_PORT: int = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER: str = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD: str = os.getenv('SMTP_PASSWORD', '')

    # Configuración de emails
    FROM_EMAIL: str = os.getenv('FROM_EMAIL', '')
    FROM_NAME: str = os.getenv('FROM_NAME', '')
    DEFAULT_TO_EMAIL: str = os.getenv('TO_EMAIL', '')

    # Configuración de reintentos
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5  # segundos

    # Templates de email
    SUBJECT_TEMPLATE: str = "Reporte Empresarial de Ventas - {fecha}"

    # Configuración de templates HTML
    USE_HTML_TEMPLATES: bool = field(default=True)
    DEFAULT_TEMPLATE: str = field(default="email_report.html")
    FALLBACK_TEMPLATE: str = field(default="email_report_simple.html")

    # Formatos de email soportados
    PREFERRED_FORMAT: str = field(default="html")  # html, multipart, plain
    INCLUDE_PLAIN_TEXT_FALLBACK: bool = field(default=False)

    # Template HTML básico (fallback legacy)
    HTML_TEMPLATE: str = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reporte de Ventas</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">📊 Reporte Empresarial de Ventas</h1>
            <p style="margin: 10px 0 0; opacity: 0.9;">Fecha: {fecha}</p>
        </div>
        <div style="background: #ffffff; padding: 30px; border: 1px solid #ddd; border-radius: 0 0 8px 8px;">
            {contenido}
        </div>
        <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
            <p>Generado automáticamente por <strong>{project_name}</strong></p>
            <p>🔒 Información Confidencial - Uso Interno Exclusivo</p>
        </div>
    </body>
    </html>
    """

    # Configuración de plantillas avanzadas
    TEMPLATE_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "use_responsive_design": True,
        "include_company_branding": True,
        "color_scheme": "professional",  # professional, modern, classic
        "include_charts": False,  # Para futuras implementaciones
        "max_template_size_kb": 100
    })

    def validate(self) -> bool:
        """Valida la configuración de email."""
        required_fields = [
            self.SMTP_SERVER,
            self.SMTP_USER,
            self.SMTP_PASSWORD,
            self.FROM_EMAIL,
            self.DEFAULT_TO_EMAIL
        ]
        return all(field for field in required_fields)


# =============================================================================
# CONFIGURACIÓN DE GOOGLE SHEETS
# =============================================================================

@dataclass
class SheetsConfig:
    """Configuración para Google Sheets."""

    # Archivos de credenciales
    CREDENTIALS_FILE: str = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    SERVICE_ACCOUNT_FILE: str = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'service_account.json')

    # Configuración de sheets
    DEFAULT_SHEET_ID: str = os.getenv('GOOGLE_SHEET_ID', '')
    DEFAULT_WORKSHEET_NAME: str = "Ventas"

    # Scopes necesarios
    SCOPES: List[str] = field(default_factory=lambda: [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ])

    # Configuración de reintentos
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 2  # segundos

    def get_credentials_path(self) -> Path:
        """Obtiene la ruta completa del archivo de credenciales."""
        return Path(self.CREDENTIALS_FILE)

    def validate(self) -> bool:
        """Valida la configuración de sheets."""
        return bool(self.DEFAULT_SHEET_ID) and self.get_credentials_path().exists()


# =============================================================================
# CONFIGURACIÓN DE ANÁLISIS DE DATOS
# =============================================================================

@dataclass
class DataAnalysisConfig:
    """Configuración para análisis de datos."""

    # Configuración de pandas
    PANDAS_DISPLAY_MAX_ROWS: int = 100
    PANDAS_DISPLAY_MAX_COLUMNS: int = 50

    # Configuración de análisis
    DEFAULT_PERIOD: str = "mensual"  # diario, semanal, mensual
    ANOMALY_THRESHOLD: float = 2.0  # desviaciones estándar
    PREDICTION_PERIODS: int = 3

    # Métricas KPI
    KPI_METRICS: List[str] = field(default_factory=lambda: [
        'total_ventas',
        'promedio_ventas',
        'crecimiento_mensual',
        'productos_top',
        'clientes_activos',
        'ticket_promedio'
    ])

    # Formatos de exportación soportados
    EXPORT_FORMATS: List[str] = field(default_factory=lambda: ['json', 'csv', 'excel', 'pdf'])

    # Configuración de gráficos
    PLOT_STYLE: str = 'seaborn-v0_8'
    FIGURE_SIZE: tuple = (12, 8)
    DPI: int = 300


# =============================================================================
# CONFIGURACIÓN DE LOGGING
# =============================================================================

@dataclass
class LoggingConfig:
    """Configuración para logging."""

    # Niveles de logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

    # Formatos
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DATE_FORMAT: str = '%Y-%m-%d %H:%M:%S'

    # Archivos de log
    MAIN_LOG_FILE: str = 'sistema_ventas.log'
    ERROR_LOG_FILE: str = 'errores.log'

    # Configuración de rotación
    MAX_LOG_SIZE: int = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT: int = 5

    # Logging a consola
    CONSOLE_LOGGING: bool = True


# =============================================================================
# CONFIGURACIÓN DE REPORTES
# =============================================================================

@dataclass
class ReportConfig:
    """Configuración para generación de reportes."""

    # Templates de reportes
    DEFAULT_TEMPLATE: str = "reporte_ejecutivo"
    AVAILABLE_TEMPLATES: List[str] = field(default_factory=lambda: [
        "reporte_ejecutivo",
        "reporte_detallado",
        "reporte_kpis",
        "reporte_tendencias"
    ])

    # Formatos de salida
    OUTPUT_FORMATS: List[str] = field(default_factory=lambda: ['html', 'pdf', 'excel'])
    DEFAULT_FORMAT: str = 'html'

    # Configuración de archivos
    FILENAME_PATTERN: str = "reporte_ventas_{fecha}_{tipo}.{extension}"
    AUTO_CLEANUP_DAYS: int = 30  # días para mantener reportes antiguos


# =============================================================================
# CONFIGURACIÓN PRINCIPAL
# =============================================================================

class Settings:
    """Clase principal de configuración del sistema."""

    def __init__(self):
        self.base = BaseConfig()
        self.email = EmailConfig()
        self.sheets = SheetsConfig()
        self.data_analysis = DataAnalysisConfig()
        self.logging = LoggingConfig()
        self.reports = ReportConfig()

    def validate_all(self) -> Dict[str, bool]:
        """
        Valida todas las configuraciones.

        Returns:
            Dict[str, bool]: Estado de validación por módulo
        """
        return {
            'email': self.email.validate(),
            'sheets': self.sheets.validate(),
            'base': True,  # BaseConfig siempre es válida
            'data_analysis': True,  # DataAnalysisConfig siempre es válida
            'logging': True,  # LoggingConfig siempre es válida
            'reports': True,  # ReportConfig siempre es válida
        }

    def get_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen de la configuración actual.

        Returns:
            Dict[str, Any]: Resumen de configuración
        """
        return {
            'project': {
                'name': self.base.PROJECT_NAME,
                'version': self.base.VERSION,
                'debug': self.base.DEBUG
            },
            'paths': {
                'base_dir': str(self.base.BASE_DIR),
                'data_dir': str(self.base.DATA_DIR),
                'logs_dir': str(self.base.LOGS_DIR),
                'reports_dir': str(self.base.REPORTS_DIR)
            },
            'validation': self.validate_all()
        }


# =============================================================================
# INSTANCIA GLOBAL DE CONFIGURACIÓN
# =============================================================================

# Instancia global de configuración
settings = Settings()

# Exportar las configuraciones principales
__all__ = [
    'settings',
    'BaseConfig',
    'EmailConfig',
    'SheetsConfig',
    'DataAnalysisConfig',
    'LoggingConfig',
    'ReportConfig',
    'Settings'
]
