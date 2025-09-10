#!/bin/bash

# Application debug script for RazorFlow AI Backend

echo "=== RazorFlow AI Application Debug ==="
echo "Time: $(date)"
echo ""

echo "=== Application Files ==="
echo "Main application file:"
ls -la /app/main.py 2>/dev/null || echo "main.py not found!"
echo ""

echo "Requirements file:"
ls -la /app/requirements.txt 2>/dev/null || echo "requirements.txt not found!"
echo ""

echo "=== Python Environment ==="
echo "Python executable: $(which python3)"
echo "Pip version: $(pip --version)"
echo ""

echo "=== Installed Packages ==="
pip list | head -20
echo "(showing first 20 packages)"
echo ""

echo "=== Application Dependencies Test ==="
echo "Testing imports..."

python3 -c "
import sys
print(f'Python version: {sys.version}')
print('Testing imports...')

try:
    import fastapi
    print('✓ FastAPI imported successfully')
except ImportError as e:
    print(f'✗ FastAPI import failed: {e}')

try:
    import uvicorn
    print('✓ Uvicorn imported successfully')
except ImportError as e:
    print(f'✗ Uvicorn import failed: {e}')

try:
    import psycopg2
    print('✓ psycopg2 imported successfully')
except ImportError as e:
    print(f'✗ psycopg2 import failed: {e}')

try:
    import redis
    print('✓ Redis imported successfully')
except ImportError as e:
    print(f'✗ Redis import failed: {e}')

# Test main.py syntax
try:
    import ast
    with open('/app/main.py', 'r') as f:
        content = f.read()
    ast.parse(content)
    print('✓ main.py syntax is valid')
except Exception as e:
    print(f'✗ main.py syntax error: {e}')
"

echo ""
echo "=== Database Connection Test ==="
if [ -n "${DATABASE_URL:-}" ]; then
    echo "Testing PostgreSQL connection..."
    python3 -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.close()
    print('✓ PostgreSQL connection successful')
except Exception as e:
    print(f'✗ PostgreSQL connection failed: {e}')
"
else
    echo "DATABASE_URL not set"
fi

echo ""
echo "=== Redis Connection Test ==="
if [ -n "${REDIS_URL:-}" ]; then
    echo "Testing Redis connection..."
    python3 -c "
import redis
import os
try:
    r = redis.from_url(os.environ['REDIS_URL'])
    r.ping()
    print('✓ Redis connection successful')
except Exception as e:
    print(f'✗ Redis connection failed: {e}')
"
else
    echo "REDIS_URL not set"
fi

echo ""
echo "=== Application Debug Complete ==="
