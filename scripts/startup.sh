#!/bin/bash

# Enhanced Startup Script for RazorFlow AI Backend
# Provides comprehensive debugging and error handling

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Trap to handle shutdown gracefully
cleanup() {
    log "Received shutdown signal, cleaning up..."
    if [ ! -z "$APP_PID" ]; then
        log "Stopping application (PID: $APP_PID)"
        kill -TERM "$APP_PID" 2>/dev/null || true
        wait "$APP_PID" 2>/dev/null || true
    fi
    log "Cleanup completed"
    exit 0
}

trap cleanup SIGTERM SIGINT

# Environment validation
validate_environment() {
    log "Validating environment variables..."
    
    # Required variables
    local required_vars=("PORT")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        error "Missing required environment variables: ${missing_vars[*]}"
        return 1
    fi
    
    # Log important environment variables (sanitized)
    log "Environment configuration:"
    log "  PORT: $PORT"
    log "  DEBUG: ${DEBUG:-false}"
    log "  ENVIRONMENT: ${ENVIRONMENT:-development}"
    log "  LOG_LEVEL: ${LOG_LEVEL:-INFO}"
    
    if [ -n "$DATABASE_URL" ]; then
        # Extract and log database info (without credentials)
        DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
        DB_NAME=$(echo "$DATABASE_URL" | sed -n 's/.*\/\([^?]*\).*/\1/p')
        log "  Database: $DB_NAME@$DB_HOST"
    fi
    
    if [ -n "$REDIS_URL" ]; then
        REDIS_HOST=$(echo "$REDIS_URL" | sed -n 's/redis:\/\/\([^:]*\):.*/\1/p')
        log "  Redis: $REDIS_HOST"
    fi
    
    success "Environment validation passed"
}

# Wait for dependencies
wait_for_dependencies() {
    log "Waiting for dependencies to be ready..."
    
    # Wait for database
    if [ -n "$DATABASE_URL" ]; then
        DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
        DB_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        
        log "Waiting for database at $DB_HOST:$DB_PORT..."
        
        TIMEOUT=60
        ELAPSED=0
        
        while [ $ELAPSED -lt $TIMEOUT ]; do
            if nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; then
                success "Database is ready"
                break
            fi
            
            log "Database not ready, waiting... ($ELAPSED/$TIMEOUT seconds)"
            sleep 5
            ELAPSED=$((ELAPSED + 5))
        done
        
        if [ $ELAPSED -ge $TIMEOUT ]; then
            error "Timeout waiting for database"
            return 1
        fi
    fi
    
    # Wait for Redis
    if [ -n "$REDIS_URL" ]; then
        REDIS_HOST=$(echo "$REDIS_URL" | sed -n 's/redis:\/\/\([^:]*\):.*/\1/p')
        REDIS_PORT=$(echo "$REDIS_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        
        log "Waiting for Redis at $REDIS_HOST:$REDIS_PORT..."
        
        TIMEOUT=30
        ELAPSED=0
        
        while [ $ELAPSED -lt $TIMEOUT ]; do
            if nc -z "$REDIS_HOST" "$REDIS_PORT" 2>/dev/null; then
                success "Redis is ready"
                break
            fi
            
            log "Redis not ready, waiting... ($ELAPSED/$TIMEOUT seconds)"
            sleep 5
            ELAPSED=$((ELAPSED + 5))
        done
        
        if [ $ELAPSED -ge $TIMEOUT ]; then
            warning "Timeout waiting for Redis (non-critical)"
        fi
    fi
    
    success "Dependencies check completed"
}

# Pre-flight checks
preflight_checks() {
    log "Running pre-flight checks..."
    
    # Check if port is available
    if netstat -tlnp 2>/dev/null | grep -q ":$PORT "; then
        error "Port $PORT is already in use"
        return 1
    fi
    
    # Check disk space
    if command -v df >/dev/null 2>&1; then
        DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
        if [ "$DISK_USAGE" -gt 90 ]; then
            error "Disk usage is critical: ${DISK_USAGE}%"
            return 1
        elif [ "$DISK_USAGE" -gt 80 ]; then
            warning "Disk usage is high: ${DISK_USAGE}%"
        fi
    fi
    
    # Check memory
    if command -v free >/dev/null 2>&1; then
        MEMORY_USAGE=$(free | grep Mem: | awk '{printf "%.0f", $3/$2 * 100.0}')
        if [ "$MEMORY_USAGE" -gt 90 ]; then
            warning "Memory usage is high: ${MEMORY_USAGE}%"
        fi
    fi
    
    success "Pre-flight checks passed"
}

# Setup logging
setup_logging() {
    log "Setting up logging..."
    
    # Create log directories
    mkdir -p /app/logs /tmp/razorflow
    
    # Set up log rotation if logrotate is available
    if command -v logrotate >/dev/null 2>&1; then
        cat > /tmp/razorflow/logrotate.conf << EOF
/app/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 appuser appuser
}
EOF
    fi
    
    # Start application logs
    echo "=== RazorFlow AI Backend Started at $(date) ===" >> /app/logs/startup.log
    
    success "Logging setup completed"
}

# Start the application
start_application() {
    log "Starting RazorFlow AI Backend..."
    
    # Log startup information
    {
        echo "=== Startup Information ==="
        echo "Date: $(date)"
        echo "User: $(whoami)"
        echo "Working Directory: $(pwd)"
        echo "Python Version: $(python --version 2>&1)"
        echo "Pip Packages:"
        pip list 2>/dev/null | head -20
        echo "=========================="
    } >> /app/logs/startup.log
    
    # Determine uvicorn command arguments
    UVICORN_ARGS="main:app --host 0.0.0.0 --port $PORT"
    
    # Add development features if in debug mode
    if [ "${DEBUG:-false}" = "true" ]; then
        log "Debug mode enabled - adding development features"
        UVICORN_ARGS="$UVICORN_ARGS --reload --log-level debug"
    else
        log "Production mode - optimizing for performance"
        UVICORN_ARGS="$UVICORN_ARGS --workers 4 --log-level info"
    fi
    
    # Add access logging
    UVICORN_ARGS="$UVICORN_ARGS --access-log"
    
    log "Starting uvicorn with: $UVICORN_ARGS"
    
    # Start the application in background so we can monitor it
    python -m uvicorn $UVICORN_ARGS &
    APP_PID=$!
    
    log "Application started with PID: $APP_PID"
    
    # Wait a moment for startup
    sleep 5
    
    # Check if the process is still running
    if ! kill -0 "$APP_PID" 2>/dev/null; then
        error "Application failed to start"
        return 1
    fi
    
    success "Application started successfully"
    
    # Wait for the application process
    wait "$APP_PID"
}

# Main startup sequence
main() {
    log "🚀 Starting RazorFlow AI Backend with enhanced debugging"
    log "======================================================="
    
    # Run startup sequence
    validate_environment || exit 1
    setup_logging || exit 1
    wait_for_dependencies || exit 1
    preflight_checks || exit 1
    start_application || exit 1
}

# Run main function
main "$@"
