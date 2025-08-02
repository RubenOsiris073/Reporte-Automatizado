# 🚀 GUÍA DE DEPLOYMENT EN RAILWAY

## 📋 Pasos para subir a Railway

### 1. **Preparar el proyecto**
```bash
# Asegúrate de que el código esté limpio
git add .
git commit -m "Preparar para deployment en Railway"
git push origin main
```

### 2. **Crear proyecto en Railway**
1. Ve a [railway.app](https://railway.app)
2. Conecta tu cuenta de GitHub
3. Selecciona "Deploy from GitHub repo"
4. Elige tu repositorio

### 3. **Configurar Variables de Entorno**
En el panel de Railway ve a **Settings > Environment** y agrega:

```env
# SMTP Configuration
SMTP_SERVER=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USER=tu_usuario_brevo
SMTP_PASSWORD=tu_password_brevo

# Email Configuration  
FROM_EMAIL=tu_email@dominio.com
FROM_NAME=tu_empresa
TO_EMAIL=destinatario@email.com

# Project Configuration
PROJECT_NAME=Análisis de Ventas
VERSION=3.0.0
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=INFO

# Google Sheets Credentials (IMPORTANTE)
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"tu-project-id",...}
```

### 4. **Variable GOOGLE_CREDENTIALS_JSON**
⚠️ **MUY IMPORTANTE**: Para esta variable debes:

1. Abrir tu archivo `credentials.json` local
2. Copiar TODO el contenido (es un JSON completo)
3. Pegarlo como valor de `GOOGLE_CREDENTIALS_JSON` en Railway
4. Asegúrate de que esté en UNA SOLA LÍNEA

**Ejemplo de formato correcto:**
```json
{"type":"service_account","project_id":"nomadic-groove-431902-n2","private_key_id":"506e105f...","private_key":"-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCkvq8CeVZQMWIZ\n..."}
```

### 5. **Verificar deployment**
- Railway detectará automáticamente que es un proyecto Python
- Instalará las dependencias de `requirements.txt`
- Ejecutará `python run.py`

### 6. **Logs y debugging**
- Ve a la pestaña **Logs** para ver la ejecución
- Si hay errores, revisa que todas las variables estén correctas

## 🔧 Troubleshooting

### Error de credenciales de Google
- Verifica que `GOOGLE_CREDENTIALS_JSON` esté completo
- Asegúrate de que no tenga saltos de línea extra

### Error de SMTP
- Confirma que las credenciales de Brevo sean correctas
- Verifica que el email origen esté verificado en Brevo

### El script no ejecuta
- Railway usa el puerto asignado automáticamente
- El script debe ejecutarse y terminar (no es un servidor web)

## 📊 Funcionamiento en Railway

El script se ejecutará cada vez que:
1. Hagas un nuevo deployment
2. Railway reinicie el contenedor
3. Manualmente desde el panel

Para ejecución programada, considera usar Railway Cron Jobs o GitHub Actions.

## 🔒 Seguridad

✅ **Qué SÍ hacer:**
- Usar variables de entorno en Railway
- Mantener credentials.json solo local
- Verificar que .gitignore excluya archivos sensibles

❌ **Qué NO hacer:**
- Subir .env al repositorio
- Hardcodear credenciales en el código
- Compartir el valor de GOOGLE_CREDENTIALS_JSON
