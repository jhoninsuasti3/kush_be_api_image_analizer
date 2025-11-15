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

## 🚀 Quick Start

### Prerrequisitos

- Python 3.11+
- Poetry 1.6+
- Docker & Docker Compose
- AWS CLI (para deployment)
- Cuenta Google Cloud (para Vision API)

### Instalación

1. **Clonar el repositorio**:
```bash
git clone https://github.com/yourusername/kush_be_api_image_analizer.git
cd kush_be_api_image_analizer
```

2. **Instalar dependencias con Poetry**:
```bash
# Instalar todas las dependencias (producción + desarrollo)
make install-all

# O manualmente:
poetry install --with code-quality,test
```

3. **Configurar variables de entorno**:
```bash
# Copiar template de .env
make env

# Editar .env con tus valores
nano .env
```

4. **Configurar Google Cloud Vision**:
- Crear proyecto en [Google Cloud Console](https://console.cloud.google.com/)
- Habilitar Vision API
- Crear service account y descargar JSON key
- Configurar `GOOGLE_APPLICATION_CREDENTIALS` en `.env`

5. **Iniciar servicios locales con Docker**:
```bash
# Inicia API + DynamoDB Local
make docker-up
```

6. **Crear tablas DynamoDB**:
```bash
make create-tables
```

7. **Acceder a la API**:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

## 📚 Comandos Disponibles

### Desarrollo
```bash
make run              # Iniciar servidor de desarrollo
make dev              # Alias de 'make run'
make help             # Ver todos los comandos
```

### Calidad de Código
```bash
make lint             # Ejecutar linters (ruff + mypy)
make format           # Formatear código automáticamente
make pre-commit       # Ejecutar pre-commit hooks
```

### Testing
```bash
make test             # Ejecutar todos los tests
make test-cov         # Tests con reporte de coverage
make test-unit        # Solo tests unitarios
make test-integration # Solo tests de integración
```

### Docker
```bash
make docker-build     # Construir imagen Docker
make docker-up        # Iniciar servicios con compose
make docker-down      # Detener servicios
make docker-logs      # Ver logs de containers
```

### Deployment
```bash
make deploy-dev       # Deploy a desarrollo
make deploy-staging   # Deploy a staging
make deploy-prod      # Deploy a producción
make logs-dev         # Ver logs de desarrollo
```

### Utilidades
```bash
make clean            # Limpiar archivos temporales
make check            # Ejecutar lint + tests + coverage
make ci               # Simular CI pipeline localmente
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

```bash
# Ejecutar todos los tests
poetry run pytest

# Con coverage
poetry run pytest --cov=app --cov-report=html

# Ver reporte de coverage
open htmlcov/index.html
```

**Estructura de tests**:
```
tests/
├── unit/              # Tests unitarios
│   ├── test_core/
│   ├── test_domain/
│   └── test_infrastructure/
└── integration/       # Tests de integración
    ├── test_auth_flow.py
    └── test_analyze_api.py
```

## 🐳 Docker

### Desarrollo Local
```bash
# Iniciar todos los servicios
docker-compose up

# Solo DynamoDB Local
docker-compose up dynamodb-local
```

### Build de Producción
```bash
# Construir imagen
docker build -t kush-image-analyzer:latest .

# Ejecutar container
docker run -p 8000:8000 --env-file .env kush-image-analyzer:latest
```

## ☁️ AWS Deployment

### Preparación
1. Configurar AWS CLI:
```bash
aws configure
```

2. Crear tabla DynamoDB en AWS:
```bash
aws dynamodb create-table \
  --table-name kush-users-prod \
  --attribute-definitions AttributeName=email,AttributeType=S \
  --key-schema AttributeName=email,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### Deploy con SAM
```bash
# Deploy a desarrollo
sam build && sam deploy --config-env dev

# Deploy a producción
sam build && sam deploy --config-env prod
```

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
│   ├── config/            # App configuration
│   ├── v1/                # API v1 (versioned)
│   └── main.py            # Entry point
├── tests/                 # Tests unitarios e integración
├── scripts/               # Scripts de utilidad
├── .github/workflows/     # CI/CD pipelines
├── Dockerfile             # Container definition
├── docker-compose.yml     # Local services
├── template.yaml          # AWS SAM template
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

## 📝 Roadmap

- [x] **FASE 1**: Foundation & Setup
- [ ] **FASE 2**: Core & Domain Layer
- [ ] **FASE 3**: Infrastructure - DynamoDB
- [ ] **FASE 4**: Infrastructure - Google Vision
- [ ] **FASE 5**: Application Layer & Auth API
- [ ] **FASE 6**: Image Analysis API
- [ ] **FASE 7**: Serverless & Docker
- [ ] **FASE 8**: CI/CD & Observability

Ver [documentation_tech.md](./documentation_tech.md) para detalles completos.

## 📄 Licencia

Este proyecto es privado y confidencial.

## 👨‍💻 Autor

**jhonmo**

---

**Documentación Técnica Completa**: Ver [documentation_tech.md](./documentation_tech.md)