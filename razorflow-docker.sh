#!/bin/bash

# RazorFlow AI Docker Deployment Script with Health Monitoring
# This script sets up and monitors the complete Docker stack

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"
DOCKER_COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.yml"
HEALTH_CHECK_TIMEOUT=300  # 5 minutes
HEALTH_CHECK_INTERVAL=10  # 10 seconds

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    log "Checking Docker status..."
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running or accessible"
        log "Please start Docker and try again"
        exit 1
    fi
    log_success "Docker is running"
}

# Function to check if Docker Compose is available
check_docker_compose() {
    log "Checking Docker Compose..."
    if ! command -v docker-compose > /dev/null 2>&1 && ! docker compose version > /dev/null 2>&1; then
        log_error "Docker Compose is not available"
        exit 1
    fi
    log_success "Docker Compose is available"
}

# Function to setup environment
setup_environment() {
    log "Setting up environment..."
    
    # Create .env file if it doesn't exist
    if [[ ! -f "$ENV_FILE" ]]; then
        log "Creating .env file from template..."
        cp "${SCRIPT_DIR}/.env.example" "$ENV_FILE"
        log_success ".env file created"
    else
        log_success ".env file already exists"
    fi
    
    # Create necessary directories
    log "Creating log directories..."
    mkdir -p "${SCRIPT_DIR}/logs/"{postgres,redis,chromadb,backend,frontend,nginx}
    mkdir -p "${SCRIPT_DIR}/database"
    log_success "Directories created"
}

# Function to build images
build_images() {
    log "Building Docker images..."
    
    # Use docker-compose or docker compose based on availability
    if command -v docker-compose > /dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    $COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" build --no-cache
    log_success "Images built successfully"
}

# Function to start services
start_services() {
    log "Starting RazorFlow AI services..."
    
    # Use docker-compose or docker compose based on availability
    if command -v docker-compose > /dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    $COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" up -d
    log_success "Services started"
}

# Function to check service health
check_service_health() {
    local service_name=$1
    local health_endpoint=$2
    local max_attempts=$((HEALTH_CHECK_TIMEOUT / HEALTH_CHECK_INTERVAL))
    local attempt=1
    
    log "Checking health of $service_name..."
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "$health_endpoint" > /dev/null 2>&1; then
            log_success "$service_name is healthy"
            return 0
        fi
        
        log "Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep $HEALTH_CHECK_INTERVAL
        ((attempt++))
    done
    
    log_error "$service_name failed to become healthy within $HEALTH_CHECK_TIMEOUT seconds"
    return 1
}

# Function to perform comprehensive health checks
health_checks() {
    log "Performing health checks..."
    local failed_checks=0
    
    # Check PostgreSQL
    if ! check_service_health "PostgreSQL" "http://localhost:5434"; then
        ((failed_checks++))
    fi
    
    # Check Redis
    if ! docker exec razorflow-redis redis-cli ping > /dev/null 2>&1; then
        log_error "Redis health check failed"
        ((failed_checks++))
    else
        log_success "Redis is healthy"
    fi
    
    # Check ChromaDB
    if ! check_service_health "ChromaDB" "http://localhost:8001/api/v1/heartbeat"; then
        ((failed_checks++))
    fi
    
    # Check Backend
    if ! check_service_health "Backend" "http://localhost:8000/health"; then
        ((failed_checks++))
    fi
    
    # Check Frontend
    if ! check_service_health "Frontend" "http://localhost:3000/health"; then
        ((failed_checks++))
    fi
    
    if [[ $failed_checks -eq 0 ]]; then
        log_success "All services are healthy! 🎉"
        return 0
    else
        log_error "$failed_checks service(s) failed health checks"
        return 1
    fi
}

# Function to show service status
show_status() {
    log "Service Status:"
    echo "===================="
    
    # Use docker-compose or docker compose based on availability
    if command -v docker-compose > /dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    $COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" ps
    
    echo ""
    log "Service URLs:"
    echo "===================="
    echo "Frontend:  http://localhost:3000"
    echo "Backend:   http://localhost:8000"
    echo "Backend Docs: http://localhost:8000/docs"
    echo "ChromaDB:  http://localhost:8001"
    echo "PostgreSQL: localhost:5434"
    echo "Redis:     localhost:6379"
}

# Function to show logs
show_logs() {
    local service=$1
    
    # Use docker-compose or docker compose based on availability
    if command -v docker-compose > /dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    if [[ -n "$service" ]]; then
        log "Showing logs for $service..."
        $COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" logs -f "$service"
    else
        log "Showing logs for all services..."
        $COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" logs -f
    fi
}

# Function to stop services
stop_services() {
    log "Stopping RazorFlow AI services..."
    
    # Use docker-compose or docker compose based on availability
    if command -v docker-compose > /dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    $COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" down
    log_success "Services stopped"
}

# Function to cleanup
cleanup() {
    log "Cleaning up Docker resources..."
    
    # Use docker-compose or docker compose based on availability
    if command -v docker-compose > /dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    $COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" down -v --remove-orphans
    docker system prune -f
    log_success "Cleanup completed"
}

# Main execution
main() {
    case "${1:-start}" in
        "start")
            log "🚀 Starting RazorFlow AI Docker Stack"
            check_docker
            check_docker_compose
            setup_environment
            build_images
            start_services
            health_checks
            show_status
            ;;
        "stop")
            log "🛑 Stopping RazorFlow AI services"
            stop_services
            ;;
        "restart")
            log "🔄 Restarting RazorFlow AI services"
            stop_services
            sleep 5
            start_services
            health_checks
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "${2:-}"
            ;;
        "health")
            health_checks
            ;;
        "cleanup")
            cleanup
            ;;
        "rebuild")
            log "🔨 Rebuilding and restarting services"
            stop_services
            build_images
            start_services
            health_checks
            show_status
            ;;
        *)
            echo "RazorFlow AI Docker Management Script"
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  start    - Start all services (default)"
            echo "  stop     - Stop all services"
            echo "  restart  - Restart all services"
            echo "  status   - Show service status"
            echo "  logs     - Show logs for all services"
            echo "  logs <service> - Show logs for specific service"
            echo "  health   - Check service health"
            echo "  cleanup  - Stop services and cleanup Docker resources"
            echo "  rebuild  - Rebuild images and restart services"
            echo ""
            echo "Examples:"
            echo "  $0 start"
            echo "  $0 logs backend"
            echo "  $0 health"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
