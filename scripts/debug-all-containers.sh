#!/bin/bash

# Comprehensive Container Debugging and Monitoring Script
# For RazorFlow AI and Pixel AI Creator

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

header() {
    echo -e "${PURPLE}=== $1 ===${NC}"
}

# Function to show all containers overview
show_containers_overview() {
    header "Docker Containers Overview"
    
    echo -e "${CYAN}All Containers:${NC}"
    docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
    
    echo -e "\n${CYAN}Running Containers:${NC}"
    docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
    
    echo -e "\n${CYAN}Docker Networks:${NC}"
    docker network ls
    
    echo -e "\n${CYAN}Docker Volumes:${NC}"
    docker volume ls
}

# Function to check specific service groups
check_razorflow_services() {
    header "RazorFlow AI Services Status"
    
    local services=("razorflow-postgres" "razorflow-redis" "razorflow-chromadb" "razorflow-backend" "razorflow-frontend")
    
    for service in "${services[@]}"; do
        if docker ps -a --filter "name=$service" --format "{{.Names}}" | grep -q "$service"; then
            local status=$(docker ps -a --filter "name=$service" --format "{{.Status}}")
            if docker ps --filter "name=$service" --format "{{.Names}}" | grep -q "$service"; then
                success "$service: $status"
            else
                error "$service: $status"
            fi
        else
            warning "$service: Not found"
        fi
    done
}

check_pixel_services() {
    header "Pixel AI Creator Services Status"
    
    local services=("pixel-postgres" "pixel-redis" "pixel-chromadb" "pixel-api")
    
    for service in "${services[@]}"; do
        if docker ps -a --filter "name=$service" --format "{{.Names}}" | grep -q "$service"; then
            local status=$(docker ps -a --filter "name=$service" --format "{{.Status}}")
            if docker ps --filter "name=$service" --format "{{.Names}}" | grep -q "$service"; then
                success "$service: $status"
            else
                error "$service: $status"
            fi
        else
            warning "$service: Not found"
        fi
    done
}

# Function to show recent logs for all services
show_all_logs() {
    header "Recent Logs from All Services"
    
    local containers=$(docker ps --format "{{.Names}}")
    
    for container in $containers; do
        echo -e "\n${CYAN}=== Logs for $container ===${NC}"
        docker logs --tail 10 "$container" 2>&1 | head -10
    done
}

# Function to test connectivity between services
test_connectivity() {
    header "Testing Service Connectivity"
    
    # Test if backend can reach database
    if docker ps --filter "name=razorflow-backend" --quiet; then
        log "Testing RazorFlow backend → database connectivity"
        if docker exec razorflow-backend nc -z razorflow-postgres 5432 2>/dev/null; then
            success "RazorFlow backend can reach database"
        else
            error "RazorFlow backend cannot reach database"
        fi
    fi
    
    # Test if pixel-api can reach its database
    if docker ps --filter "name=pixel-api" --quiet; then
        log "Testing Pixel API → database connectivity"
        if docker exec pixel-api nc -z pixel-postgres 5432 2>/dev/null; then
            success "Pixel API can reach database"
        else
            error "Pixel API cannot reach database"
        fi
    fi
    
    # Test external access to services
    log "Testing external access to services"
    
    # Test RazorFlow backend
    if curl -f -s --max-time 5 "http://localhost:8000/health" > /dev/null 2>&1; then
        success "RazorFlow backend accessible externally"
    else
        error "RazorFlow backend not accessible externally"
    fi
    
    # Test Pixel API (if it should be accessible)
    if curl -f -s --max-time 5 "http://localhost:8080/health" > /dev/null 2>&1; then
        success "Pixel API accessible externally"
    else
        warning "Pixel API not accessible externally (may be expected)"
    fi
}

# Function to show resource usage for all containers
show_resource_usage() {
    header "Resource Usage"
    
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# Function to diagnose failed containers
diagnose_failed_containers() {
    header "Diagnosing Failed Containers"
    
    local failed_containers=$(docker ps -a --filter "status=exited" --format "{{.Names}}")
    
    if [ -z "$failed_containers" ]; then
        success "No failed containers found"
        return
    fi
    
    for container in $failed_containers; do
        echo -e "\n${RED}=== Diagnosing failed container: $container ===${NC}"
        
        # Show exit code and status
        local exit_code=$(docker inspect "$container" --format='{{.State.ExitCode}}')
        local finished_at=$(docker inspect "$container" --format='{{.State.FinishedAt}}')
        
        error "Container $container exited with code $exit_code at $finished_at"
        
        # Show last logs
        echo -e "${CYAN}Last 20 lines of logs:${NC}"
        docker logs --tail 20 "$container" 2>&1
        
        # Show container configuration that might be relevant
        echo -e "\n${CYAN}Environment Variables:${NC}"
        docker inspect "$container" --format='{{range .Config.Env}}{{println .}}{{end}}' | head -10
        
        echo -e "\n${CYAN}Command:${NC}"
        docker inspect "$container" --format='{{.Config.Cmd}}'
        
        echo -e "${PURPLE}===========================================${NC}\n"
    done
}

# Function to create debugging report
create_debug_report() {
    local output_file="debug-report-$(date +%Y%m%d-%H%M%S).txt"
    
    header "Creating Comprehensive Debug Report"
    
    {
        echo "=== Docker Debugging Report ==="
        echo "Generated: $(date)"
        echo "Host: $(hostname)"
        echo
        
        echo "=== Docker Version ==="
        docker version
        echo
        
        echo "=== Docker Info ==="
        docker info
        echo
        
        echo "=== All Containers ==="
        docker ps -a
        echo
        
        echo "=== Running Containers ==="
        docker ps
        echo
        
        echo "=== Networks ==="
        docker network ls
        echo
        
        echo "=== Volumes ==="
        docker volume ls
        echo
        
        echo "=== Resource Usage ==="
        docker stats --no-stream
        echo
        
        echo "=== Container Logs ==="
        local containers=$(docker ps -a --format "{{.Names}}")
        for container in $containers; do
            echo "--- Logs for $container ---"
            docker logs --tail 50 "$container" 2>&1
            echo
        done
        
    } > "$output_file"
    
    success "Debug report created: $output_file"
}

# Function to fix common issues
fix_common_issues() {
    header "Attempting to Fix Common Issues"
    
    log "1. Cleaning up unused Docker resources..."
    docker system prune -f
    
    log "2. Restarting failed containers..."
    local failed_containers=$(docker ps -a --filter "status=exited" --format "{{.Names}}")
    
    for container in $failed_containers; do
        log "Attempting to restart $container..."
        docker start "$container" || warning "Failed to restart $container"
    done
    
    log "3. Checking disk space..."
    df -h /var/lib/docker 2>/dev/null || df -h /
    
    success "Common fixes attempted"
}

# Interactive menu
show_menu() {
    echo -e "\n${PURPLE}🔧 Docker Debugging Menu${NC}"
    echo "1. Show containers overview"
    echo "2. Check RazorFlow services"
    echo "3. Check Pixel AI services"
    echo "4. Show recent logs"
    echo "5. Test connectivity"
    echo "6. Show resource usage"
    echo "7. Diagnose failed containers"
    echo "8. Create debug report"
    echo "9. Fix common issues"
    echo "10. Debug specific container"
    echo "0. Exit"
    echo
}

# Main function
main() {
    log "🐳 Docker Debugging and Monitoring Tool"
    log "======================================="
    
    if [ $# -eq 0 ]; then
        # Interactive mode
        while true; do
            show_menu
            read -p "Select an option (0-10): " choice
            
            case $choice in
                1) show_containers_overview ;;
                2) check_razorflow_services ;;
                3) check_pixel_services ;;
                4) show_all_logs ;;
                5) test_connectivity ;;
                6) show_resource_usage ;;
                7) diagnose_failed_containers ;;
                8) create_debug_report ;;
                9) fix_common_issues ;;
                10) 
                    echo "Available containers:"
                    docker ps -a --format "{{.Names}}"
                    read -p "Enter container name: " container_name
                    if [ -n "$container_name" ]; then
                        ./scripts/debug/debug-container.sh "$container_name"
                    fi
                    ;;
                0) log "Goodbye!"; exit 0 ;;
                *) error "Invalid option" ;;
            esac
            
            echo
            read -p "Press Enter to continue..."
            clear
        done
    else
        # Non-interactive mode
        case $1 in
            "overview") show_containers_overview ;;
            "razorflow") check_razorflow_services ;;
            "pixel") check_pixel_services ;;
            "logs") show_all_logs ;;
            "connectivity") test_connectivity ;;
            "resources") show_resource_usage ;;
            "failed") diagnose_failed_containers ;;
            "report") create_debug_report ;;
            "fix") fix_common_issues ;;
            *) 
                echo "Usage: $0 [overview|razorflow|pixel|logs|connectivity|resources|failed|report|fix]"
                exit 1
                ;;
        esac
    fi
}

# Run main function
main "$@"
