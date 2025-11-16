# Guía de Pruebas Locales - Kush Image Analyzer API

Esta guía te ayudará a probar la API completa en tu entorno local.

## 📋 Pre-requisitos

1. **Docker y Docker Compose instalados**
2. **Poetry instalado** (`pip install poetry`)
3. **Credenciales de Google Cloud Vision** configuradas (ver `GOOGLE_CLOUD_SETUP.md`)
4. **Python 3.11+** instalado

## 🚀 Configuración Inicial

### 1. Instalar Dependencias

```bash
poetry install
```

### 2. Configurar Variables de Entorno

Asegúrate de tener tu archivo `.env` configurado:

```bash
# Application
APP_NAME=Kush Image Analyzer
ENVIRONMENT=development
DEBUG=true

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS DynamoDB (Local)
AWS_REGION=us-east-1
DYNAMODB_ENDPOINT_URL=http://localhost:8000
DYNAMODB_USERS_TABLE=kush-users-dev

# Google Cloud Vision
GOOGLE_APPLICATION_CREDENTIALS=./credentials/google-cloud-vision.json

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 3. Configurar Credenciales de Google Cloud Vision

Sigue las instrucciones en `GOOGLE_CLOUD_SETUP.md` para:
1. Habilitar Google Cloud Vision API
2. Crear una Service Account
3. Descargar el archivo JSON de credenciales
4. Colocar el archivo en `./credentials/google-cloud-vision.json`

### 4. Iniciar DynamoDB Local

```bash
docker-compose up -d dynamodb-local
```

Verifica que esté corriendo:
```bash
docker ps
```

Deberías ver el contenedor `dynamodb-local` en la lista.

### 5. Crear Tablas en DynamoDB

```bash
poetry run python scripts/create_tables.py
```

Deberías ver:
```
🚀 Creating DynamoDB tables...
📍 Region: us-east-1
📍 Endpoint: http://localhost:8000
📍 Table: kush-users-dev

✅ Table 'kush-users-dev' created successfully!
✅ All tables created successfully!
```

### 6. Iniciar el Servidor FastAPI

```bash
poetry run uvicorn app.main:app --reload --port 8080
```

El servidor estará disponible en: `http://localhost:8080`

## 🧪 Probar los Endpoints

### 1. Health Check

Verifica que la API esté funcionando:

```bash
curl http://localhost:8080/
```

Respuesta esperada:
```json
{
  "message": "Kush Image Analyzer API",
  "version": "1.0.0",
  "docs": "/docs",
  "v1": "/api/v1"
}
```

Prueba el health check de v1:
```bash
curl http://localhost:8080/api/v1/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-15T..."
}
```

Prueba el readiness check (verifica DynamoDB):
```bash
curl http://localhost:8080/api/v1/ready
```

Respuesta esperada:
```json
{
  "status": "ready",
  "services": {
    "database": "connected"
  },
  "timestamp": "2025-11-15T..."
}
```

### 2. Registro de Usuario

Registra un nuevo usuario:

```bash
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'
```

Respuesta esperada:
```json
{
  "email": "test@example.com",
  "is_active": true,
  "created_at": "2025-11-15T..."
}
```

### 3. Login y Obtener Token

Inicia sesión para obtener el JWT token:

```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'
```

Respuesta esperada:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**¡IMPORTANTE!** Guarda el `access_token` para usarlo en las siguientes peticiones.

### 4. Obtener Información del Usuario Actual

Verifica el token obteniendo la información del usuario:

```bash
curl http://localhost:8080/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

Reemplaza `YOUR_ACCESS_TOKEN_HERE` con el token obtenido en el paso anterior.

Respuesta esperada:
```json
{
  "email": "test@example.com",
  "is_active": true,
  "created_at": "2025-11-15T..."
}
```

### 5. Analizar una Imagen

Este es el endpoint principal. Necesitas una imagen para probarlo.

#### Opción A: Descargar una imagen de prueba

```bash
curl -o test-image.jpg https://images.unsplash.com/photo-1517849845537-4d257902454a
```

#### Opción B: Usar una imagen existente

Usa cualquier imagen JPG/PNG que tengas en tu computadora.

#### Hacer la petición de análisis

```bash
curl -X POST http://localhost:8080/api/v1/analyze \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -F "file=@test-image.jpg"
```

Respuesta esperada:
```json
{
  "tags": [
    {
      "label": "Dog",
      "confidence": 0.98
    },
    {
      "label": "Mammal",
      "confidence": 0.96
    },
    {
      "label": "Pet",
      "confidence": 0.94
    }
  ]
}
```

## 🌐 Usando la Documentación Interactiva (Swagger)

FastAPI incluye documentación interactiva automática. Abre tu navegador en:

```
http://localhost:8080/docs
```

Aquí puedes:
1. Ver todos los endpoints disponibles
2. Probar cada endpoint directamente desde el navegador
3. Ver los esquemas de request/response
4. Autenticarte usando el botón "Authorize" (pega tu token Bearer)

## 🔍 Verificar Datos en DynamoDB Local

Puedes usar AWS CLI para verificar los datos en DynamoDB Local:

```bash
# Listar tablas
aws dynamodb list-tables --endpoint-url http://localhost:8000 --region us-east-1

# Ver todos los usuarios
aws dynamodb scan --table-name kush-users-dev --endpoint-url http://localhost:8000 --region us-east-1

# Ver un usuario específico
aws dynamodb get-item \
  --table-name kush-users-dev \
  --key '{"email": {"S": "test@example.com"}}' \
  --endpoint-url http://localhost:8000 \
  --region us-east-1
```

## 🐛 Troubleshooting

### Error: "Could not validate credentials"

- Verifica que el token no haya expirado (duración: 30 minutos por defecto)
- Asegúrate de incluir "Bearer " antes del token
- Genera un nuevo token haciendo login nuevamente

### Error: "Failed to analyze image: 403 Permission denied"

- Verifica que tus credenciales de Google Cloud estén configuradas correctamente
- Asegúrate de que la API de Google Cloud Vision esté habilitada
- Verifica que la Service Account tenga los permisos necesarios

### Error: "Failed to connect to DynamoDB"

- Verifica que DynamoDB Local esté corriendo: `docker ps`
- Verifica que la variable `DYNAMODB_ENDPOINT_URL` esté configurada en `.env`
- Reinicia el contenedor: `docker-compose restart dynamodb-local`

### Error: "Table kush-users-dev does not exist"

- Ejecuta el script para crear tablas: `poetry run python scripts/create_tables.py`

### Error al subir imagen: "File size exceeds maximum allowed"

- El tamaño máximo por defecto es 10 MB
- Usa una imagen más pequeña o modifica `MAX_FILE_SIZE_MB` en el código

### Error: "Invalid image format"

- Solo se aceptan formatos: JPG, JPEG, PNG, GIF, WEBP
- Verifica que el archivo sea realmente una imagen válida

## 📊 Logs Estructurados

La aplicación usa structured logging con `structlog`. Los logs se imprimen en formato JSON:

```json
{
  "event": "request_started",
  "level": "info",
  "method": "POST",
  "path": "/api/v1/analyze",
  "timestamp": "2025-11-15T12:00:00.000Z"
}
```

Esto facilita el debugging y es compatible con CloudWatch Logs para producción.

## 🧹 Limpiar el Entorno

### Detener DynamoDB Local

```bash
docker-compose down
```

### Eliminar datos de DynamoDB Local

```bash
docker-compose down -v
```

### Eliminar tablas (sin eliminar el contenedor)

```bash
aws dynamodb delete-table \
  --table-name kush-users-dev \
  --endpoint-url http://localhost:8000 \
  --region us-east-1
```

## 🚀 Próximos Pasos

Una vez que hayas probado la API localmente:

1. **Pruebas Automatizadas**: Ejecuta `poetry run pytest` para correr los tests
2. **Cobertura**: Ejecuta `poetry run pytest --cov=app` para ver la cobertura de código
3. **Linting**: Ejecuta `make lint` para verificar calidad de código
4. **Deployment**: Sigue las instrucciones en `DEPLOYMENT.md` para desplegar en AWS Lambda

## 📚 Recursos Adicionales

- **Documentación FastAPI**: https://fastapi.tiangolo.com
- **Google Cloud Vision API**: https://cloud.google.com/vision/docs
- **AWS DynamoDB**: https://docs.aws.amazon.com/dynamodb/
- **JWT Authentication**: https://jwt.io/introduction
