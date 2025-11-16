# 🔧 Configuración de Google Cloud Vision API

Esta guía te ayudará a configurar Google Cloud Vision API para el proyecto.

## 📋 Prerrequisitos

- Cuenta de Google Cloud (puedes usar la capa gratuita)
- Proyecto creado en Google Cloud Console

---

## 🚀 Paso 1: Habilitar Google Cloud Vision API

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Selecciona tu proyecto o crea uno nuevo
3. Ve a **APIs & Services** > **Library**
4. Busca "Cloud Vision API"
5. Haz clic en **Enable** (si ya lo hiciste, verás "Manage")

---

## 🔑 Paso 2: Crear Service Account

1. Ve a **IAM & Admin** > **Service Accounts**
   - URL directa: https://console.cloud.google.com/iam-admin/serviceaccounts

2. Haz clic en **+ CREATE SERVICE ACCOUNT**

3. Configura los detalles:
   ```
   Service account name: kush-image-analyzer
   Service account ID: kush-image-analyzer (se genera automáticamente)
   Description: Service account for Kush Image Analyzer API
   ```

4. Haz clic en **CREATE AND CONTINUE**

5. Asigna roles (Grant this service account access to project):
   ```
   Role: Cloud Vision AI Service Agent
   ```

   O alternativamente:
   ```
   Role: Owner (para desarrollo, más permisivo)
   ```

6. Haz clic en **CONTINUE** y luego **DONE**

---

## 📥 Paso 3: Descargar Credenciales JSON

1. En la lista de Service Accounts, encuentra la que acabas de crear
2. Haz clic en los **tres puntos** (⋮) a la derecha > **Manage keys**
3. Haz clic en **ADD KEY** > **Create new key**
4. Selecciona **JSON** como tipo de clave
5. Haz clic en **CREATE**
6. Se descargará un archivo JSON automáticamente

**⚠️ IMPORTANTE:** Este archivo contiene credenciales sensibles. NO lo subas a Git.

---

## 📁 Paso 4: Configurar el Proyecto

### Opción A: Usando archivo de credenciales (Recomendado para desarrollo local)

1. **Renombra el archivo descargado** a algo más simple:
   ```bash
   mv ~/Downloads/kush-image-analyzer-*.json google-credentials.json
   ```

2. **Mueve el archivo al directorio del proyecto:**
   ```bash
   # Opción 1: En la raíz del proyecto (ignorado por .gitignore)
   mv google-credentials.json /home/jhonmo/apps/retos/kush_be_api_image_analizer/

   # Opción 2: En una carpeta dedicada
   mkdir -p /home/jhonmo/apps/retos/kush_be_api_image_analizer/credentials
   mv google-credentials.json /home/jhonmo/apps/retos/kush_be_api_image_analizer/credentials/
   ```

3. **Actualiza tu archivo `.env`:**
   ```bash
   # Opción 1: Archivo en la raíz
   GOOGLE_APPLICATION_CREDENTIALS=/home/jhonmo/apps/retos/kush_be_api_image_analizer/google-credentials.json

   # Opción 2: Archivo en carpeta credentials
   GOOGLE_APPLICATION_CREDENTIALS=/home/jhonmo/apps/retos/kush_be_api_image_analizer/credentials/google-credentials.json

   # Para Docker (ruta relativa)
   GOOGLE_APPLICATION_CREDENTIALS=/app/google-credentials.json
   ```

4. **Verifica que `.gitignore` ignore el archivo:**
   ```bash
   # Ya está configurado en .gitignore:
   # *.json (ignora todos los JSON excepto los especificados)
   # !template.yaml
   # !pyproject.toml
   ```

### Opción B: Usando variable de entorno (Alternativa)

En lugar de usar un archivo, puedes exportar el contenido como variable de entorno:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/ruta/al/archivo.json"
```

---

## 🧪 Paso 5: Verificar la Configuración

Una vez configurado el proyecto (después de implementar el código), puedes probar la conexión:

```bash
# Dentro del proyecto
poetry run python -c "
from google.cloud import vision
import os

# Verificar que la variable de entorno está configurada
print(f'Credentials path: {os.getenv(\"GOOGLE_APPLICATION_CREDENTIALS\")}')

# Intentar crear el cliente
try:
    client = vision.ImageAnnotatorClient()
    print('✅ Google Cloud Vision client created successfully!')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

---

## 💰 Capa Gratuita de Google Cloud Vision

Google Cloud Vision ofrece:
- **1,000 unidades gratis por mes** para Label Detection
- Después: $1.50 por cada 1,000 imágenes

Más info: https://cloud.google.com/vision/pricing

---

## 🔒 Seguridad

### ✅ Buenas Prácticas:

1. **NO commitear credenciales:**
   ```bash
   # Verificar que no están en git
   git status
   # No debería aparecer google-credentials.json
   ```

2. **Usar diferentes Service Accounts por entorno:**
   - Desarrollo: `kush-image-analyzer-dev`
   - Producción: `kush-image-analyzer-prod`

3. **Rotar credenciales periódicamente:**
   - Cada 90 días en producción
   - Crear nueva key, actualizar, eliminar la antigua

4. **Para producción (AWS Lambda):**
   - Usar AWS Secrets Manager para guardar el JSON
   - O usar Workload Identity Federation (más seguro)

---

## 🐳 Configuración para Docker

En `docker-compose.yml`, montaremos el archivo de credenciales:

```yaml
services:
  api:
    volumes:
      - ./google-credentials.json:/app/google-credentials.json:ro
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/app/google-credentials.json
```

---

## 🚨 Troubleshooting

### Error: "Could not automatically determine credentials"

**Solución:**
```bash
# Verificar que la variable de entorno está configurada
echo $GOOGLE_APPLICATION_CREDENTIALS

# Verificar que el archivo existe
ls -la $GOOGLE_APPLICATION_CREDENTIALS

# Verificar permisos
chmod 600 google-credentials.json
```

### Error: "Permission denied"

**Solución:**
1. Ve a IAM & Admin en Google Cloud Console
2. Verifica que el Service Account tiene el rol "Cloud Vision API User" o "Owner"
3. Puede tardar unos minutos en propagarse

### Error: "API not enabled"

**Solución:**
```bash
# Habilitar la API desde la consola
gcloud services enable vision.googleapis.com --project=YOUR_PROJECT_ID
```

---

## 📚 Referencias

- [Google Cloud Vision Documentation](https://cloud.google.com/vision/docs)
- [Python Client Library](https://cloud.google.com/vision/docs/setup#client_libraries)
- [Pricing](https://cloud.google.com/vision/pricing)
- [Quotas & Limits](https://cloud.google.com/vision/quotas)

---

**¡Listo!** Una vez hayas completado estos pasos, podrás usar Google Cloud Vision API en el proyecto.