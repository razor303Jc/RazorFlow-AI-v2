#!/bin/bash

# Container Debugging Script
# Provides comprehensive debugging information for Docker containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to check container status
check_container_status() {
    local container_name=$1
    
    log "Checking status of container: $container_name"
    
    if docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -q "$container_name"; then
        docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "$container_name"
        
        # Get container ID
        local container_id=$(docker ps -a -q --filter "name=$container_name")
        
        if [ -n "$container_id" ]; then
            log "Container ID: $container_id"
            
            # Check if container is running
            if docker ps -q --filter "name=$container_name" | grep -q "$container_id"; then
                success "Container $container_name is running"
                return 0
            else
                warning "Container $container_name exists but is not running"
                return 1
            fi
        fi
    else
        error "Container $container_name not found"
        return 1
    fi
}

# Function to get container logs
get_container_logs() {
    local container_name=$1
    local lines=${2:-50}
    
    log "Getting last $lines lines of logs for $container_name"
    
    if docker ps -a --filter "name=$container_name" --format "{{.Names}}" | grep -q "$container_name"; then
        echo "=== Recent Logs for $container_name ==="
        docker logs --tail $lines "$container_name" 2>&1
        echo "=== End of Logs ==="
    else
        error "Container $container_name not found"
    fi
}

# Function to inspect container configuration
inspect_container() {
    local container_name=$1
    
    log "Inspecting container configuration: $container_name"
    
    if docker ps -a --filter "name=$container_name" --format "{{.Names}}" | grep -q "$container_name"; then
        echo "=== Container Configuration ==="
        docker inspect "$container_name" | jq '.[] | {
            Name: .Name,
            State: .State,
            NetworkSettings: .NetworkSettings,
            Mounts: .Mounts,
            Config: {
                Env: .Config.Env,
                ExposedPorts: .Config.ExposedPorts,
                Cmd: .Config.Cmd
            }
        }'
        echo "=== End of Configuration ==="
    else
        error "Container $container_name not found"
    fi
}

# Function to check container health
check_container_health() {
    local container_name=$1
    
    log "Checking health of container: $container_name"
    
    if docker ps --filter "name=$container_name" --format "{{.Names}}" | grep -q "$container_name"; then
        local health_status=$(docker inspect "$container_name" | jq -r '.[0].State.Health.Status // "no-healthcheck"')
        
        case $health_status in
            "healthy")
                success "Container $container_name is healthy"
                ;;
            "unhealthy")
                error "Container $container_name is unhealthy"
                log "Recent health check logs:"
                docker inspect "$container_name" | jq -r '.[0].State.Health.Log[-3:] | .[] | "  " + .Start + ": " + .Output'
                ;;
            "starting")
                warning "Container $container_name health check is starting"
                ;;
            "no-healthcheck")
                warning "Container $container_name has no health check configured"
                ;;
            *)
                warning "Container $container_name has unknown health status: $health_status"
                ;;
        esac
    else
        error "Container $container_name is not running"
    fi
}

# Function to debug network connectivity
debug_network() {
    local container_name=$1
    
    log "Debugging network connectivity for: $container_name"
    
    if docker ps --filter "name=$container_name" --format "{{.Names}}" | grep -q "$container_name"; then
        echo "=== Network Information ==="
        
        # Get network information
        docker inspect "$container_name" | jq -r '.[0].NetworkSettings.Networks | to_entries[] | "Network: " + .key + ", IP: " + .value.IPAddress'
        
        # Test connectivity to other services
        log "Testing network connectivity from $container_name"
        
        case $container_name in
            "razorflow-backend"|"pixel-api"*)
                # Test database connectivity
                if docker ps --filter "name=postgres" --quiet | head -1; then
                    log "Testing database connectivity..."
                    docker exec "$container_name" nc -z postgres 5432 2>/dev/null && success "Database connection OK" || error "Database connection failed"
                fi
                
                # Test Redis connectivity
                if docker ps --filter "name=redis" --quiet | head -1; then
                    log "Testing Redis connectivity..."
                    docker exec "$container_name" nc -z redis 6379 2>/dev/null && success "Redis connection OK" || error "Redis connection failed"
                fi
                ;;
            "razorflow-postgres"|"pixel-postgres")
                log "Testing if database is accepting connections..."
                docker exec "$container_name" pg_isready 2>/dev/null && success "Database is ready" || error "Database not ready"
                ;;
            "razorflow-redis"|"pixel-redis")
                log "Testing Redis ping..."
                docker exec "$container_name" redis-cli ping 2>/dev/null && success "Redis is responding" || error "Redis not responding"
                ;;
        esac
        
        echo "=== End of Network Information ==="
    else
        error "Container $container_name is not running"
    fi
}

# Function to show resource usage
show_resource_usage() {
    local container_name=$1
    
    log "Showing resource usage for: $container_name"
    
    if docker ps --filter "name=$container_name" --format "{{.Names}}" | grep -q "$container_name"; then
        echo "=== Resource Usage ==="
        docker stats "$container_name" --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}"
        echo "=== End of Resource Usage ==="
    else
        error "Container $container_name is not running"
    fi
}

# Function to export debugging information
export_debug_info() {
    local container_name=$1
    local output_dir="./debug-output"
    
    log "Exporting debugging information for: $container_name"
    
    mkdir -p "$output_dir"
    
    # Export logs
    docker logs "$container_name" > "$output_dir/${container_name}-logs.txt" 2>&1
    
    # Export configuration
    docker inspect "$container_name" > "$output_dir/${container_name}-inspect.json"
    
    # Export stats
    docker stats "$container_name" --no-stream > "$output_dir/${container_name}-stats.txt"
    
    success "Debug information exported to $output_dir/"
}

# Main debugging function
debug_container() {
    local container_name=$1
    
    if [ -z "$container_name" ]; then
        error "Usage: debug_container <container_name>"
        return 1
    fi
    
    log "🔍 Starting comprehensive debugging for container: $container_name"
    log "================================================================"
    
    check_container_status "$container_name"
    echo
    
    check_container_health "$container_name"
    echo
    
    debug_network "$container_name"
    echo
    
    show_resource_usage "$container_name"
    echo
    
    get_container_logs "$container_name" 30
    echo
    
    # Ask if user wants to export debug info
    read -p "Export debugging information to files? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        export_debug_info "$container_name"
    fi
}

# If script is called directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    if [ $# -eq 0 ]; then
        echo "Usage: $0 <container_name>"
        echo "Available containers:"
        docker ps -a --format "table {{.Names}}\t{{.Status}}"
    else
        debug_container "$1"
    fi
fi
