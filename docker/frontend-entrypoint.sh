#!/bin/bash

# Frontend Docker container entrypoint with debugging support

set -e

echo "=== RazorFlow AI Frontend Container Starting ==="
echo "Timestamp: $(date)"
echo "Node Environment: ${NODE_ENV:-development}"
echo "API Base URL: ${VITE_API_BASE:-http://localhost:8000}"
echo "Debug Mode: ${VITE_DEBUG:-true}"

# Create log directory if it doesn't exist
mkdir -p /app/logs

# Log environment information
echo "=== Environment Information ===" > /app/logs/startup.log
env | grep -E "(NODE_|VITE_|NGINX_)" >> /app/logs/startup.log 2>/dev/null || true

# Check if Nginx config is valid
echo "=== Validating Nginx Configuration ==="
nginx -t

# Start logging nginx access and error logs to stdout/stderr for Docker
tail -f /var/log/nginx/access.log &
tail -f /var/log/nginx/error.log >&2 &

# Log startup completion
echo "Frontend container initialized successfully at $(date)" >> /app/logs/startup.log
echo "=== Frontend Ready ==="

# Execute the main command
exec "$@"
