# RazorFlow AI Test Framework Documentation

## Overview

This comprehensive test framework ensures the reliability, security, and performance of the RazorFlow AI business automation platform. The framework covers all aspects of testing from unit tests to end-to-end deployment validation.

## Architecture

```
tests/
├── conftest.py              # Global test configuration and fixtures
├── pytest.ini              # Pytest configuration
├── test-requirements.txt    # Test dependencies
├── run_tests.sh            # Main test runner script
├── backend/                # Backend API tests
│   ├── test_api.py         # API endpoint tests
│   └── test_security.py    # Security vulnerability tests
├── frontend/               # Frontend component tests
│   └── test_components.py  # React component and build tests
├── integration/            # Integration tests
│   └── test_integration.py # Frontend-backend integration
├── deployment/             # Deployment tests
│   └── test_production.py  # Production environment tests
├── e2e/                   # End-to-end tests
│   └── test_e2e.py        # Browser automation tests
└── reports/               # Test reports and coverage
```

## Test Categories

### 1. Unit Tests (`tests/backend/`)

- **API Endpoints**: Test all FastAPI endpoints individually
- **Business Logic**: Validate bot responses and data processing
- **Error Handling**: Test error scenarios and edge cases
- **Performance**: Measure response times and resource usage

### 2. Security Tests (`tests/backend/test_security.py`)

- **Input Validation**: SQL injection, XSS protection
- **Authentication**: Access control and session management
- **Data Protection**: Sensitive information exposure
- **CORS Configuration**: Cross-origin request validation

### 3. Frontend Tests (`tests/frontend/`)

- **Build Process**: NPM install and build validation
- **Component Rendering**: React component functionality
- **Responsive Design**: Multi-device compatibility
- **Asset Optimization**: Bundle size and performance

### 4. Integration Tests (`tests/integration/`)

- **API Communication**: Frontend-backend data flow
- **CORS Functionality**: Cross-origin requests
- **Data Consistency**: Multi-endpoint data validation
- **Error Propagation**: End-to-end error handling

### 5. End-to-End Tests (`tests/e2e/`)

- **User Workflows**: Complete user journey testing
- **Browser Compatibility**: Cross-browser functionality
- **Accessibility**: WCAG compliance testing
- **Performance**: Real-world usage scenarios

### 6. Deployment Tests (`tests/deployment/`)

- **Production Readiness**: Live environment validation
- **Configuration**: Environment-specific settings
- **SSL/Security**: HTTPS and certificate validation
- **Performance**: Production load characteristics

## Quick Start

### Prerequisites

```bash
# Python 3.11+
python --version

# Node.js 18+
node --version

# Git
git --version
```

### Installation

```bash
# Clone repository
git clone https://github.com/razor303jc/RazorFlow-AI-v2.git
cd RazorFlow-AI-v2

# Install test dependencies
cd tests
pip install -r test-requirements.txt

# Install Playwright for E2E tests
python -m playwright install chromium
```

### Running Tests

#### All Tests

```bash
./tests/run_tests.sh
```

#### Specific Test Categories

```bash
# Backend unit tests only
./tests/run_tests.sh -t unit -v

# Integration tests with coverage
./tests/run_tests.sh -t integration -c

# Deployment tests
./tests/run_tests.sh -t deployment -d

# E2E tests
./tests/run_tests.sh -t e2e
```

#### Manual Test Execution

```bash
# Backend tests
cd tests
python -m pytest backend/ -v

# Frontend tests
python -m pytest frontend/ -v

# Integration tests (requires running backend)
python -m pytest integration/ -v

# E2E tests (requires both frontend and backend)
python -m pytest e2e/ -v

# Deployment tests
python -m pytest deployment/ -v -m deployment
```

## Configuration

### Environment Variables

```bash
# Test API endpoint
export TEST_API_URL="http://localhost:8000"

# Test frontend URL
export TEST_FRONTEND_URL="http://localhost:5173"

# Test timeout (seconds)
export TEST_TIMEOUT="30"

# Coverage threshold
export COVERAGE_THRESHOLD="80"
```

### Pytest Configuration

The `pytest.ini` file configures:

- Test discovery patterns
- Coverage reporting
- HTML report generation
- Test markers and categorization
- Warning filters

### Test Markers

```python
@pytest.mark.unit           # Unit tests
@pytest.mark.integration    # Integration tests
@pytest.mark.e2e           # End-to-end tests
@pytest.mark.deployment    # Deployment tests
@pytest.mark.slow          # Slow-running tests
@pytest.mark.performance   # Performance tests
```

## CI/CD Integration

### GitHub Actions

The `.github/workflows/test.yml` provides:

- **Multi-environment testing**: Python 3.11/3.12, Node 18/20
- **Parallel execution**: Backend, frontend, integration tests
- **Artifact collection**: Coverage reports, test results
- **Security scanning**: Bandit, Safety, Semgrep
- **Performance monitoring**: Load testing on main branch

### Workflow Triggers

- **Push to main/develop**: Full test suite
- **Pull requests**: Targeted test execution
- **Daily schedule**: Comprehensive validation
- **Manual dispatch**: On-demand testing

## Test Data Management

### Fixtures (`conftest.py`)

- **Backend server**: Automatic startup/shutdown
- **Test data**: Sample data for all bot types
- **HTTP clients**: Async and sync clients
- **Performance tracking**: Response time monitoring

### Mock Data

```python
# Sample finance data
finance_data = {
    'revenue': 125000,
    'expenses': 75000,
    'profit': 50000,
    'growth': 15.5
}

# Sample chat messages
test_messages = [
    {"message": "What's my current status?"},
    {"message": "Show me the latest data"},
    {"message": "What recommendations do you have?"}
]
```

## Performance Testing

### Response Time Targets

- **Health checks**: < 1 second
- **API endpoints**: < 2 seconds
- **Chat responses**: < 5 seconds
- **Page load**: < 10 seconds

### Load Testing

```bash
# Concurrent API requests
python -m pytest -v -m performance

# Browser performance
python -m pytest e2e/ -v -m slow
```

## Security Testing

### Automated Scans

```bash
# Security vulnerability scan
bandit -r backend/

# Dependency vulnerability check
safety check

# Code security patterns
semgrep --config=auto backend/
```

### Manual Security Tests

- Input validation (SQL injection, XSS)
- Authentication bypass attempts
- Data exposure validation
- CORS configuration testing

## Troubleshooting

### Common Issues

#### Backend Server Won't Start

```bash
# Check port availability
lsof -i :8000

# Check dependencies
pip install -r backend/requirements.txt

# Check Python path
export PYTHONPATH="$PWD/backend:$PYTHONPATH"
```

#### Frontend Tests Fail

```bash
# Check Node version
node --version  # Should be 18+

# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check build process
npm run build
```

#### E2E Tests Timeout

```bash
# Install browser dependencies
python -m playwright install-deps

# Increase timeout
export TEST_TIMEOUT="60"

# Run headful for debugging
python -m pytest e2e/ --headed
```

#### Permission Errors

```bash
# Make scripts executable
chmod +x tests/run_tests.sh

# Fix Python path
export PYTHONPATH="$PWD:$PWD/backend:$PYTHONPATH"
```

### Debug Mode

```bash
# Verbose output
./tests/run_tests.sh -v

# Keep browser open
python -m pytest e2e/ --headed --slowmo 1000

# Detailed coverage
./tests/run_tests.sh -c -v
```

## Reports and Coverage

### Generated Reports

- **HTML Coverage**: `tests/reports/coverage/index.html`
- **Test Results**: `tests/reports/pytest_report.html`
- **Security Scan**: `tests/reports/bandit-report.json`
- **Performance**: `tests/reports/performance-report.html`

### Coverage Targets

- **Backend Code**: 80% minimum
- **Critical Paths**: 95% minimum
- **API Endpoints**: 100% coverage
- **Error Handlers**: 90% coverage

## Best Practices

### Writing Tests

1. **Descriptive Names**: Clear test method names
2. **Single Responsibility**: One assertion per test
3. **Independent Tests**: No test dependencies
4. **Proper Cleanup**: Use fixtures and teardown
5. **Error Testing**: Test failure scenarios

### Test Organization

1. **Logical Grouping**: Group related tests in classes
2. **Consistent Structure**: Follow naming conventions
3. **Documentation**: Docstrings for complex tests
4. **Markers**: Use pytest markers for categorization

### Performance Considerations

1. **Fast Feedback**: Quick unit tests first
2. **Parallel Execution**: Independent test design
3. **Resource Cleanup**: Proper fixture management
4. **Selective Running**: Use markers for targeted testing

## Contributing

### Adding New Tests

1. **Identify Category**: Unit, integration, e2e, deployment
2. **Create Test File**: Follow naming convention `test_*.py`
3. **Add Markers**: Use appropriate pytest markers
4. **Update Documentation**: Document new test scenarios
5. **Verify CI**: Ensure tests run in GitHub Actions

### Test Guidelines

1. **Follow PEP 8**: Python style guidelines
2. **Use Type Hints**: Improve code clarity
3. **Handle Exceptions**: Proper error handling
4. **Mock External Services**: Avoid external dependencies
5. **Validate Assumptions**: Test edge cases

## Monitoring and Maintenance

### Regular Tasks

- **Weekly**: Review test failures and flaky tests
- **Monthly**: Update dependencies and security scans
- **Quarterly**: Performance baseline updates
- **Annually**: Framework architecture review

### Metrics to Track

- **Test Coverage**: Maintain > 80%
- **Test Execution Time**: Keep under 10 minutes
- **Flaky Test Rate**: < 5% failure rate
- **Security Scan Results**: Zero high-severity issues

---

For additional support or questions about the test framework, please refer to the project documentation or create an issue in the GitHub repository.
