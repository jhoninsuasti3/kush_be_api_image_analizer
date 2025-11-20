# Documentation Técnica - Kush Backend API Image Analyzer

## 📋 Información del Proyecto

**Nombre**: Kush Backend API Image Analyzer
**Objetivo**: Backend API serverless para análisis inteligente de imágenes con IA
**Tiempo estimado**: 1 día de desarrollo
**Stack**: Python 3.11+ | FastAPI | AWS Lambda | DynamoDB | Google Cloud Vision

---

## 🎯 Requerimientos del Proyecto

### Requerimientos BASE (Prueba Técnica)
1. **Endpoint POST /api/analyze**:
   - Recibe imagen (multipart/form-data)
   - Analiza con servicio de IA (Google Cloud Vision)
   - Retorna tags con confidence scores en JSON

2. **Integración con IA**:
   - Google Cloud Vision API (1000 requests/mes free tier)
   - Variables de entorno para API keys
   - Manejo de rate limits y errores

3. **Validaciones**:
   - Tipo de archivo (jpg, png, webp)
   - Tamaño máximo (5MB recomendado)
   - Formato de imagen válido

4. **Git Profesional**:
   - Commits atómicos con mensajes descriptivos
   - Ramas por feature
   - README completo

### Requerimientos ENTERPRISE (Extras)
1. **Autenticación JWT**: Registro y login de usuarios
2. **AWS Serverless**: Deploy en Lambda + API Gateway
3. **Persistencia**: DynamoDB para usuarios
4. **Containerización**: Docker + docker-compose
5. **CI/CD**: GitHub Actions (tests + deploy automático)
6. **Calidad de Código**:
   - Linters: ruff (linting + formatting) + mypy (type checking)
   - Tests unitarios + integración (coverage >70%)
   - Pre-commit hooks
7. **Observabilidad**:
   - Structured logging (structlog)
   - AWS CloudWatch Logs
   - CloudWatch Insights queries

---

## 🏗️ Arquitectura del Sistema

### Clean Architecture Modular (Inspirada en insights_backend)

**Principios de diseño**:
- ✅ Separación de responsabilidades por capas
- ✅ Inversión de dependencias (Ports & Adapters)
- ✅ Testeable y mantenible
- ✅ Escalable a microservicio

**Capas**:

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
│  - Orquestación de casos de uso         │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│    Infrastructure Layer (Adapters)      │
│  - GoogleVisionService (IAIService)     │
│  - DynamoDBUserRepository (IUserRepo)   │
│  - FileValidator                        │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        Domain Layer (Core)              │
│  - Models (User, Tag, ImageAnalysis)    │
│  - Ports (Interfaces ABC)               │
│  - Exceptions personalizadas            │
│  - Security utilities (JWT, bcrypt)     │
└─────────────────────────────────────────┘
```

---

## 📁 Estructura de Directorios

### Estructura FINAL del proyecto

```
kush_be_api_image_analizer/
├── app/                                 # Código fuente principal
│   ├── core/                            # Configuración y utilidades core
│   │   ├── __init__.py
│   │   ├── config.py                    # Pydantic Settings (centralizado)
│   │   ├── security.py                  # JWT + password hashing
│   │   ├── exceptions.py                # Custom exceptions
│   │   └── logging.py                   # Structured logging config
│   │
│   ├── domain/                          # Capa de dominio (modelos + contratos)
│   │   ├── __init__.py
│   │   ├── models.py                    # Pydantic models (User, Tag, ImageAnalysisResult)
│   │   └── ports.py                     # Interfaces (IAIService, IUserRepository)
│   │
│   ├── infrastructure/                  # Implementaciones concretas
│   │   ├── __init__.py
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   └── google_vision_service.py # Implementación de IAIService
│   │   ├── persistence/
│   │   │   ├── __init__.py
│   │   │   ├── dynamodb_client.py       # Cliente DynamoDB
│   │   │   └── user_repository.py       # Implementación de IUserRepository
│   │   └── validation/
│   │       ├── __init__.py
│   │       └── file_validator.py        # Validación de archivos
│   │
│   ├── application/                     # Capa de aplicación (casos de uso)
│   │   ├── __init__.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── auth_service.py          # Lógica de autenticación
│   │       └── image_analysis_service.py # Lógica de análisis de imágenes
│   │
│   ├── config/                          # Configuración de app (insights_backend pattern)
│   │   ├── __init__.py
│   │   ├── dependencies.py              # Dependency injection global
│   │   ├── exception_handlers.py        # Exception handlers centralizados
│   │   └── middlewares.py               # Middlewares (CORS, logging, errors)
│   │
│   ├── v1/                              # API v1 (versionamiento)
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI app v1
│   │   ├── dependencies/                # Dependencies específicos de v1
│   │   │   └── __init__.py
│   │   ├── serializers/                 # Request/Response models (Pydantic)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                  # UserCreate, UserLogin, Token
│   │   │   └── analyze.py               # ImageAnalysisResponse
│   │   ├── services/                    # Service layer de v1
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                  # Auth business logic
│   │   │   └── analyze.py               # Analysis business logic
│   │   └── views/                       # FastAPI routers (endpoints)
│   │       ├── __init__.py
│   │       ├── auth.py                  # POST /auth/register, /auth/login
│   │       ├── analyze.py               # POST /analyze
│   │       └── health.py                # GET /health, /ready
│   │
│   ├── __init__.py
│   └── main.py                          # Entry point principal + Mangum handler
│
├── tests/                               # Tests (unitarios + integración)
│   ├── __init__.py
│   ├── conftest.py                      # Fixtures compartidos
│   ├── unit/                            # Tests unitarios
│   │   ├── __init__.py
│   │   ├── test_core/
│   │   │   ├── test_security.py
│   │   │   └── test_config.py
│   │   ├── test_domain/
│   │   │   └── test_models.py
│   │   └── test_infrastructure/
│   │       ├── test_google_vision.py
│   │       └── test_file_validator.py
│   └── integration/                     # Tests de integración
│       ├── __init__.py
│       ├── test_auth_flow.py
│       └── test_analyze_api.py
│
├── scripts/                             # Scripts de utilidad
│   ├── create_tables.py                 # Crear tablas DynamoDB
│   ├── deploy.sh                        # Script de deploy
│   └── analyze_logs.sh                  # Queries CloudWatch Insights
│
├── .github/                             # CI/CD
│   └── workflows/
│       ├── ci.yml                       # Lint + Test + Coverage
│       └── cd.yml                       # Deploy staging/prod
│
├── Dockerfile                           # Multi-stage Docker build
├── docker-compose.yml                   # Servicios locales (API + DynamoDB Local)
├── template.yaml                        # AWS SAM template
├── pyproject.toml                       # Poetry config + linters
├── poetry.lock                          # Lock de dependencias
├── Makefile                             # Comandos de desarrollo
├── .env.example                         # Template de variables de entorno
├── .gitignore                           # Python + AWS gitignore
├── .pre-commit-config.yaml              # Pre-commit hooks
├── README.md                            # Documentación principal
└── documentation_tech.md                # Este archivo
```

---

## 🔑 Lecciones Aprendidas de insights_backend

### ✅ Buenas Prácticas Adoptadas

1. **Poetry Groups Opcionales**:
   ```toml
   [tool.poetry.group.code-quality]
   optional = true

   [tool.poetry.group.test]
   optional = true
   ```
   - Permite instalar solo dependencias necesarias por entorno
   - Reduce tamaño de imagen Docker en producción

2. **Settings Centralizados con Dataclasses**:
   ```python
   @dataclass(frozen=True)
   class Settings:
       jwt_secret: str = field(default_factory=lambda: os.getenv("JWT_SECRET"))
   ```
   - Inmutables (`frozen=True`)
   - Type hints para validación
   - Defaults desde environment variables

3. **Dependency Injection Explícita**:
   - `apps/config/dependencies.py` con factory functions
   - Facilita testing con mocks
   - Separa configuración de lógica de negocio

4. **Multi-stage Dockerfile Optimizado**:
   ```dockerfile
   FROM python-base AS python-builder
   # Build dependencies

   FROM python-base AS python-app
   # Runtime minimal
   ```
   - Reduce tamaño final de imagen
   - Separa build-time vs runtime dependencies

5. **Comandos de Management Personalizados**:
   - `manage.py` con utilidad de comandos
   - Migraciones, health checks, scripts custom
   - Similar a Django management commands

6. **Configuración de Linters Estricta**:
   ```toml
   [tool.mypy]
   disallow_untyped_defs = true

   [tool.ruff]
   line-length = 119
   ```
   - Enforza type hints
   - Consistencia en código

7. **Versionamiento de API**:
   ```python
   app.mount(path="/v1", app=app_v1)
   app.mount(path="/v2", app=app_v2)
   ```
   - Permite evolución sin breaking changes

8. **Exception Handlers Centralizados**:
   - `register_exception_handlers(app)`
   - Respuestas de error consistentes
   - Logging automático de errores

9. **Badges en README**:
   - Code style, linting, typing
   - Demuestra profesionalismo

10. **`.env.template` Documentado**:
    - Cada variable con comentario explicativo
    - Facilita onboarding de nuevos devs

---

## 🛠️ Stack Tecnológico

### Core
- **Python**: 3.11+ (mismo que insights_backend)
- **FastAPI**: Framework web moderno, async
- **Poetry**: Gestión de dependencias y entorno virtual
- **Pydantic**: Validación de datos y settings

### AWS Services
- **Lambda**: Compute serverless (con Mangum adapter)
- **API Gateway**: HTTP API
- **DynamoDB**: Base de datos NoSQL para usuarios
- **CloudWatch**: Logs y métricas
- **SAM CLI**: Deploy y testing local

### AI/ML
- **Google Cloud Vision API**: Análisis de imágenes (label detection)

### Seguridad
- **python-jose**: JWT tokens
- **passlib[bcrypt]**: Password hashing

### Calidad de Código
- **ruff**: Linter ultra-rápido (reemplaza flake8, black, isort)
  - Linting + formatting + import sorting todo en uno
  - Compatible con Black, pero más rápido
- **mypy**: Type checking estático

### Testing
- **pytest**: Framework de testing
- **pytest-cov**: Coverage reports
- **pytest-asyncio**: Tests async
- **httpx**: Cliente HTTP para tests de integración
- **faker**: Datos fake para tests
- **factory-boy**: Factories para modelos (opcional)

### DevOps
- **Docker**: Containerización
- **docker-compose**: Orquestación local
- **GitHub Actions**: CI/CD
- **pre-commit**: Git hooks

### Observabilidad
- **structlog**: Structured logging
- **OpenTelemetry**: Tracing (opcional para futuro)
- **Sentry**: Error tracking (opcional)

---

## 📦 Dependencias (pyproject.toml)

### Dependencias de Producción
```toml
[tool.poetry.dependencies]
python = ">=3.11, <3.12"
fastapi = {version = ">=0.115.0, <1.0.0", extras = ["standard"]}
uvicorn = {version = ">=0.27.0, <1.0.0", extras = ["standard"]}
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"

# AWS
boto3 = "^1.35.0"
mangum = "^0.17.0"

# AI
google-cloud-vision = "^3.7.0"
pillow = "^10.2.0"

# Auth
python-jose = {version = "^3.3.0", extras = ["cryptography"]}
passlib = {version = "^1.7.4", extras = ["bcrypt"]}
python-multipart = "^0.0.6"

# Utils
python-dotenv = "^1.0.0"
structlog = "^24.0.0"
```

### Dependencias de Desarrollo
```toml
[tool.poetry.group.code-quality]
optional = true
[tool.poetry.group.code-quality.dependencies]
ruff = ">=0.6.0, <1.0.0"
mypy = "^1.11.0"

[tool.poetry.group.test]
optional = true
[tool.poetry.group.test.dependencies]
pytest = "^8.3.0"
pytest-cov = "^5.0.0"
pytest-asyncio = "^0.24.0"
httpx = "^0.27.0"
faker = "^33.0.0"
```

---

## ⚙️ Configuración de Linters

### Ruff (linting + formatting + imports)
```toml
[tool.ruff]
target-version = "py311"
line-length = 119
show-fixes = true
extend-exclude = ["local/", ".venv/", "venv/"]

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "UP",   # pyupgrade
]
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
```

### Mypy
```toml
[tool.mypy]
python_version = "3.11"
disallow_untyped_defs = true
disallow_untyped_calls = false
show_column_numbers = true
ignore_missing_imports = true
exclude = [".venv/", "venv/", "local/", "tests/"]
```

### Coverage
```toml
[tool.coverage.run]
source = ["."]
omit = ["tests/*", "local/*", ".venv/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

---

## 🔐 Variables de Entorno (.env.example)

```bash
# App Configuration
DEBUG=false
ENVIRONMENT=development  # development | staging | production

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
DYNAMODB_USERS_TABLE=kush-users-dev
DYNAMODB_ENDPOINT_URL=http://localhost:8000  # Para DynamoDB Local

# Google Cloud Vision
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
# O alternativamente:
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_API_KEY=your-api-key

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload Limits
MAX_FILE_SIZE_MB=5
ALLOWED_EXTENSIONS=jpg,jpeg,png,webp

# Logging
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR

# CORS (opcional)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Sentry (opcional)
SENTRY_DSN=
SENTRY_ENVIRONMENT=development
```

---

## 🚀 Roadmap de Desarrollo (8 Fases)

### FASE 1: Foundation & Setup ⏱️ 1.5h
**Rama**: `feature/project-setup`

**Entregables**:
- ✅ Poetry inicializado con pyproject.toml
- ✅ Todas las dependencias instaladas
- ✅ Linters configurados (ruff + mypy)
- ✅ Pre-commit hooks
- ✅ Makefile con comandos útiles
- ✅ .env.example documentado
- ✅ Estructura de carpetas creada (vacía)
- ✅ README.md inicial
- ✅ .gitignore

**Comandos clave**:
```bash
poetry install --with "code-quality,test"
make lint
make test
```

---

### FASE 2: Core & Domain Layer ⏱️ 1h
**Rama**: `feature/core-domain`

**Entregables**:
- ✅ `core/config.py`: Pydantic Settings
- ✅ `core/security.py`: JWT + password hashing
- ✅ `core/exceptions.py`: Custom exceptions
- ✅ `domain/models.py`: User, Tag, ImageAnalysisResult
- ✅ `domain/ports.py`: IAIService, IUserRepository (ABC)
- ✅ Tests unitarios (>85% coverage)

**Modelos clave**:
```python
# User, UserCreate, UserLogin, TokenData
# Tag (label, confidence)
# ImageAnalysisRequest, ImageAnalysisResult
```

---

### FASE 3: Infrastructure - DynamoDB ⏱️ 1.5h
**Rama**: `feature/dynamodb-users`

**Entregables**:
- ✅ `infrastructure/persistence/dynamodb_client.py`
- ✅ `infrastructure/persistence/user_repository.py`: CRUD completo
- ✅ `docker-compose.yml`: DynamoDB Local
- ✅ `scripts/create_tables.py`: Inicialización de tablas
- ✅ Tests de integración con DynamoDB Local

**Schema DynamoDB**:
```
Table: users
PK: email (String)
SK: USER#{timestamp} (String)
Attributes: hashed_password, created_at, is_active
```

---

### FASE 4: Infrastructure - Google Vision ⏱️ 1.5h
**Rama**: `feature/google-vision-integration`

**Entregables**:
- ✅ `infrastructure/ai/google_vision_service.py`: Implementa IAIService
- ✅ `infrastructure/validation/file_validator.py`: Validaciones de archivos
- ✅ Retry logic con exponential backoff
- ✅ Transformación de EntityAnnotation → Tag
- ✅ Tests unitarios con mocks

**Validaciones**:
- Tamaño < 5MB
- Extensión: .jpg, .jpeg, .png, .webp
- Formato válido (Pillow.Image.open)

---

### FASE 5: Application Layer & Auth API ⏱️ 2h
**Rama**: `feature/auth-endpoints`

**Entregables**:
- ✅ `application/services/auth_service.py`
- ✅ `application/services/image_analysis_service.py`
- ✅ `api/dependencies.py`: IoC container
- ✅ `api/middleware.py`: CORS, logging, error handling
- ✅ `api/routes/auth.py`: /register, /login, /me
- ✅ `api/routes/health.py`: /health, /ready
- ✅ Tests e2e de auth flow

**Endpoints**:
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me` (protected)
- `GET /health`
- `GET /ready` (check DynamoDB)

---

### FASE 6: Image Analysis API ⏱️ 1h
**Rama**: `feature/analyze-endpoint`

**Entregables**:
- ✅ `api/routes/analyze.py`: POST /api/analyze
- ✅ Multipart file upload
- ✅ JWT authentication required
- ✅ Integración completa: validate → AI → respond
- ✅ Manejo de errores HTTP (400, 401, 413, 500)
- ✅ Logging de métricas
- ✅ Tests e2e con imágenes reales

**Response example**:
```json
{
  "tags": [
    {"label": "Dog", "confidence": 0.98},
    {"label": "Golden Retriever", "confidence": 0.95}
  ]
}
```

---

### FASE 7: Serverless & Docker ⏱️ 2h
**Rama**: `feature/serverless-deployment`

**Entregables**:
- ✅ `app/main.py`: FastAPI + Mangum handler
- ✅ `Dockerfile`: Multi-stage optimizado
- ✅ `docker-compose.yml`: API + DynamoDB Local
- ✅ `template.yaml`: AWS SAM (Lambda + API Gateway + DynamoDB)
- ✅ `scripts/deploy.sh`: Deploy a dev/staging/prod
- ✅ Makefile actualizado
- ✅ README con instrucciones de deploy

**Mangum adapter**:
```python
from mangum import Mangum
handler = Mangum(app, lifespan="off")
```

---

### FASE 8: CI/CD & Observability ⏱️ 1.5h
**Rama**: `feature/cicd-observability`

**Entregables**:
- ✅ `.github/workflows/ci.yml`: Lint + Test + Coverage
- ✅ `.github/workflows/cd.yml`: Deploy automático
- ✅ `core/logging.py`: Structured logging con structlog
- ✅ Logging en todos los endpoints
- ✅ `scripts/analyze_logs.sh`: Queries CloudWatch
- ✅ Coverage >70% validado
- ✅ README con badges

**GitHub Actions CI**:
```yaml
- Lint (ruff check + format)
- Type check (mypy)
- Test con pytest
- Coverage report
- Upload a Codecov
```

---

## 📝 Makefile - Comandos de Desarrollo

```makefile
.PHONY: install lint format test test-cov run docker-up docker-down deploy-dev deploy-prod

install:
	poetry install --with "code-quality,test"

lint:
	ruff check .
	ruff format --check .
	mypy app/

format:
	ruff format .
	ruff check --fix .

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

test-watch:
	pytest-watch tests/ -v

run:
	fastapi dev app/main.py

docker-build:
	docker build -t kush-image-analyzer:latest .

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down -v

create-tables:
	python scripts/create_tables.py

deploy-dev:
	sam build && sam deploy --config-env dev

deploy-staging:
	sam build && sam deploy --config-env staging

deploy-prod:
	sam build && sam deploy --config-env prod

logs-dev:
	sam logs --stack-name kush-image-analyzer-dev --tail

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache
```

---

## 🧪 Estrategia de Testing

### Coverage Target: >70%

**Prioridades**:
1. **Core (>90%)**: `security.py`, `config.py`
2. **Domain (>85%)**: Validación de modelos Pydantic
3. **Infrastructure (>80%)**: AI service, User repository
4. **Application (>75%)**: Services
5. **API (>70%)**: Endpoints end-to-end

**Fixtures importantes**:
```python
# conftest.py
@pytest.fixture
def test_user():
    return User(email="test@example.com", hashed_password="...")

@pytest.fixture
def test_image():
    return Path("tests/fixtures/test_dog.jpg")

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

---

## 🔄 Git Workflow

### Estrategia de Branching

```
main (production)
  ├── develop (integration)
  │     ├── feature/project-setup
  │     ├── feature/core-domain
  │     ├── feature/dynamodb-users
  │     ├── feature/google-vision-integration
  │     ├── feature/auth-endpoints
  │     ├── feature/analyze-endpoint
  │     ├── feature/serverless-deployment
  │     └── feature/cicd-observability
  └── hotfix/* (emergencias en producción)
```

### Commit Message Convention

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Ejemplo**:
```
feat(auth): implement JWT authentication endpoints

- Add register endpoint with email validation
- Add login endpoint with bcrypt password verification
- Implement get_current_user dependency for protected routes
- Add custom exceptions for auth errors

Tests: 18 e2e tests, coverage 84%
```

---

## 🚦 CI/CD Pipeline

### CI (Continuous Integration)
**Trigger**: Push a cualquier rama, PRs a develop/main

```yaml
jobs:
  lint:
    - ruff check .
    - ruff format --check .
    - mypy app/

  test:
    - pytest --cov
    - coverage report
    - upload to Codecov
```

### CD (Continuous Deployment)
**Trigger**:
- Merge a `develop` → Deploy a **staging**
- Merge a `main` → Deploy a **production** (con aprobación manual)

```yaml
deploy-staging:
  - sam build
  - sam deploy --config-env staging

deploy-prod:
  - Require manual approval
  - sam build
  - sam deploy --config-env prod
```

---

## 📊 Observabilidad

### Structured Logging
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "image_analyzed",
    user_id=user.id,
    file_size_kb=file_size / 1024,
    tags_count=len(tags),
    latency_ms=latency,
)
```

### CloudWatch Insights Queries
```sql
-- Errores en últimas 24h
fields @timestamp, level, event, exception
| filter level = "error"
| sort @timestamp desc
| limit 100

-- Latencia promedio por endpoint
fields @timestamp, event, latency_ms
| filter event = "image_analyzed"
| stats avg(latency_ms), max(latency_ms), count() by bin(5m)
```

---

## 🔒 Seguridad

### Checklist
- ✅ JWT tokens con expiración (30 min)
- ✅ Passwords hasheados con bcrypt (cost factor 12)
- ✅ Variables sensibles en .env (NO en código)
- ✅ Validación de archivos (tipo, tamaño, formato)
- ✅ CORS configurado solo para orígenes permitidos
- ✅ Rate limiting (futuro: AWS API Gateway throttling)
- ✅ Sanitización de inputs (Pydantic)
- ✅ HTTPS only en producción (API Gateway)
- ✅ Secrets en AWS Secrets Manager (producción)

---

## 📚 Referencias y Recursos

### Documentación Oficial
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [AWS SAM](https://docs.aws.amazon.com/serverless-application-model/)
- [Google Cloud Vision](https://cloud.google.com/vision/docs)
- [Mangum](https://mangum.io/)
- [Structlog](https://www.structlog.org/)

### Inspiración
- `insights_backend/`: Estructura y buenas prácticas de Simetrik

---

## 🎓 Notas para Claude en Cursor

Cuando trabajes en este proyecto:

1. **Sigue la arquitectura limpia**: Respeta las capas (API → Application → Infrastructure → Domain)
2. **Type hints obligatorios**: Mypy en modo strict
3. **Tests primero**: Escribe tests mientras desarrollas, no al final
4. **Commits atómicos**: Una responsabilidad por commit
5. **Logging defensivo**: Logea entradas, salidas y errores
6. **Documentación**: Docstrings en funciones públicas
7. **No hardcodear**: Usa Settings para configuración
8. **Manejo de errores**: Siempre captura y logea excepciones
9. **Validación**: Usa Pydantic para validar datos de entrada
10. **DRY**: No te repitas, crea abstracciones reutilizables

---

## ✅ Checklist Pre-Deploy

- [ ] Coverage >70% (verificar con `make test-cov`)
- [ ] Todos los linters pasan (`make lint`)
- [ ] Tests e2e pasando localmente
- [ ] Variables de entorno documentadas en `.env.example`
- [ ] README con instrucciones claras
- [ ] Health check respondiendo (`/health`, `/ready`)
- [ ] Docker build exitoso (`make docker-build`)
- [ ] Docker-compose funcional (`make docker-up`)
- [ ] CI verde en GitHub Actions
- [ ] SAM local testing (`sam local start-api`)
- [ ] Secrets configurados en AWS Secrets Manager
- [ ] DynamoDB table creada en AWS
- [ ] Google Cloud service account configurado
- [ ] CloudWatch logs group creado
- [ ] API Gateway configurado con throttling

---

**Última actualización**: 2025-11-15
**Versión**: 1.0.0
**Mantenedor**: @jhonmo