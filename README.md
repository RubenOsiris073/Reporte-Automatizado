# 📊 Sistema Empresarial de Análisis de Ventas v3.0

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Architecture](https://img.shields.io/badge/Architecture-Clean%20Architecture-green.svg)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
[![SOLID](https://img.shields.io/badge/Principles-SOLID-orange.svg)](https://en.wikipedia.org/wiki/SOLID)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](/)

Sistema profesional de análisis de datos de ventas con **arquitectura modular**, implementando **Clean Architecture** y principios **SOLID** con **reportes automáticos por email**.

## 🚀 Características Principales

### 📧 Reportes Automáticos por Email
- **Envío automático** de reportes por email con **templates HTML profesionales**
- **Análisis estadístico avanzado** con gráficos y métricas
- **Templates responsive** optimizados para email
- **Configuración simple** con variables de entorno

## ⚙️ Configuración Rápida

### 1. Clona el repositorio
```bash
git clone https://github.com/RubenOsiris073/testing.git
cd testing
```

### 2. Configura el entorno virtual
```bash
python -m venv env
source env/bin/activate  # En Linux/Mac
# o
env\Scripts\activate     # En Windows
```

### 3. Instala las dependencias
```bash
pip install -r requirements.txt
```

### 4. Configura las variables de entorno
```bash
cp .env.example .env
```

Edita el archivo `.env` con tus credenciales:
```env
# Configuración SMTP para Brevo
SMTP_SERVER=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USER=tu_usuario_smtp@smtp-brevo.com
SMTP_PASSWORD=tu_clave_smtp_aqui

# Configuración de email
FROM_EMAIL=tu_email@dominio.com
FROM_NAME=tu_nombre
TO_EMAIL=destinatario@dominio.com
```

### 5. Ejecuta el sistema
```bash
python run.py
```

## 🔒 Seguridad

Este proyecto utiliza variables de entorno para manejar credenciales sensibles. **NUNCA** hagas commit del archivo `.env` al repositorio.

## 🌟 Características Principales

### ✨ **Funcionalidades de Negocio**
- 📈 **Análisis estadístico avanzado** de datos de ventas
- 🔗 **Conexión automatizada** con Google Sheets
- 📧 **Envío automático** de reportes por email con **templates HTML profesionales**
- 🎨 **Templates HTML responsivos** y compatibles con múltiples clientes de email
- 🤖 **Análisis estratégico con IA** (Ollama/Qwen)
- 📊 **Generación de KPIs** y métricas de rendimiento
- 📉 **Análisis de tendencias temporales**
- 🔍 **Detección de anomalías** en ventas

### 🏗️ **Arquitectura Técnica**
- ✅ **Clean Architecture** con separación clara de responsabilidades
- ✅ **Principios SOLID** en todos los componentes
- ✅ **Patrón Repository** para acceso a datos
- ✅ **Service Layer** para lógica de negocio
- ✅ **Factory Pattern** para creación de objetos
- ✅ **Dependency Injection** e inversión de dependencias
- ✅ **Manejo centralizado de errores** con excepciones específicas
- ✅ **Logging estructurado** y monitoreo

## 🏁 Inicio Rápido

### 1. **Instalación**

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd analisis

# Crear y activar entorno virtual
python3 -m venv env
source env/bin/activate  # Linux/Mac
# o
env\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. **Configuración**

```bash
# Configurar credenciales de Google Sheets
cp credentials.json.example credentials.json
# Editar credentials.json con tus credenciales reales

# Configurar email (opcional, editar config/__init__.py)
# Las variables de ambiente tienen prioridad
export SMTP_SERVER="tu-servidor-smtp.com"
export SMTP_USER="tu-usuario@dominio.com"
export SMTP_PASSWORD="tu-password"
```

### 3. **Ejecución**

```bash
# Ejecución básica
python run.py

# Con hoja personalizada
python run.py "MiHojaVentas"

# Verificar configuración
python run.py --check-config

# Ver ayuda detallada
python run.py --help-detailed
```

## 📁 Arquitectura del Sistema

```
sistema_ventas/
├── 🔧 config/              # Configuración centralizada
│   └── __init__.py         # Settings y configuraciones
├── 🎯 core/                # Núcleo del dominio
│   ├── interfaces/         # Contratos/Interfaces (ABC)
│   │   ├── email_interface.py
│   │   ├── data_interface.py
│   │   └── sheets_interface.py
│   └── exceptions/         # Excepciones específicas del dominio
│       └── __init__.py
├── 🏢 services/            # Lógica de negocio (casos de uso)
│   ├── __init__.py         # EmailService
│   ├── sheets_service.py   # SheetsService
│   ├── data_analysis_service.py  # DataAnalysisService
│   └── html_template_service.py  # HTMLTemplateService
├── 🎨 templates/           # Templates HTML para emails
│   ├── email_report.html   # Template principal profesional
│   ├── email_report_simple.html  # Template compatible simplificado
│   └── email_report_compact.html # Template compacto rápido
├── 💾 repositories/        # Acceso a datos (futuro)
├── 📊 models/              # Modelos de datos y entidades
│   └── __init__.py         # SalesData, KPIMetrics, etc.
├── 🛠️ utils/               # Utilidades y helpers
│   └── __init__.py         # Logger, validators, decoradores
├── 🏭 factories/           # Creación de objetos (Factory Pattern)
│   └── __init__.py         # ServiceFactory
├── 🚀 main.py              # Orquestador principal
└── 📄 __init__.py          # Exports públicos
```

## 💡 Ejemplos de Uso

### **Uso Básico (Función Original)**

```python
from sistema_ventas import analisis_empresarial

# Análisis completo con una línea
resultado = analisis_empresarial("DB_sales")

if resultado and resultado['analisis_completado']:
    print("✅ Análisis completado exitosamente")
    print(f"📄 Reporte: {resultado['archivo_reporte']}")
```

### **Uso Avanzado (Nueva Arquitectura)**

```python
from sistema_ventas import SistemaVentasMain
from sistema_ventas.factories import get_complete_services

# Crear instancia del sistema
sistema = SistemaVentasMain()

# Ejecutar componentes individuales
sistema.inicializar_servicios()
sistema.cargar_datos_sheets("MiHojaPersonalizada")
resultados = sistema.ejecutar_analisis_estadistico()

# Acceso directo a servicios
servicios = get_complete_services()
email_service = servicios['email']
data_service = servicios['data_analysis']
```

### **Uso con Factory Pattern**

```python
from sistema_ventas.factories import ServiceFactory
from sistema_ventas.models import SalesData
from sistema_ventas.services.html_template_service import HTMLTemplateService

# Crear servicios específicos
email_service = ServiceFactory.create_email_service()
sheets_service = ServiceFactory.create_sheets_service()
data_service = ServiceFactory.create_data_analysis_service()
template_service = HTMLTemplateService()

# Usar servicios individualmente
if sheets_service.conectar_sheets("DB_sales"):
    df = sheets_service.cargar_datos()
    resumen = data_service.generar_resumen(df)
    # El email se envía automáticamente con template HTML profesional
    email_service.enviar_reporte_automatico(resumen)
```

## 🚀 Deployment en Railway

### **Deploy en la Nube**
Este proyecto está optimizado para deployment en [Railway](https://railway.app):

```bash
# 1. Commitea los cambios
git add .
git commit -m "Deploy to Railway"
git push origin main

# 2. Conecta en railway.app
# 3. Configura las variables de entorno
```

📖 **Guía completa**: Ver [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)

### **Variables de Entorno Requeridas**
```env
SMTP_SERVER=smtp-relay.brevo.com
SMTP_USER=tu_usuario_brevo
SMTP_PASSWORD=tu_password_brevo
FROM_EMAIL=tu_email@dominio.com
TO_EMAIL=destinatario@email.com
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
```

⚠️ **Importante**: Para `GOOGLE_CREDENTIALS_JSON`, copia el contenido completo de `credentials.json` como string JSON.

## ⚙️ Configuración Avanzada

### **Variables de Entorno**

```bash
# Email Configuration
export SMTP_SERVER="smtp-relay.brevo.com"
export SMTP_PORT="587"
export SMTP_USER="tu-usuario@smtp-brevo.com"
export SMTP_PASSWORD="tu-password"
export FROM_EMAIL="tu-email@dominio.com"
export TO_EMAIL="destinatario@dominio.com"

# HTML Templates Configuration
export USE_HTML_TEMPLATES="true"
export DEFAULT_EMAIL_TEMPLATE="email_report.html"
export EMAIL_FORMAT="multipart"  # multipart, html, plain

# Google Sheets
export GOOGLE_CREDENTIALS_FILE="credentials.json"
export GOOGLE_SHEET_ID="tu-sheet-id"

# Logging
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### **Configuración Programática**

```python
from sistema_ventas.config import settings

# Modificar configuración en tiempo de ejecución
# Configuración programática
settings.email.DEFAULT_TO_EMAIL = "nuevo@destinatario.com"
settings.email.USE_HTML_TEMPLATES = True
settings.email.DEFAULT_TEMPLATE = "email_report_compact.html"
settings.data_analysis.ANOMALY_THRESHOLD = 1.5

# Validar configuración
validacion = settings.validate_all()
print(f"Configuración válida: {validacion}")
```

## 🔧 Desarrollo y Extensión

### **Agregar Nuevo Servicio**

1. **Crear Interface**
```python
# core/interfaces/mi_interface.py
from abc import ABC, abstractmethod

class MiServiceInterface(ABC):
    @abstractmethod
    def mi_metodo(self) -> bool:
        pass
```

2. **Implementar Servicio**
```python
# services/mi_service.py
from ..core.interfaces.mi_interface import MiServiceInterface

class MiService(MiServiceInterface):
    def mi_metodo(self) -> bool:
        # Implementación
        return True
```

3. **Agregar al Factory**
```python
# factories/__init__.py
def create_mi_service(self) -> MiServiceInterface:
    return MiService()
```

### **Crear Nuevas Excepciones**

```python
# core/exceptions/__init__.py
class MiServiceError(SistemaVentasError):
    """Error específico de mi servicio."""
    pass
```

## 🧪 Testing

```python
import unittest
from sistema_ventas.factories import ServiceFactory
from sistema_ventas.core.exceptions import EmailServiceError

class TestEmailService(unittest.TestCase):
    def setUp(self):
        self.email_service = ServiceFactory.create_email_service()
    
    def test_configuracion_valida(self):
        self.assertTrue(self.email_service.validar_configuracion())
    
    def test_conexion_smtp(self):
        # Test connection
        pass
```

## 📊 Monitoreo y Logging

### **Logs del Sistema**
```bash
# Ver logs en tiempo real
tail -f logs/sistema_ventas.log

# Ver solo errores
tail -f logs/errores.log

# Buscar en logs
grep "ERROR" logs/sistema_ventas.log
```

### **Métricas de Rendimiento**
```python
from sistema_ventas.utils import log_execution_time

@log_execution_time
def mi_funcion_lenta():
    # Tu código aquí
    pass
```

## 🚨 Solución de Problemas

### **Errores Comunes**

| Error | Causa | Solución |
|-------|-------|----------|
| `SheetsConnectionError` | credentials.json inválido | Verificar credenciales de Google Cloud |
| `EmailConnectionError` | Configuración SMTP incorrecta | Verificar servidor, puerto y credenciales |
| `DataAnalysisError` | Datos vacíos o mal formateados | Verificar estructura de Google Sheets |
| `ImportError` | Dependencias faltantes | Ejecutar `pip install -r requirements.txt` |

### **Diagnóstico**

```bash
# Verificar estado del sistema
python -c "from sistema_ventas import check_dependencies; print(check_dependencies())"

# Verificar configuración
python run.py --check-config

# Logs detallados
python run.py --verbose "DB_sales"
```

## 🔄 Migración desde Versión Anterior

### **Código Anterior (Monolítico)**
```python
# ANTES: Todo en un archivo
def analisis_empresarial():
    # 494 líneas de código mezclado
    pass
```

### **Nuevo Código (Modular)**
```python
# DESPUÉS: Arquitectura limpia
from sistema_ventas import analisis_empresarial  # Mantiene compatibilidad
# O usar la nueva arquitectura
from sistema_ventas import SistemaVentasMain
```

**✅ La función `analisis_empresarial()` mantiene total compatibilidad hacia atrás.**

## 📊 Métricas y KPIs

El sistema genera automáticamente:

- 💰 **Métricas Financieras**: Ventas totales, ticket promedio, márgenes
- 📊 **KPIs Operacionales**: Número de transacciones, productos top, clientes activos
- 📈 **Análisis Temporal**: Tendencias mensuales, crecimiento, estacionalidad
- 🔍 **Detección de Anomalías**: Ventas atípicas, productos con bajo rendimiento
- 🎯 **Predicciones**: Proyecciones de ventas futuras (básico)

## 🎨 Templates HTML Profesionales

### **Características de Templates**
- ✅ **Diseño Responsivo**: Compatible con móviles y escritorio
- ✅ **Multi-cliente**: Funciona en Gmail, Outlook, Apple Mail, etc.
- ✅ **Profesional**: Diseño empresarial moderno con gradientes y colores
- ✅ **Fallback**: Texto plano automático para clientes incompatibles

### **Templates Disponibles**

| Template | Descripción | Tamaño | Uso Recomendado |
|----------|-------------|---------|-----------------|
| `email_report.html` | Template principal completo | ~15KB | Reportes detallados ejecutivos |
| `email_report_simple.html` | Template compatible básico | ~8KB | Máxima compatibilidad |
| `email_report_compact.html` | Template compacto rápido | ~5KB | Reportes diarios/resúmenes |

### **Uso de Templates**

```python
from sistema_ventas.services.html_template_service import HTMLTemplateService

# Crear servicio de templates
template_service = HTMLTemplateService()

# Renderizar con template específico
html_content = template_service.render_email_report(
    datos_resumen, 
    template_name="email_report_compact.html"
)

# Listar templates disponibles
templates = template_service.list_available_templates()
print(f"Templates: {templates}")

# Validar template
validation = template_service.validate_template("email_report.html")
print(f"Válido: {validation['is_valid']}")
```

### **Testing de Templates**

```bash
# Probar todos los templates
python test_templates.py

# Probar template específico
python test_templates.py --template compact

# Generar email de demostración
python test_templates.py --demo

# Solo validar templates
python test_templates.py --validate
```

## 🤝 Contribución

### **Estándares de Código**
- Seguir principios **SOLID**
- Documentar con **docstrings**
- Tests unitarios para nuevas funcionalidades
- Tipo hints en Python
- Logging estructurado

### **Pull Requests**
1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'Agregar nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🙏 Reconocimientos

- **Clean Architecture** por Robert C. Martin
- **SOLID Principles** para diseño de software
- **Google Sheets API** para integración de datos
- **Ollama/Qwen** para análisis con IA

---

## 📞 Soporte

Para soporte técnico:
- 📧 Email: [tu-email@dominio.com]
- 📋 Issues: [GitHub Issues]
- 📖 Documentación: Ver `/docs` (futuro)

---

**Sistema Empresarial de Análisis de Ventas v2.0** - Desarrollado con ❤️ y principios de **Clean Architecture**