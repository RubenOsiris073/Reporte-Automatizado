"""
Factory Pattern para servicios del sistema de ventas.
Centraliza la creación de instancias de servicios con sus dependencias.
"""

from typing import Optional, Dict, Any
from ..services import EmailService
from ..services.sheets_service import SheetsService
from ..services.data_analysis_service import DataAnalysisService
from ..core.interfaces.email_interface import EmailServiceInterface
from ..core.interfaces.sheets_interface import SheetsServiceInterface
from ..core.interfaces.data_interface import DataServiceInterface
from ..config import settings
from ..utils import logger


class ServiceFactory:
    """
    Factory para crear instancias de servicios del sistema.

    Implementa el patrón Factory para centralizar la creación de servicios
    y gestionar sus dependencias de forma consistente.
    """

    _instances: Dict[str, Any] = {}
    _singleton_services = ['email_service', 'sheets_service']

    @classmethod
    def create_email_service(
        cls,
        config: Optional[Any] = None,
        use_singleton: bool = True
    ) -> EmailServiceInterface:
        """
        Crea una instancia del servicio de email.

        Args:
            config: Configuración personalizada opcional
            use_singleton: Si usar patrón singleton

        Returns:
            EmailServiceInterface: Instancia del servicio de email
        """
        service_key = 'email_service'

        if use_singleton and service_key in cls._instances:
            logger.debug("Retornando instancia singleton de EmailService")
            return cls._instances[service_key]

        try:
            logger.info("Creando nueva instancia de EmailService")
            service = EmailService(config=config)

            if use_singleton:
                cls._instances[service_key] = service

            logger.info("EmailService creado exitosamente")
            return service

        except Exception as e:
            logger.error(f"Error creando EmailService: {str(e)}")
            raise

    @classmethod
    def create_sheets_service(
        cls,
        config: Optional[Any] = None,
        use_singleton: bool = True
    ) -> SheetsServiceInterface:
        """
        Crea una instancia del servicio de Google Sheets.

        Args:
            config: Configuración personalizada opcional
            use_singleton: Si usar patrón singleton

        Returns:
            SheetsServiceInterface: Instancia del servicio de sheets
        """
        service_key = 'sheets_service'

        if use_singleton and service_key in cls._instances:
            logger.debug("Retornando instancia singleton de SheetsService")
            return cls._instances[service_key]

        try:
            logger.info("Creando nueva instancia de SheetsService")
            service = SheetsService(config=config)

            if use_singleton:
                cls._instances[service_key] = service

            logger.info("SheetsService creado exitosamente")
            return service

        except Exception as e:
            logger.error(f"Error creando SheetsService: {str(e)}")
            raise

    @classmethod
    def create_data_analysis_service(
        cls,
        config: Optional[Any] = None,
        use_singleton: bool = False
    ) -> DataServiceInterface:
        """
        Crea una instancia del servicio de análisis de datos.

        Args:
            config: Configuración personalizada opcional
            use_singleton: Si usar patrón singleton (por defecto False)

        Returns:
            DataServiceInterface: Instancia del servicio de análisis
        """
        service_key = 'data_analysis_service'

        if use_singleton and service_key in cls._instances:
            logger.debug("Retornando instancia singleton de DataAnalysisService")
            return cls._instances[service_key]

        try:
            logger.info("Creando nueva instancia de DataAnalysisService")
            service = DataAnalysisService(config=config)

            if use_singleton:
                cls._instances[service_key] = service

            logger.info("DataAnalysisService creado exitosamente")
            return service

        except Exception as e:
            logger.error(f"Error creando DataAnalysisService: {str(e)}")
            raise

    @classmethod
    def create_complete_service_stack(cls) -> Dict[str, Any]:
        """
        Crea una pila completa de servicios para el sistema.

        Returns:
            Dict[str, Any]: Diccionario con todos los servicios instanciados
        """
        try:
            logger.info("Creando pila completa de servicios")

            services = {
                'email': cls.create_email_service(),
                'sheets': cls.create_sheets_service(),
                'data_analysis': cls.create_data_analysis_service()
            }

            logger.info("Pila completa de servicios creada exitosamente")
            return services

        except Exception as e:
            logger.error(f"Error creando pila de servicios: {str(e)}")
            raise

    @classmethod
    def get_service_instance(cls, service_name: str) -> Optional[Any]:
        """
        Obtiene una instancia de servicio existente.

        Args:
            service_name: Nombre del servicio

        Returns:
            Optional[Any]: Instancia del servicio o None
        """
        return cls._instances.get(service_name)

    @classmethod
    def clear_instances(cls):
        """
        Limpia todas las instancias singleton.
        Útil para testing o reconfiguración.
        """
        logger.info("Limpiando instancias singleton de servicios")
        cls._instances.clear()

    @classmethod
    def get_service_status(cls) -> Dict[str, Any]:
        """
        Obtiene el estado de los servicios instanciados.

        Returns:
            Dict[str, Any]: Estado de los servicios
        """
        status = {
            'total_instances': len(cls._instances),
            'active_services': list(cls._instances.keys()),
            'singleton_services': cls._singleton_services,
            'configuration_valid': settings.validate_all()
        }

        # Verificar conectividad de servicios activos
        for service_name, service in cls._instances.items():
            try:
                if hasattr(service, 'probar_conexion'):
                    status[f'{service_name}_connected'] = service.probar_conexion()
                elif hasattr(service, 'probar_conectividad'):
                    status[f'{service_name}_connected'] = service.probar_conectividad()
                else:
                    status[f'{service_name}_connected'] = True  # Asumir conectado si no hay método
            except Exception as e:
                logger.warning(f"Error verificando conectividad de {service_name}: {str(e)}")
                status[f'{service_name}_connected'] = False

        return status


class BusinessServiceFactory:
    """
    Factory especializado para servicios de negocio.

    Implementa patrones específicos para la lógica de negocio del sistema de ventas.
    """

    @staticmethod
    def create_sales_analysis_pipeline():
        """
        Crea un pipeline completo para análisis de ventas.

        Returns:
            Dict[str, Any]: Pipeline de servicios configurado
        """
        try:
            logger.info("Creando pipeline de análisis de ventas")

            # Crear servicios necesarios
            sheets_service = ServiceFactory.create_sheets_service()
            data_service = ServiceFactory.create_data_analysis_service()
            email_service = ServiceFactory.create_email_service()

            pipeline = {
                'data_source': sheets_service,
                'analyzer': data_service,
                'reporter': email_service,
                'pipeline_id': f"sales_analysis_{settings.base.PROJECT_NAME}",
                'created_at': settings.base.PROJECT_NAME
            }

            logger.info("Pipeline de análisis de ventas creado exitosamente")
            return pipeline

        except Exception as e:
            logger.error(f"Error creando pipeline: {str(e)}")
            raise

    @staticmethod
    def create_reporting_service_bundle():
        """
        Crea un bundle de servicios para reportes.

        Returns:
            Dict[str, Any]: Bundle de servicios para reportes
        """
        try:
            logger.info("Creando bundle de servicios de reportes")

            bundle = {
                'data_analyzer': ServiceFactory.create_data_analysis_service(),
                'email_sender': ServiceFactory.create_email_service(),
                'template_engine': None,  # Podrá expandirse en el futuro
                'export_formats': settings.data_analysis.EXPORT_FORMATS
            }

            logger.info("Bundle de servicios de reportes creado exitosamente")
            return bundle

        except Exception as e:
            logger.error(f"Error creando bundle de reportes: {str(e)}")
            raise


class ConfigurableServiceFactory:
    """
    Factory que permite configuraciones personalizadas avanzadas.
    """

    @staticmethod
    def create_service_with_custom_config(
        service_type: str,
        custom_config: Dict[str, Any]
    ) -> Any:
        """
        Crea un servicio con configuración personalizada.

        Args:
            service_type: Tipo de servicio ('email', 'sheets', 'data_analysis')
            custom_config: Configuración personalizada

        Returns:
            Any: Instancia del servicio configurado

        Raises:
            ValueError: Si el tipo de servicio no es válido
        """
        service_map = {
            'email': ServiceFactory.create_email_service,
            'sheets': ServiceFactory.create_sheets_service,
            'data_analysis': ServiceFactory.create_data_analysis_service
        }

        if service_type not in service_map:
            raise ValueError(f"Tipo de servicio no válido: {service_type}")

        try:
            logger.info(f"Creando {service_type} con configuración personalizada")

            # Crear configuración temporal
            # Nota: Esto requeriría implementar clases de configuración más flexibles
            # Por ahora, pasamos la configuración directamente

            service = service_map[service_type](config=custom_config, use_singleton=False)

            logger.info(f"{service_type} con configuración personalizada creado exitosamente")
            return service

        except Exception as e:
            logger.error(f"Error creando {service_type} personalizado: {str(e)}")
            raise


# Funciones de conveniencia para acceso rápido
def get_email_service() -> EmailServiceInterface:
    """Función de conveniencia para obtener servicio de email."""
    return ServiceFactory.create_email_service()


def get_sheets_service() -> SheetsServiceInterface:
    """Función de conveniencia para obtener servicio de sheets."""
    return ServiceFactory.create_sheets_service()


def get_data_analysis_service() -> DataServiceInterface:
    """Función de conveniencia para obtener servicio de análisis."""
    return ServiceFactory.create_data_analysis_service()


def get_complete_services() -> Dict[str, Any]:
    """Función de conveniencia para obtener todos los servicios."""
    return ServiceFactory.create_complete_service_stack()


# Exportar clases y funciones principales
__all__ = [
    'ServiceFactory',
    'BusinessServiceFactory',
    'ConfigurableServiceFactory',
    'get_email_service',
    'get_sheets_service',
    'get_data_analysis_service',
    'get_complete_services'
]
