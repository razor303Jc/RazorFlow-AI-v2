#!/bin/bash
# Simple test validation script

echo "🧪 Testing basic framework functionality..."

# Set up environment
export PYTHONPATH="$PWD/../:$PWD/../backend:$PYTHONPATH"

echo "✅ Environment variables set"
echo "PYTHONPATH: $PYTHONPATH"

# Test Python imports
echo "🔍 Testing Python imports..."
python3 -c "
try:
    import sys
    sys.path.insert(0, '../backend')
    import pytest
    import fastapi
    import httpx
    print('✅ All core imports successful')
    print(f'   - pytest: {pytest.__version__}')
    print(f'   - fastapi: {fastapi.__version__}')
    print(f'   - httpx: {httpx.__version__}')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

echo "🧪 Testing pytest discovery..."
python3 -m pytest --collect-only -q 2>/dev/null | head -5

echo "✅ Basic framework validation complete!"
