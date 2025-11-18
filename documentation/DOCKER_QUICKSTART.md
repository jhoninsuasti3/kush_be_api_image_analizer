# Docker Quick Start Guide

Get the Kush Image Analyzer API running locally in under 5 minutes with Docker.

## Prerequisites

- Docker 20.10 or higher
- Docker Compose 2.0 or higher
- 2GB free RAM
- 1GB free disk space

Check your installation:
```bash
docker --version
docker-compose --version
```

---

## Quick Start (30 seconds)

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Build and start all services
docker-compose up --build

# 3. Wait for services to be ready (~30-60 seconds)
# You'll see: "Application startup complete"

# 4. Test the API
curl http://localhost:8000/api/v1/health
```

**That's it!** The API is now running at `http://localhost:8000`

---

## What Gets Started?

The `docker-compose up` command starts **3 services**:

| Service | Purpose | Port | Container Name |
|---------|---------|------|----------------|
| **dynamodb-local** | Local DynamoDB database | 8001 | kush-dynamodb-local |
| **dynamodb-init** | Creates tables automatically | - | kush-dynamodb-init |
| **api** | FastAPI application | 8000 | kush-api |

### Service Details

1. **dynamodb-local**:
   - Amazon's official DynamoDB Local image
   - Data persisted in Docker volume `dynamodb-data`
   - Accessible at `http://localhost:8001`

2. **dynamodb-init**:
   - One-time initialization container
   - Creates `kush-users-dev` table
   - Exits after successful table creation

3. **api**:
   - FastAPI application with hot reload enabled
   - Built from multi-stage Dockerfile (development stage)
   - Code changes auto-reload without restart

---

## Testing the API

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-18T12:00:00.000000",
  "service": "kush-image-analyzer",
  "version": "1.0.0"
}
```

### Register a User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!"
  }'
```

Expected response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Analyze Image (requires token)
```bash
TOKEN="your-access-token-here"

curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@path/to/image.jpg"
```

Note: Image analysis requires Google Cloud Vision credentials (see below).

---

## API Documentation

Once the API is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Interactive API documentation with request/response examples and testing capability.

---

## Google Cloud Vision Setup (Optional)

Image analysis requires Google Cloud Vision API credentials.

### Option 1: Using Service Account JSON (Recommended)

1. **Get credentials** from Google Cloud Console
2. **Save** the JSON file as `google-credentials.json` in project root
3. **Update** `.env`:
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=/app/google-credentials.json
   ```
4. **Update** `docker-compose.yml` to mount the file:
   ```yaml
   api:
     volumes:
       - ./google-credentials.json:/app/google-credentials.json:ro
   ```
5. **Restart** the API:
   ```bash
   docker-compose restart api
   ```

### Option 2: Skip for Now

The API will work without Google credentials:
- ✅ Authentication endpoints work
- ✅ Health checks work
- ❌ Image analysis will return error

This is useful for testing auth functionality only.

---

## Common Commands

### Start Services
```bash
# Start in foreground (see logs)
docker-compose up

# Start in background (detached)
docker-compose up -d

# Rebuild and start
docker-compose up --build
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f dynamodb-local
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart api
```

### Execute Commands in Container
```bash
# Open shell in API container
docker-compose exec api sh

# Check Python version
docker-compose exec api python --version

# Run tests
docker-compose exec api pytest tests/
```

---

## Development Workflow

### Code Changes with Hot Reload

1. **Edit code** in `app/` directory
2. **Save file**
3. **Watch logs** - API auto-reloads
4. **Test** - changes are live immediately

No need to restart Docker containers!

### Adding Dependencies

If you add a new dependency to `pyproject.toml`:

```bash
# Rebuild the image
docker-compose up --build
```

### Running Tests

```bash
# Inside container
docker-compose exec api pytest tests/

# With coverage
docker-compose exec api pytest tests/ --cov=app --cov-report=html

# Specific test file
docker-compose exec api pytest tests/unit/test_infrastructure/test_user_repository.py
```

---

## Troubleshooting

### Port Already in Use

**Error**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution**: Change the port in `docker-compose.yml`:
```yaml
api:
  ports:
    - "8080:8000"  # Access at http://localhost:8080
```

### DynamoDB Table Creation Failed

**Error**: `ResourceInUseException: Table already exists`

**Solution**: This is normal if restarting. The init script handles it gracefully.

To recreate tables:
```bash
# Stop and remove volumes
docker-compose down -v

# Start fresh
docker-compose up
```

### Module Not Found Error

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Rebuild the image:
```bash
docker-compose down
docker-compose up --build
```

### Connection Refused to DynamoDB

**Error**: `ConnectionRefusedError: [Errno 111] Connection refused`

**Solution**: Wait for DynamoDB health check to pass:
```bash
# Check service health
docker-compose ps

# View DynamoDB logs
docker-compose logs dynamodb-local
```

### API Not Starting

Check logs for details:
```bash
docker-compose logs api
```

Common issues:
- Missing `.env` file → Copy from `.env.example`
- Invalid environment variables → Check `.env` syntax
- Port conflict → Change port mapping

---

## Environment Variables

The `.env` file configures the application. Key variables for Docker:

```env
# Must be "development" for Docker
ENVIRONMENT=development
DEBUG=true

# DynamoDB connection (Docker network)
DYNAMODB_ENDPOINT_URL=http://dynamodb-local:8000
DYNAMODB_USERS_TABLE=kush-users-dev

# AWS credentials (dummy values for local)
AWS_ACCESS_KEY_ID=dummy
AWS_SECRET_ACCESS_KEY=dummy
AWS_REGION=us-east-1

# JWT secret (change in production!)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-min-32-chars

# File upload limits
MAX_FILE_SIZE_MB=5
ALLOWED_EXTENSIONS=jpg,jpeg,png,webp

# Optional: Google Cloud Vision
GOOGLE_APPLICATION_CREDENTIALS=
```

See `.env.example` for all available options with detailed comments.

---

## Architecture

```
┌─────────────────────────────────────────┐
│         Docker Network (kush-network)   │
│                                          │
│  ┌──────────────┐    ┌───────────────┐ │
│  │   API        │───▶│  DynamoDB     │ │
│  │  (FastAPI)   │    │  Local        │ │
│  │  Port: 8000  │    │  Port: 8001   │ │
│  └──────────────┘    └───────────────┘ │
│         ▲                     ▲          │
│         │                     │          │
│         │          ┌──────────────┐     │
│         │          │  DynamoDB    │     │
│         │          │  Init        │     │
│         │          │  (one-time)  │     │
│         │          └──────────────┘     │
└─────────────────────────────────────────┘
         │
         ▼
    Your Browser
  http://localhost:8000
```

### Multi-Stage Dockerfile

The Dockerfile has 4 stages:

1. **python-base**: Base Python 3.11 with Poetry
2. **python-builder**: Installs dependencies
3. **development**: Development image with hot reload (used by Docker Compose)
4. **production**: Optimized production image with 4 workers

Docker Compose uses the **development** stage via the `target` parameter.

---

## Data Persistence

### DynamoDB Data

By default, DynamoDB data persists in a Docker volume:

```bash
# List volumes
docker volume ls | grep dynamodb

# Remove volume (clears all data)
docker volume rm kush_be_api_image_analizer_dynamodb-data
```

To use in-memory DynamoDB (data lost on restart):

Edit `docker-compose.yml`:
```yaml
dynamodb-local:
  command: "-jar DynamoDBLocal.jar -sharedDb -inMemory"
  # Remove the volumes section
```

---

## Production Deployment

This Docker setup is for **development only**. For production:

### Option 1: AWS Lambda (Recommended)

Use the serverless architecture:
```bash
npm run deploy:prod
```

See `SERVERLESS_ARCHITECTURE.md` for details.

### Option 2: Docker Production Image

Build the production stage:
```bash
docker build --target production -t kush-api:prod .

docker run -d \
  -p 8000:8000 \
  --env-file .env.prod \
  --name kush-api-prod \
  kush-api:prod
```

Production stage differences:
- No hot reload
- 4 Uvicorn workers
- Smaller image size
- Non-root user
- Only necessary files included

---

## Next Steps

After getting the API running:

1. **Explore API**: Visit http://localhost:8000/docs
2. **Run Tests**: `docker-compose exec api pytest tests/`
3. **Add Google Credentials**: Enable image analysis
4. **Read Architecture**: See `SERVERLESS_ARCHITECTURE.md`
5. **Deploy to AWS**: See `README_SERVERLESS.md`

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [DynamoDB Local Documentation](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html)
- [Google Cloud Vision API](https://cloud.google.com/vision/docs)

---

## Getting Help

**Container won't start?**
```bash
docker-compose logs api
```

**Database issues?**
```bash
docker-compose logs dynamodb-local
docker-compose logs dynamodb-init
```

**Clean slate?**
```bash
docker-compose down -v
docker system prune -f
docker-compose up --build
```

**Still stuck?** Check the main README.md or open an issue.