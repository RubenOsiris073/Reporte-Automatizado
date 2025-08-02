import os
import json
import tempfile
from pathlib import Path

class CredentialsManager:
    """Maneja las credenciales de Google Sheets para diferentes entornos"""
    
    @staticmethod
    def get_credentials_path():
        """
        Obtiene la ruta de las credenciales según el entorno:
        - Desarrollo: usar credentials.json local O variable de entorno
        - Producción: crear archivo temporal desde variable de entorno
        """
        # Verificar si estamos en Railway (producción)
        if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('ENVIRONMENT') == 'production':
            return CredentialsManager._create_temp_credentials()
        else:
            # Entorno local - preferir archivo credentials.json, luego variable de entorno
            credentials_file = Path(__file__).parent / 'credentials.json'
            if credentials_file.exists():
                return str(credentials_file)
            elif os.getenv('GOOGLE_CREDENTIALS_JSON'):
                # Si existe la variable de entorno, usarla (para desarrollo con .env)
                return CredentialsManager._create_temp_credentials()
            else:
                raise FileNotFoundError(
                    "No se encontró credentials.json ni GOOGLE_CREDENTIALS_JSON. "
                    "Para desarrollo local, coloca el archivo credentials.json en la raíz del proyecto "
                    "o configura GOOGLE_CREDENTIALS_JSON en el archivo .env"
                )
    
    @staticmethod
    def _create_temp_credentials():
        """Crea un archivo temporal de credenciales desde variable de entorno"""
        credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        
        if not credentials_json:
            raise ValueError(
                "Variable de entorno GOOGLE_CREDENTIALS_JSON no encontrada. "
                "Configúrala en Railway con el contenido completo del archivo credentials.json"
            )
        
        try:
            # Validar que sea JSON válido
            credentials_data = json.loads(credentials_json)
            
            # Crear archivo temporal
            temp_file = tempfile.NamedTemporaryFile(
                mode='w', 
                suffix='.json', 
                delete=False,
                prefix='gcp_credentials_'
            )
            
            json.dump(credentials_data, temp_file, indent=2)
            temp_file.close()
            
            return temp_file.name
            
        except json.JSONDecodeError as e:
            raise ValueError(f"GOOGLE_CREDENTIALS_JSON no es un JSON válido: {e}")
        except Exception as e:
            raise RuntimeError(f"Error creando credenciales temporales: {e}")
    
    @staticmethod
    def cleanup_temp_file(file_path):
        """Limpia el archivo temporal de credenciales"""
        try:
            if file_path and os.path.exists(file_path) and 'temp' in file_path:
                os.unlink(file_path)
        except Exception:
            pass  # Ignorar errores de limpieza
