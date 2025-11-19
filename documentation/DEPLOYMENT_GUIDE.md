# 🚀 Deployment Guide - AWS Lambda

Guía completa para desplegar la API a AWS Lambda usando GitHub Actions.

## 📋 Tabla de Contenidos

- [Prerequisitos](#prerequisitos)
- [Configuración de AWS](#configuración-de-aws)
- [Configuración de GitHub Secrets](#configuración-de-github-secrets)
- [Configuración de Ambientes](#configuración-de-ambientes)
- [Deploy Automático](#deploy-automático)
- [Deploy Manual](#deploy-manual)
- [Verificación](#verificación)
- [Rollback](#rollback)
- [Troubleshooting](#troubleshooting)

---

## 📦 Prerequisitos

### AWS
- ✅ Cuenta de AWS activa
- ✅ Permisos de IAM para Lambda, API Gateway, DynamoDB, CloudWatch
- ✅ AWS CLI configurado localmente (para testing)

### GitHub
- ✅ Repositorio con permisos de admin
- ✅ GitHub Actions habilitado

### Local
- ✅ Node.js 18+
- ✅ Python 3.11+
- ✅ Serverless Framework (`npm install -g serverless`)

---

## 🔐 Configuración de AWS

### 1. Crear Usuario IAM para CI/CD

```bash
# En AWS Console o CLI
aws iam create-user --user-name github-actions-kush-api

# Crear access key
aws iam create-access-key --user-name github-actions-kush-api
```

**Guarda estos valores**:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### 2. Asignar Permisos

Crea una policy con estos permisos mínimos:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:*",
        "apigateway:*",
        "dynamodb:*",
        "cloudformation:*",
        "s3:*",
        "iam:GetRole",
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:PassRole",
        "logs:*",
        "cloudwatch:*"
      ],
      "Resource": "*"
    }
  ]
}
```

Adjunta la policy al usuario:

```bash
aws iam put-user-policy \
  --user-name github-actions-kush-api \
  --policy-name KushAPIDeploymentPolicy \
  --policy-document file://policy.json
```

### 3. Crear Tablas DynamoDB en AWS

```bash
# Development
aws dynamodb create-table \
  --table-name kush-users-dev \
  --attribute-definitions AttributeName=email,AttributeType=S \
  --key-schema AttributeName=email,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Staging
aws dynamodb create-table \
  --table-name kush-users-staging \
  --attribute-definitions AttributeName=email,AttributeType=S \
  --key-schema AttributeName=email,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Production
aws dynamodb create-table \
  --table-name kush-users-prod \
  --attribute-definitions AttributeName=email,AttributeType=S \
  --key-schema AttributeName=email,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

---

## 🔑 Configuración de GitHub Secrets

### Secrets a Nivel de Repositorio

Ve a: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

Agrega estos secrets:

| Secret Name | Descripción | Ejemplo |
|-------------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | Access Key del usuario IAM | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | Secret Access Key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `JWT_SECRET_KEY` | Secret para firmar JWTs | `openssl rand -hex 32` |

### Variables a Nivel de Repositorio (Opcionales)

| Variable Name | Valor | Descripción |
|---------------|-------|-------------|
| `SLACK_WEBHOOK_URL` | `https://hooks.slack.com/...` | Para notificaciones |
| `AWS_REGION` | `us-east-1` | Región por defecto |

---

## 🌍 Configuración de Ambientes

### Crear Ambientes en GitHub

Ve a: `Settings` → `Environments`

#### 1. Ambiente `dev`
- **Deployment branches**: `develop`
- **Secrets específicos** (opcionales):
  - `JWT_SECRET_KEY_DEV` (si quieres uno diferente)

#### 2. Ambiente `staging`
- **Deployment branches**: `staging`
- **Required reviewers**: 1 persona
- **Secrets específicos**:
  - `JWT_SECRET_KEY_STAGING`

#### 3. Ambiente `prod`
- **Deployment branches**: `main`
- **Required reviewers**: 2 personas
- **Wait timer**: 5 minutos
- **Secrets específicos**:
  - `JWT_SECRET_KEY_PROD` (CRÍTICO: debe ser único y seguro)

---

## 🚀 Deploy Automático

### Workflow Automático por Branch

El deploy se ejecuta automáticamente cuando haces push a:

```bash
# Deploy a DEV
git push origin develop

# Deploy a STAGING
git push origin staging

# Deploy a PRODUCTION
git push origin main
```

### Proceso Automático

1. **Determinar ambiente** según el branch
2. **Ejecutar tests** (unit, integration, e2e)
3. **Deploy a Lambda** usando Serverless Framework
4. **Smoke tests** para verificar el deployment
5. **Notificaciones** (Slack opcional)

---

## 🎯 Deploy Manual

### Desde GitHub UI

1. Ve a `Actions` → `Deploy to AWS`
2. Click en `Run workflow`
3. Selecciona el ambiente (`dev`, `staging`, `prod`)
4. Click en `Run workflow`

### Desde Terminal Local

```bash
# Asegúrate de tener AWS configurado
aws configure

# Deploy a development
npm run deploy:dev
# o
make sls-deploy-dev

# Deploy a staging
npm run deploy:staging
# o
make sls-deploy-staging

# Deploy a production (requiere confirmación)
npm run deploy:prod
# o
make sls-deploy-prod
```

---

## ✅ Verificación

### 1. Verificar Deployment en GitHub

- Ve a `Actions` → Workflow ejecutado
- Revisa los logs de cada job
- Verifica el deployment summary al final

### 2. Verificar en AWS Console

```bash
# Listar funciones Lambda
aws lambda list-functions | grep kush-image-analyzer

# Ver información del stack
serverless info --stage dev

# Ver logs
aws logs tail /aws/lambda/kush-image-analyzer-dev-authRegister --follow
```

### 3. Probar Endpoints

```bash
# Obtener el endpoint
ENDPOINT=$(serverless info --stage dev | grep "endpoint:" | awk '{print $2}')

# Health check
curl $ENDPOINT/api/v1/health

# Respuesta esperada:
# {"status":"healthy","timestamp":"...","service":"kush-image-analyzer","version":"1.0.0"}

# Registrar usuario
curl -X POST $ENDPOINT/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User"
  }'

# Login
curl -X POST $ENDPOINT/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!"
  }'
```

### 4. Verificar Logs en CloudWatch

```bash
# Ver logs en tiempo real
aws logs tail /aws/lambda/kush-image-analyzer-dev-authRegister --follow --format short

# Buscar errores
aws logs filter-log-events \
  --log-group-name /aws/lambda/kush-image-analyzer-dev-authRegister \
  --filter-pattern "ERROR"
```

---

## 🔄 Rollback

### Rollback Automático

Si el deployment falla, el workflow intenta rollback automático en staging/prod.

### Rollback Manual

#### Opción 1: Re-deploy versión anterior

```bash
# Ver últimos commits
git log --oneline -5

# Hacer rollback a commit específico
git checkout <commit-hash>
git push origin main --force

# Esto triggerea un nuevo deployment
```

#### Opción 2: Rollback con Serverless

```bash
# Ver versiones anteriores
serverless deploy list --stage prod

# Rollback a versión anterior
serverless rollback --timestamp <timestamp> --stage prod
```

#### Opción 3: Rollback en AWS Console

1. Ve a `CloudFormation` → Stack `kush-image-analyzer-prod`
2. `Actions` → `Rollback stack`
3. Selecciona la versión anterior

---

## 🐛 Troubleshooting

### Error: "Credentials not configured"

```bash
# Verifica que los secrets estén configurados en GitHub
# Settings → Secrets → Actions

# Localmente, verifica AWS CLI
aws sts get-caller-identity
```

### Error: "Table already exists"

```bash
# Normal en re-deployments
# El script de Serverless maneja esto automáticamente
```

### Error: "Lambda timeout"

```bash
# Aumenta el timeout en serverless.yml
functions:
  authRegister:
    timeout: 60  # Aumentar de 30 a 60 segundos
```

### Error: "Memory exceeded"

```bash
# Aumenta la memoria en serverless.yml
functions:
  analyzeImage:
    memorySize: 2048  # Aumentar de 1024 a 2048 MB
```

### Tests fallan en CI/CD

```bash
# Verifica que las variables de entorno estén configuradas
# en el workflow: .github/workflows/deploy.yml

# Ejecuta tests localmente primero
make test
```

### Deployment exitoso pero API no responde

```bash
# Verifica los logs
serverless logs -f authRegister --stage dev --tail

# Verifica el health check
curl $ENDPOINT/api/v1/health

# Verifica API Gateway
aws apigateway get-rest-apis
```

---

## 📊 Monitoreo Post-Deployment

### CloudWatch Dashboards

Crea un dashboard para monitorear:
- Invocaciones por función
- Errores y throttling
- Duración promedio
- Concurrencia

```bash
# Ver métricas
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=kush-image-analyzer-dev-authRegister \
  --start-time 2025-01-18T00:00:00Z \
  --end-time 2025-01-18T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

### Alarmas Recomendadas

```bash
# Crear alarma de errores
aws cloudwatch put-metric-alarm \
  --alarm-name kush-api-errors-dev \
  --alarm-description "Alert on Lambda errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1
```

---

## 🎯 Mejores Prácticas

1. **Siempre testea en dev primero**
   ```bash
   git push origin develop  # Deploy a dev
   # Verifica que todo funcione
   git push origin main     # Deploy a prod
   ```

2. **Usa feature branches**
   ```bash
   git checkout -b feature/nueva-funcionalidad
   # Desarrolla y testea localmente
   git push origin feature/nueva-funcionalidad
   # Crea PR a develop
   ```

3. **Revisa los logs después de cada deploy**
   ```bash
   serverless logs -f authRegister --stage prod --tail
   ```

4. **Mantén separados los secrets por ambiente**
   - Dev: Secrets de prueba
   - Staging: Secrets similares a prod
   - Prod: Secrets únicos y seguros

5. **Configura notificaciones**
   - Slack para deployments
   - Email para errores críticos
   - PagerDuty para producción

---

## 📚 Recursos Adicionales

- [Serverless Framework Docs](https://www.serverless.com/framework/docs)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)

---

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs en GitHub Actions
2. Revisa los logs en CloudWatch
3. Verifica la documentación: [SERVERLESS_ARCHITECTURE.md](./SERVERLESS_ARCHITECTURE.md)
4. Contacta al equipo de DevOps

---

**Última actualización**: Enero 2025