# Testing Documentation

This directory contains comprehensive tests for the Kush Image Analyzer API.

## Test Structure

```
tests/
├── conftest.py              # Global fixtures and test configuration
├── unit/                    # Unit tests (isolated component testing)
│   ├── test_core/          # Core layer tests (security, config, exceptions)
│   ├── test_domain/        # Domain layer tests (models, validation)
│   ├── test_infrastructure/ # Infrastructure tests (repos, validators, AI service)
│   └── test_application/   # Application service tests
├── integration/            # Integration tests (API endpoints)
│   ├── test_auth_endpoints.py
│   ├── test_analyze_endpoint.py
│   └── test_health_endpoints.py
└── e2e/                    # End-to-end tests (complete user flows)
    └── test_complete_user_flow.py
```

## Test Categories

### Unit Tests
- **Core Layer**: Security utilities, configuration, exception handling
- **Domain Layer**: Model validation, business rules
- **Infrastructure Layer**: Database repositories, file validators, AI service integration
- **Application Layer**: Service orchestration, business logic

### Integration Tests
- **Authentication Endpoints**: Registration, login, token validation
- **Image Analysis Endpoint**: File upload, validation, AI analysis
- **Health Endpoints**: Health checks, readiness checks

### End-to-End Tests
- **Complete User Flows**: Full user journeys from registration to image analysis
- **Multi-user Scenarios**: Concurrent user operations
- **Error Handling Flows**: Complete error scenarios

## Running Tests

### Quick Start

```bash
# Install dependencies
make install-all

# Run all tests
make test

# Run tests with coverage
make test-cov
```

### Specific Test Suites

```bash
# Run only unit tests
make test-unit

# Run only integration tests
make test-integration

# Run only E2E tests
make test-e2e
```

### Advanced Options

```bash
# Run tests in fast mode (fail fast)
make test-fast

# Re-run only failed tests
make test-failed

# Run tests with detailed summary
make test-summary

# Watch mode (runs tests on file changes)
make test-watch
```

### Using pytest Directly

```bash
# Run all tests
poetry run pytest tests/ -v

# Run specific test file
poetry run pytest tests/unit/test_infrastructure/test_user_repository.py -v

# Run specific test class
poetry run pytest tests/unit/test_infrastructure/test_user_repository.py::TestDynamoDBUserRepository -v

# Run specific test method
poetry run pytest tests/unit/test_infrastructure/test_user_repository.py::TestDynamoDBUserRepository::test_create_user_success -v

# Run tests matching a pattern
poetry run pytest tests/ -k "auth" -v

# Run with coverage for specific module
poetry run pytest tests/unit/ --cov=app/core --cov-report=term-missing
```

## Test Coverage

### Viewing Coverage Reports

```bash
# Generate HTML coverage report
make test-cov

# Open coverage report in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Coverage Targets

- **Minimum Coverage**: 70%
- **Target Coverage**: 80%+
- **Critical Paths**: 90%+

Current coverage by layer:
- Core Layer: ~95%
- Domain Layer: ~90%
- Infrastructure Layer: ~85%
- Application Layer: ~85%
- API Layer: ~80%

## Test Fixtures

### Available Fixtures

Global fixtures are defined in `conftest.py`:

**Environment & Configuration**
- `setup_test_environment`: Sets up test environment variables
- `test_settings`: Provides test Settings instance

**FastAPI Clients**
- `client`: Synchronous TestClient
- `async_client`: Async TestClient

**Database**
- `dynamodb_mock`: Mocked DynamoDB instance
- `users_table`: DynamoDB users table
- `reset_db`: Automatically cleans database before/after each test

**Authentication**
- `valid_token`: Valid JWT token
- `expired_token`: Expired JWT token
- `invalid_token`: Invalid JWT token
- `auth_headers`: Authorization headers with valid token

**Users**
- `user_create_data`: User registration data
- `valid_user`: Active user instance
- `inactive_user`: Inactive user instance
- `user_factory`: Factory for creating test users

**Files**
- `valid_image_file`: Valid JPEG image
- `large_image_file`: Image exceeding size limit
- `invalid_file_type`: Non-image file
- `corrupted_image_file`: Corrupted image

**AI Service**
- `mock_google_vision_client`: Mocked Google Vision client
- `mock_vision_response_multiple_labels`: Mock response with labels
- `image_analysis_result_factory`: Factory for analysis results

## Writing Tests

### Test Naming Conventions

```python
# Test classes
class TestUserRepository:
    """Test suite for UserRepository."""

# Test methods
def test_create_user_success(self):
    """Test successful user creation."""

def test_create_user_duplicate_email(self):
    """Test that creating duplicate user raises exception."""
```

### Test Structure (Arrange-Act-Assert)

```python
def test_login_success(self, auth_service, valid_user, mock_user_repository):
    """Test successful login."""
    # Arrange
    credentials = UserLogin(email=valid_user.email, password="password123")
    mock_user_repository.get_by_email.return_value = valid_user

    # Act
    token = auth_service.login(credentials)

    # Assert
    assert token is not None
    assert isinstance(token, str)
    mock_user_repository.get_by_email.assert_called_once()
```

### Mocking External Services

```python
from unittest.mock import patch, Mock

def test_analyze_image_success(self, service, test_image_bytes):
    """Test successful image analysis."""
    with patch('app.infrastructure.ai.google_vision_service.GoogleVisionService.analyze_image') as mock_analyze:
        mock_analyze.return_value = ImageAnalysisResult(tags=[...])

        result = service.analyze_image(test_image_bytes)

        assert len(result.tags) > 0
```

## Continuous Integration

Tests run automatically on GitHub Actions for:
- All pushes to `main`, `develop`, and `feature/*` branches
- All pull requests to `main` and `develop`

### CI Pipeline

1. **Lint**: Ruff linter, format check, MyPy type checking
2. **Unit Tests**: Fast, isolated component tests
3. **Integration Tests**: API endpoint tests with DynamoDB Local
4. **E2E Tests**: Complete user flow tests
5. **Coverage Report**: Combined coverage report uploaded to Codecov
6. **Security Scan**: Safety check for vulnerabilities

### Running CI Locally

```bash
# Run full CI pipeline locally
make ci

# Or step by step
make install-all
make lint
make test-cov
```

## Debugging Tests

### Using pytest Options

```bash
# Show print statements
poetry run pytest tests/ -v -s

# Stop on first failure
poetry run pytest tests/ -v -x

# Show local variables on failure
poetry run pytest tests/ -v -l

# Enter debugger on failure
poetry run pytest tests/ -v --pdb

# Run last failed tests first
poetry run pytest tests/ -v --ff
```

### Using VSCode

Add to `.vscode/settings.json`:

```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests",
    "-v"
  ]
}
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Mock External Services**: Always mock AWS, Google Vision, etc.
3. **Use Fixtures**: Reuse common setup via fixtures
4. **Descriptive Names**: Test names should describe what they test
5. **One Assertion Focus**: Each test should verify one behavior
6. **Clean Up**: Use fixtures with cleanup or `reset_db` fixture
7. **Fast Tests**: Keep unit tests fast (<0.1s each)
8. **Realistic Data**: Use Faker for realistic test data

## Troubleshooting

### Common Issues

**Issue**: Tests fail with "table not found"
```bash
# Solution: Ensure DynamoDB mock is working
# Check that users_table fixture is being used
```

**Issue**: Import errors
```bash
# Solution: Install test dependencies
make install-all
```

**Issue**: Token validation fails
```bash
# Solution: Check JWT_SECRET_KEY is set in test environment
# The conftest.py should set this automatically
```

**Issue**: Async tests fail
```bash
# Solution: Ensure pytest-asyncio is installed
# Check that asyncio_mode = "auto" is in pyproject.toml
```

## Contributing

When adding new features:

1. Write tests first (TDD approach recommended)
2. Ensure all tests pass: `make test`
3. Check coverage: `make test-cov`
4. Run linting: `make lint`
5. Run full CI locally: `make ci`

Target: All new code should have >80% test coverage.

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Moto (AWS Mocking)](https://docs.getmoto.org/)