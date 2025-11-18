# Testing

## Test Statistics
- **Test Coverage Target**: >80%
- **Test Categories**: Unit, Integration, E2E

## Test Structure

```
tests/
├── conftest.py                  # Global fixtures and configuration
├── unit/                        # 139 unit tests
│   ├── test_core/              # 27 tests (config, security, exceptions)
│   ├── test_domain/            # 27 tests (models, validation)
│   ├── test_infrastructure/    # 67 tests (repos, validators, AI service)
│   └── test_application/       # 18 tests (service orchestration)
├── integration/                # 48 integration tests
│   ├── test_auth_endpoints.py  # 24 tests
│   ├── test_analyze_endpoint.py # 19 tests
│   └── test_health_endpoints.py # 5 tests
└── e2e/                        # 14 end-to-end tests
    └── test_complete_user_flow.py
```

