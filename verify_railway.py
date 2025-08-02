#!/usr/bin/env python3
"""
Script de verificación para deployment en Railway
Verifica que todas las variables de entorno estén configuradas
"""

import os
import json
import sys
from pathlib import Path

# Cargar variables de entorno para entorno local
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def verificar_variables_entorno():
    """Verifica que todas las variables de entorno necesarias estén configuradas"""
    
    variables_requeridas = [
        'SMTP_SERVER',
        'SMTP_PORT', 
        'SMTP_USER',
        'SMTP_PASSWORD',
        'FROM_EMAIL',
        'TO_EMAIL',
        'GOOGLE_CREDENTIALS_JSON'
    ]
    
    variables_faltantes = []
    
    print("🔍 Verificando variables de entorno...")
    
    for var in variables_requeridas:
        valor = os.getenv(var)
        if not valor:
            variables_faltantes.append(var)
            print(f"❌ {var}: NO CONFIGURADA")
        else:
            # Ocultar valores sensibles
            if 'PASSWORD' in var or 'CREDENTIALS' in var:
                print(f"✅ {var}: [OCULTO]")
            else:
                print(f"✅ {var}: {valor}")
    
    return variables_faltantes

def verificar_credenciales_google():
    """Verifica que las credenciales de Google sean válidas"""
    
    print("\n🔍 Verificando credenciales de Google Sheets...")
    
    credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    
    if not credentials_json:
        print("❌ GOOGLE_CREDENTIALS_JSON no configurada")
        return False
    
    try:
        credentials_data = json.loads(credentials_json)
        
        campos_requeridos = [
            'type', 'project_id', 'private_key_id', 
            'private_key', 'client_email', 'client_id'
        ]
        
        for campo in campos_requeridos:
            if campo not in credentials_data:
                print(f"❌ Campo faltante en credenciales: {campo}")
                return False
        
        print("✅ Credenciales de Google válidas")
        print(f"✅ Proyecto: {credentials_data.get('project_id')}")
        print(f"✅ Email del servicio: {credentials_data.get('client_email')}")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ GOOGLE_CREDENTIALS_JSON no es un JSON válido")
        return False
    except Exception as e:
        print(f"❌ Error verificando credenciales: {e}")
        return False

def verificar_archivos():
    """Verifica que los archivos necesarios estén presentes"""
    
    print("\n🔍 Verificando archivos del proyecto...")
    
    archivos_requeridos = [
        'requirements.txt',
        'run.py',
        'sistema_ventas_profesional.py',
        'credentials_manager.py'
    ]
    
    archivos_faltantes = []
    
    for archivo in archivos_requeridos:
        if Path(archivo).exists():
            print(f"✅ {archivo}")
        else:
            archivos_faltantes.append(archivo)
            print(f"❌ {archivo}: NO ENCONTRADO")
    
    return archivos_faltantes

def main():
    """Función principal de verificación"""
    
    print("🚀 VERIFICACIÓN DE DEPLOYMENT PARA RAILWAY")
    print("=" * 50)
    
    # Verificar si estamos en Railway
    if os.getenv('RAILWAY_ENVIRONMENT'):
        print("🎯 Ejecutándose en Railway")
    else:
        print("🏠 Ejecutándose en entorno local")
    
    # Verificaciones
    variables_faltantes = verificar_variables_entorno()
    archivos_faltantes = verificar_archivos()
    credenciales_validas = verificar_credenciales_google()
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 50)
    
    if variables_faltantes:
        print(f"❌ Variables faltantes: {', '.join(variables_faltantes)}")
    else:
        print("✅ Todas las variables de entorno configuradas")
    
    if archivos_faltantes:
        print(f"❌ Archivos faltantes: {', '.join(archivos_faltantes)}")
    else:
        print("✅ Todos los archivos presentes")
    
    if credenciales_validas:
        print("✅ Credenciales de Google válidas")
    else:
        print("❌ Credenciales de Google inválidas")
    
    # Resultado final
    if not variables_faltantes and not archivos_faltantes and credenciales_validas:
        print("\n🎉 ¡VERIFICACIÓN EXITOSA! El proyecto está listo para Railway")
        return 0
    else:
        print("\n⚠️  VERIFICACIÓN FALLIDA. Corrige los errores antes del deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())
