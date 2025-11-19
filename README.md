# 🖼️ Kush Backend API - Image Analyzer

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![AWS: Lambda](https://img.shields.io/badge/AWS-Lambda-orange.svg)](https://aws.amazon.com/lambda/)

Backend API serverless para análisis inteligente de imágenes con IA. La aplicación analiza imágenes utilizando Google Cloud Vision y retorna etiquetas (tags) que describen el contenido de la imagen con scores de confianza.

## 📋 Características

- ✅ **API REST** con FastAPI (async/await)
- ✅ **Análisis de Imágenes** con Google Cloud Vision API
- ✅ **Autenticación JWT** para usuarios
- ✅ **Serverless** con AWS Lambda + API Gateway
- ✅ **Base de datos** DynamoDB para persistencia de usuarios
- ✅ **Clean Architecture** modular y escalable
- ✅ **Containerización** con Docker y docker-compose
- ✅ **CI/CD** con GitHub Actions
- ✅ **Tests** unitarios e integración (coverage >70%)
- ✅ **Observabilidad** con structured logging (CloudWatch)

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────┐
│           API Layer (FastAPI)           │
│  - Routes (auth, analyze, health)       │
│  - Dependencies (IoC)                   │
│  - Middlewares (CORS, JWT, Logging)     │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│      Application Layer (Services)       │
│  - AuthService                          │
│  - ImageAnalysisService                 │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│    Infrastructure Layer (Adapters)      │
│  - GoogleVisionService                  │
│  - DynamoDBUserRepository               │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        Domain Layer (Core)              │
│  - Models, Ports, Exceptions            │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start (Desarrollo Local)

### Prerrequisitos

- Docker 20.10+
- Docker Compose 2.0+

### Instalación

1. **Clonar el repositorio**:
```bash
git clone <repository-url>
cd kush_be_api_image_analizer
```

2. **Configurar variables de entorno**:
```bash
cp .env.example .env
```

3. **Iniciar servicios con Docker**:
```bash
docker compose up --build

# O usando Makefile
make docker-up
```

**¡Listo!** Los servicios están corriendo:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health
- DynamoDB Local: http://localhost:8001

### Verificar instalación

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Debe retornar: {"status": "healthy", ...}
```

### Configuración de Google Cloud Vision (Opcional)

Para habilitar el análisis de imágenes con IA:

1. **Obtener credenciales** de Google Cloud (ver [GOOGLE_CLOUD_SETUP.md](./documentation/GOOGLE_CLOUD_SETUP.md))
2. **Guardar** el archivo JSON en `credentials/google-vision-credentials.json`
3. **Reiniciar** servicios: `docker compose restart api`

**Nota**: La API funciona sin Google Cloud, pero el endpoint `/api/v1/analyze` retornará error. Los endpoints de autenticación funcionan normalmente.

## 📚 Comandos Disponibles

### Docker (Desarrollo Local)
```bash
make docker-up           # Iniciar servicios (foreground)
make docker-up-d         # Iniciar servicios (background)
make docker-down         # Detener servicios
make docker-down-clean   # Detener y limpiar base de datos
make docker-logs         # Ver logs de todos los servicios
make docker-logs-api     # Ver logs solo de la API
make docker-restart      # Reiniciar servicios
make docker-shell        # Abrir shell en el container
make docker-test         # Ejecutar tests dentro del container
make docker-test-cov     # Tests con coverage
```

### Testing (Dentro del container)
```bash
docker compose exec api pytest tests/              # Todos los tests
docker compose exec api pytest tests/unit/         # Solo unitarios
docker compose exec api pytest tests/integration/  # Solo integración
docker compose exec api pytest --cov=app           # Con coverage
```

### Calidad de Código
```bash
make lint             # Ejecutar linters (ruff + mypy)
make format           # Formatear código automáticamente
make check            # Ejecutar lint + tests + coverage
```

#### Hooks de pre-commit

1. Instalar los hooks (solo una vez):
   ```bash
   poetry run pre-commit install
   ```
2. Ejecutarlos manualmente en todo el repo (opcional):
   ```bash
   poetry run pre-commit run --all-files
   ```

Los hooks ejecutan automáticamente `ruff` (lint + format) y `mypy` antes de cada commit, evitando subir código que no pase las validaciones básicas.

### Utilidades
```bash
make help             # Ver todos los comandos disponibles
make clean            # Limpiar archivos temporales
```

## 📖 API Endpoints

### Authentication
```http
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

### Image Analysis
```http
POST /api/v1/analyze
```

**Ejemplo de request**:
```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/image.jpg"
```

**Ejemplo de response**:
```json
{
  "tags": [
    {"label": "Dog", "confidence": 0.98},
    {"label": "Golden Retriever", "confidence": 0.95},
    {"label": "Pet", "confidence": 0.92}
  ]
}
```

### Health Check
```http
GET /health       # Health check básico
GET /ready        # Readiness check (incluye DynamoDB)
```

## 🧪 Testing

El proyecto cuenta con **201+ tests profesionales** (unitarios e integración) con coverage >70%.

```bash
# Ejecutar todos los tests (dentro del container)
docker compose exec api pytest tests/

# Con coverage
docker compose exec api pytest tests/ --cov=app --cov-report=html

# Ver reporte de coverage
open htmlcov/index.html
```

**Estructura de tests**:
```
tests/
├── unit/              # Tests unitarios (106 tests)
│   ├── test_core/
│   ├── test_domain/
│   └── test_infrastructure/
└── integration/       # Tests de integración (95 tests)
    ├── test_auth_endpoints.py
    └── test_analyze_endpoint.py
```

Ver [TESTING_GUIDE.md](./documentation/TESTING_GUIDE.md) para más detalles.

## 🔐 Seguridad

- ✅ JWT tokens con expiración (30 min)
- ✅ Passwords hasheados con bcrypt
- ✅ Variables sensibles en AWS Secrets Manager
- ✅ Validación de archivos (tipo, tamaño)
- ✅ CORS configurado
- ✅ HTTPS only en producción
- ✅ Rate limiting en API Gateway

## 📊 Observabilidad

### Logs Estructurados
Todos los eventos importantes se loguean en formato JSON:
```python
logger.info("image_analyzed", user_id=user.id, tags_count=5)
```

### CloudWatch
- Logs centralizados en CloudWatch Logs
- Métricas custom
- Alarmas configuradas

## 🛠️ Stack Tecnológico

- **Framework**: FastAPI 0.115+
- **Language**: Python 3.11+
- **Package Manager**: Poetry
- **AWS**: Lambda, API Gateway, DynamoDB, CloudWatch
- **AI**: Google Cloud Vision API
- **Auth**: JWT (python-jose, passlib)
- **Linting**: Ruff (linter + formatter)
- **Type Checking**: mypy
- **Testing**: pytest, httpx, faker
- **Containerization**: Docker, docker-compose
- **IaC**: AWS SAM
- **CI/CD**: GitHub Actions

## 📁 Estructura del Proyecto

```
kush_be_api_image_analizer/
├── app/                    # Código fuente
│   ├── core/              # Config, security, exceptions
│   ├── domain/            # Models y ports
│   ├── infrastructure/    # AI, persistence, validation
│   ├── application/       # Business logic
│   ├── v1/                # API v1 (versioned)
│   └── main.py            # Entry point
├── credentials/           # Credenciales (ignorado por Git)
│   ├── .gitignore        # Ignora todos los archivos sensibles
│   └── README.md         # Instrucciones de uso
├── tests/                 # Tests unitarios e integración
├── handlers/              # Lambda handlers para AWS
├── documentation/         # Documentación técnica
├── scripts/               # Scripts de utilidad
├── Dockerfile             # Container definition (multi-stage)
├── docker-compose.yml     # Local services
├── pyproject.toml         # Dependencies + config
└── Makefile               # Development commands
```

## 🤝 Contribución

1. Crear feature branch desde `develop`
2. Implementar cambios con tests
3. Ejecutar `make check` para validar
4. Crear Pull Request a `develop`

**Git Workflow**:
```
main (production)
  └── develop (integration)
        └── feature/your-feature-name
```

## 🚀 Deployment a AWS Lambda

El proyecto está configurado para deployment automático a AWS Lambda usando GitHub Actions.

### Quick Deploy

```bash
# Crear tablas DynamoDB en AWS (solo primera vez)
aws dynamodb create-table \
  --table-name kush-users-dev \
  --attribute-definitions AttributeName=email,AttributeType=S \
  --key-schema AttributeName=email,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Deploy automático con push
git push origin develop   # Deploy a dev
git push origin staging   # Deploy a staging
git push origin main      # Deploy a production

# Deploy manual
npm run deploy:dev
# o
make sls-deploy-dev
```

### Configuración Requerida

1. **GitHub Secrets** (Settings → Secrets → Actions):
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `JWT_SECRET_KEY`

2. **Ambientes en GitHub** (Settings → Environments):
   - `dev` (branch: develop)
   - `staging` (branch: staging, requires 1 reviewer)
   - `prod` (branch: main, requires 2 reviewers)

Ver guía completa: **[DEPLOYMENT_GUIDE.md](./documentation/DEPLOYMENT_GUIDE.md)**

## 📚 Documentación Adicional

- **[DOCKER_QUICKSTART.md](./DOCKER_QUICKSTART.md)** - Guía completa de Docker (troubleshooting, desarrollo)
- **[DEPLOYMENT_GUIDE.md](./documentation/DEPLOYMENT_GUIDE.md)** - Guía completa de deployment a AWS
- **[GOOGLE_CLOUD_SETUP.md](./documentation/GOOGLE_CLOUD_SETUP.md)** - Configuración de Google Cloud Vision
- **[TESTING_GUIDE.md](./documentation/TESTING_GUIDE.md)** - Guía completa de testing
- **[SERVERLESS_ARCHITECTURE.md](./documentation/SERVERLESS_ARCHITECTURE.md)** - Arquitectura serverless (AWS Lambda)
- **[documentation_tech.md](./documentation/documentation_tech.md)** - Documentación técnica detallada

## 📄 Licencia

Este proyecto es privado y confidencial.

## 👨‍💻 Autor

**jhonmo**
