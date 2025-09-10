#!/bin/bash
# -*- coding: utf-8 -*-
#
# Test Framework Validation Script
# Validates the complete test framework setup for RazorFlow AI
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

print_success() {
    print_status $GREEN "✅ $1"
}

print_warning() {
    print_status $YELLOW "⚠️  $1"
}

print_error() {
    print_status $RED "❌ $1"
}

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TESTS_DIR="$SCRIPT_DIR"

print_header "RazorFlow AI Test Framework Validation"
echo "Project Root: $PROJECT_ROOT"
echo "Tests Directory: $TESTS_DIR"

# Change to tests directory
cd "$TESTS_DIR"

# Initialize counters
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

# Function to increment counters
pass_check() {
    print_success "$1"
    ((CHECKS_PASSED++))
}

fail_check() {
    print_error "$1"
    ((CHECKS_FAILED++))
}

warn_check() {
    print_warning "$1"
    ((CHECKS_WARNING++))
}

# Check 1: Required test files exist
print_header "Checking Test File Structure"

required_files=(
    "conftest.py"
    "pytest.ini"
    "test-requirements.txt"
    "run_tests.sh"
    "README.md"
    "backend/test_api.py"
    "backend/test_security.py"
    "frontend/test_components.py"
    "integration/test_integration.py"
    "deployment/test_production.py"
    "e2e/test_e2e.py"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        pass_check "Test file exists: $file"
    else
        fail_check "Missing test file: $file"
    fi
done

# Check 2: Test directories
print_header "Checking Test Directory Structure"

required_dirs=(
    "backend"
    "frontend"
    "integration"
    "deployment"
    "e2e"
    "reports"
)

for dir in "${required_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        pass_check "Test directory exists: $dir"
    else
        fail_check "Missing test directory: $dir"
    fi
done

# Check 3: Python syntax validation
print_header "Validating Python Syntax"

python_files=(
    "conftest.py"
    "backend/test_api.py"
    "backend/test_security.py"
    "frontend/test_components.py"
    "integration/test_integration.py"
    "deployment/test_production.py"
    "e2e/test_e2e.py"
)

for file in "${python_files[@]}"; do
    if [[ -f "$file" ]]; then
        if python -m py_compile "$file" 2>/dev/null; then
            pass_check "Valid Python syntax: $file"
        else
            fail_check "Invalid Python syntax: $file"
        fi
    else
        warn_check "Skipping syntax check (file not found): $file"
    fi
done

# Check 4: Dependencies availability
print_header "Checking Test Dependencies"

required_packages=(
    "pytest"
    "pytest-asyncio"
    "pytest-cov"
    "pytest-html"
    "requests"
    "selenium"
    "playwright"
    "fastapi"
    "httpx"
)

for package in "${required_packages[@]}"; do
    if python -c "import $package" 2>/dev/null; then
        pass_check "Package available: $package"
    else
        warn_check "Package not installed: $package (install with: pip install $package)"
    fi
done

# Check 5: Configuration validation
print_header "Validating Test Configuration"

# Check pytest.ini
if [[ -f "pytest.ini" ]]; then
    if grep -q "testpaths" pytest.ini; then
        pass_check "pytest.ini has testpaths configured"
    else
        warn_check "pytest.ini missing testpaths configuration"
    fi
    
    if grep -q "addopts" pytest.ini; then
        pass_check "pytest.ini has addopts configured"
    else
        warn_check "pytest.ini missing addopts configuration"
    fi
else
    fail_check "pytest.ini not found"
fi

# Check run_tests.sh permissions
if [[ -f "run_tests.sh" ]]; then
    if [[ -x "run_tests.sh" ]]; then
        pass_check "run_tests.sh is executable"
    else
        warn_check "run_tests.sh is not executable (run: chmod +x run_tests.sh)"
    fi
else
    fail_check "run_tests.sh not found"
fi

# Check 6: Project structure dependencies
print_header "Checking Project Dependencies"

# Check backend exists
if [[ -d "$PROJECT_ROOT/backend" ]]; then
    pass_check "Backend directory exists"
    
    if [[ -f "$PROJECT_ROOT/backend/main.py" ]]; then
        pass_check "Backend main.py exists"
    else
        fail_check "Backend main.py not found"
    fi
    
    if [[ -f "$PROJECT_ROOT/backend/requirements.txt" ]]; then
        pass_check "Backend requirements.txt exists"
    else
        warn_check "Backend requirements.txt not found"
    fi
else
    fail_check "Backend directory not found"
fi

# Check frontend exists
if [[ -d "$PROJECT_ROOT/frontend" ]]; then
    pass_check "Frontend directory exists"
    
    if [[ -f "$PROJECT_ROOT/frontend/package.json" ]]; then
        pass_check "Frontend package.json exists"
    else
        fail_check "Frontend package.json not found"
    fi
    
    if [[ -f "$PROJECT_ROOT/frontend/vite.config.js" ]]; then
        pass_check "Frontend vite.config.js exists"
    else
        warn_check "Frontend vite.config.js not found"
    fi
else
    fail_check "Frontend directory not found"
fi

# Check 7: CI/CD configuration
print_header "Checking CI/CD Configuration"

if [[ -f "$PROJECT_ROOT/.github/workflows/test.yml" ]]; then
    pass_check "GitHub Actions test workflow exists"
else
    fail_check "GitHub Actions test workflow not found"
fi

# Check 8: Environment variables
print_header "Checking Environment Configuration"

env_vars=(
    "PYTHONPATH"
)

for var in "${env_vars[@]}"; do
    if [[ -n "${!var}" ]]; then
        pass_check "Environment variable set: $var=${!var}"
    else
        warn_check "Environment variable not set: $var"
    fi
done

# Check 9: Test execution (dry run)
print_header "Test Execution Validation (Dry Run)"

if [[ -f "run_tests.sh" ]] && [[ -x "run_tests.sh" ]]; then
    if ./run_tests.sh --help >/dev/null 2>&1; then
        pass_check "Test runner script executes successfully"
    else
        warn_check "Test runner script has execution issues"
    fi
else
    fail_check "Cannot execute test runner script"
fi

# Test pytest discovery
if command -v pytest >/dev/null 2>&1; then
    test_count=$(pytest --collect-only -q 2>/dev/null | grep -c "test session starts" || echo "0")
    if [[ $test_count -gt 0 ]]; then
        pass_check "Pytest can discover test files"
    else
        # Try with explicit discovery
        discovered_tests=$(find . -name "test_*.py" | wc -l)
        if [[ $discovered_tests -gt 0 ]]; then
            warn_check "Pytest may have discovery issues ($discovered_tests test files found)"
        else
            fail_check "No test files discovered by pytest"
        fi
    fi
else
    fail_check "Pytest not available in PATH"
fi

# Check 10: Documentation
print_header "Checking Documentation"

if [[ -f "README.md" ]]; then
    if grep -q "RazorFlow AI Test Framework" README.md; then
        pass_check "Test documentation exists and is properly titled"
    else
        warn_check "Test documentation exists but may be incomplete"
    fi
else
    fail_check "Test documentation (README.md) not found"
fi

# Summary
print_header "Validation Summary"

echo -e "\n📊 Test Framework Validation Results:"
echo -e "   ✅ Checks Passed: ${GREEN}$CHECKS_PASSED${NC}"
echo -e "   ⚠️  Warnings: ${YELLOW}$CHECKS_WARNING${NC}"
echo -e "   ❌ Checks Failed: ${RED}$CHECKS_FAILED${NC}"

total_checks=$((CHECKS_PASSED + CHECKS_WARNING + CHECKS_FAILED))
success_rate=$((CHECKS_PASSED * 100 / total_checks))

echo -e "\n📈 Success Rate: ${success_rate}%"

if [[ $CHECKS_FAILED -eq 0 ]]; then
    if [[ $CHECKS_WARNING -eq 0 ]]; then
        print_status $GREEN "\n🎉 Test framework validation PASSED! All checks successful."
        echo -e "\n🚀 Your test framework is ready for use!"
        echo -e "\nNext steps:"
        echo -e "  1. Install test dependencies: pip install -r test-requirements.txt"
        echo -e "  2. Run the full test suite: ./run_tests.sh"
        echo -e "  3. Check the test reports in: tests/reports/"
        exit 0
    else
        print_status $YELLOW "\n✅ Test framework validation PASSED with warnings."
        echo -e "\n⚠️  Please review the warnings above and consider addressing them."
        echo -e "\n🚀 Your test framework is functional but could be improved."
        exit 0
    fi
else
    print_status $RED "\n❌ Test framework validation FAILED."
    echo -e "\n🔧 Please fix the failed checks above before proceeding."
    echo -e "\nCommon fixes:"
    echo -e "  - Install missing dependencies: pip install -r test-requirements.txt"
    echo -e "  - Make scripts executable: chmod +x run_tests.sh"
    echo -e "  - Set Python path: export PYTHONPATH=\"\$PWD:\$PWD/backend:\$PYTHONPATH\""
    echo -e "  - Create missing directories: mkdir -p tests/reports"
    exit 1
fi
