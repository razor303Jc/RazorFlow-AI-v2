#!/bin/bash

# Enhanced Health Check Script for RazorFlow AI Backend
# Provides detailed debugging information

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

# Check if running in container
if [ -f /.dockerenv ]; then
    log "Running health check inside Docker container"
    HEALTH_CHECK_URL="http://localhost:${PORT:-8000}/health"
else
    log "Running health check outside Docker container"
    HEALTH_CHECK_URL="http://localhost:${PORT:-8000}/health"
fi

# Function to check service connectivity
check_service() {
    local service_name=$1
    local service_url=$2
    local timeout=${3:-5}
    
    log "Checking $service_name connectivity..."
    
    if curl -f -s --max-time $timeout "$service_url" > /dev/null 2>&1; then
        success "$service_name is accessible"
        return 0
    else
        error "$service_name is not accessible at $service_url"
        return 1
    fi
}

# Function to check database connectivity
check_database() {
    log "Checking database connectivity..."
    
    if [ -n "$DATABASE_URL" ]; then
        # Extract components from DATABASE_URL
        DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
        DB_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        
        log "Testing database connection to $DB_HOST:$DB_PORT"
        
        if command -v pg_isready >/dev/null 2>&1; then
            if pg_isready -h "$DB_HOST" -p "$DB_PORT" -t 5; then
                success "Database is ready"
                return 0
            else
                error "Database is not ready"
                return 1
            fi
        else
            # Fallback to netcat
            if nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; then
                success "Database port is open"
                return 0
            else
                error "Cannot connect to database port"
                return 1
            fi
        fi
    else
        warning "DATABASE_URL not set, skipping database check"
        return 0
    fi
}

# Function to check Redis connectivity
check_redis() {
    log "Checking Redis connectivity..."
    
    if [ -n "$REDIS_URL" ]; then
        REDIS_HOST=$(echo "$REDIS_URL" | sed -n 's/redis:\/\/\([^:]*\):.*/\1/p')
        REDIS_PORT=$(echo "$REDIS_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        
        log "Testing Redis connection to $REDIS_HOST:$REDIS_PORT"
        
        if command -v redis-cli >/dev/null 2>&1; then
            if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping 2>/dev/null | grep -q PONG; then
                success "Redis is responding"
                return 0
            else
                error "Redis is not responding"
                return 1
            fi
        else
            # Fallback to netcat
            if nc -z "$REDIS_HOST" "$REDIS_PORT" 2>/dev/null; then
                success "Redis port is open"
                return 0
            else
                error "Cannot connect to Redis port"
                return 1
            fi
        fi
    else
        warning "REDIS_URL not set, skipping Redis check"
        return 0
    fi
}

# Function to collect system information
collect_system_info() {
    log "Collecting system information..."
    
    echo "=== System Information ===" >> /app/logs/health-check.log
    echo "Date: $(date)" >> /app/logs/health-check.log
    echo "Hostname: $(hostname)" >> /app/logs/health-check.log
    echo "Uptime: $(uptime)" >> /app/logs/health-check.log
    
    if command -v free >/dev/null 2>&1; then
        echo "Memory: $(free -h)" >> /app/logs/health-check.log
    fi
    
    if command -v df >/dev/null 2>&1; then
        echo "Disk: $(df -h /)" >> /app/logs/health-check.log
    fi
    
    echo "Environment Variables:" >> /app/logs/health-check.log
    env | grep -E "(PORT|DEBUG|DATABASE|REDIS|CHROMA)" >> /app/logs/health-check.log
    
    echo "=========================" >> /app/logs/health-check.log
}

# Main health check
main() {
    log "Starting comprehensive health check..."
    
    # Create logs directory if it doesn't exist
    mkdir -p /app/logs
    
    # Collect system information
    collect_system_info
    
    # Check external dependencies first
    DEPS_OK=true
    
    if ! check_database; then
        DEPS_OK=false
    fi
    
    if ! check_redis; then
        DEPS_OK=false
    fi
    
    # Check ChromaDB if configured
    if [ -n "$CHROMA_URL" ]; then
        if ! check_service "ChromaDB" "$CHROMA_URL/api/v1/heartbeat"; then
            warning "ChromaDB check failed, but not critical"
        fi
    fi
    
    # Check main application health endpoint
    log "Checking main application health..."
    
    # Wait a bit for the application to start if dependencies are OK
    if [ "$DEPS_OK" = true ]; then
        sleep 2
    fi
    
    # Multiple attempts for application health check
    ATTEMPTS=3
    APP_HEALTHY=false
    
    for i in $(seq 1 $ATTEMPTS); do
        log "Health check attempt $i/$ATTEMPTS"
        
        if curl -f -s --max-time 10 "$HEALTH_CHECK_URL" > /dev/null 2>&1; then
            success "Application health check passed"
            APP_HEALTHY=true
            break
        else
            error "Health check attempt $i failed"
            if [ $i -lt $ATTEMPTS ]; then
                log "Retrying in 5 seconds..."
                sleep 5
            fi
        fi
    done
    
    # Final result
    if [ "$APP_HEALTHY" = true ]; then
        success "🎉 Health check PASSED - Application is healthy"
        exit 0
    else
        error "❌ Health check FAILED - Application is not responding"
        
        # Additional debugging information
        log "Collecting additional debug information..."
        
        # Check if the process is running
        if command -v ps >/dev/null 2>&1; then
            log "Running processes:"
            ps aux | head -20
        fi
        
        # Check listening ports
        if command -v netstat >/dev/null 2>&1; then
            log "Listening ports:"
            netstat -tlnp 2>/dev/null | head -10
        elif command -v ss >/dev/null 2>&1; then
            log "Listening ports:"
            ss -tlnp | head -10
        fi
        
        # Check recent logs if available
        if [ -f "/app/logs/razorflow.log" ]; then
            log "Recent application logs:"
            tail -20 /app/logs/razorflow.log
        fi
        
        exit 1
    fi
}

# Run main function
main "$@"
